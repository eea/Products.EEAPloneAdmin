""" Admin
"""
from AccessControl import Unauthorized
from Acquisition import aq_base
from App.config import getConfiguration
from Products.ATContentTypes.config import MX_TIDY_OPTIONS
from Products.ATContentTypes.lib.validators import unwrapValueFromHTML
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from Products.Five.browser.resource import Resource as z3_Resource
from Products.ResourceRegistries.tools.BaseRegistry import \
        getCharsetFromContentType
from ZPublisher.Iterators import IStreamIterator
import codecs
import logging
import os
import re
import subprocess

#import urllib

logger = logging.getLogger('Products.EEAPloneAdmin')

try:
    from mx.Tidy import tidy
    has_tidy = True
except ImportError:
    has_tidy = False

if has_tidy:
    mx_tidy = tidy
else:
    mx_tidy = lambda x, **y:x

OBJNAME = re.compile('(.*)-([A-Za-z]{2})([.][A-Za-z]{3})*$')


class LinguaPlone(BrowserView):
    """ LinguaPlone
    """
    def getNameParts(self, nid):
        """ Get name parts
        """
        parts = OBJNAME.findall(nid)
        cid = lang = ending = ''
        if len(parts) == 1:
            cid, lang, ending = parts[0]
        return cid, lang, ending

    def fixTranslations(self):
        """ Fix translations
        """
        canonicals = {}
        context = self.context
        for obj in context.contentValues():
            oid = obj.getId()
            cid, lang, _ending = self.getNameParts(oid)
            lang = lang.lower()
            if lang == 'en':
                obj.setLanguage('')
                obj.setCanonical()
                obj.setLanguage('en')
                canonicals[ cid ] = obj

        for obj in context.contentValues():
            oid = obj.getId()
            cid, lang, _ending = self.getNameParts(oid)
            lang = lang.lower()
            canonical = canonicals.get(cid, None)
            if canonical and lang != 'en':
                obj.setLanguage('')
                obj.setLanguage(lang)
                obj.addTranslationReference(canonical)
        return [ { 'canonical' : k,
                   'translations' : v.getTranslationLanguages() }
                                    for k,v in canonicals.items() ]

class TidyContent(BrowserView):
    """ Tidy content
    """
    def tidyAll(self):
        """ Tidy all
        """
        fixed = {'ok' : [],
                 'err' : [] }
        context = self.context
        for obj in context.contentValues():
            if hasattr(obj, 'getRawText') and hasattr(obj, 'setText'):
                value = obj.getRawText()
                result = mx_tidy(value, **MX_TIDY_OPTIONS)
                _nerrors, _nwarnings, outputdata, _errordata = result

                try:
                    outputdata = unwrapValueFromHTML(outputdata)
                    if outputdata != '' and outputdata is not None:
                        obj.setText(outputdata)
                        fixed['ok'].append(obj.getId())
                except Exception:
                    fixed['err'].append(obj.absolute_url())
        return fixed


def localize(content, default_url, portal_url):
    """ Localize
    """
    if default_url == portal_url:
        return content
    return content.replace(unicode(portal_url), unicode(default_url))


def save_resources_on_disk(registry, request=None):
    """ Reads merged resources from registry and saves them on disk
    """
    if request == None:
        request = getattr(registry, "REQUEST", None)

    if request == None:
        return

    logger.info(
        u"Starting to save resources on disk for registry %s" % registry)

    portal_url_tool = getToolByName(registry, 'portal_url')
    portal_url      = portal_url_tool()
    portal          = portal_url_tool.getPortalObject()
    skins           = getToolByName(registry,
                                    'portal_skins').getSkinSelections()
    conf            = getConfiguration()

    if not hasattr(conf, 'environment'):
        return  #this happens during unit tests, we skip this procedure

    base            = conf.environment['saved_resources']
    script          = conf.environment.get('sync_resources')
    default_url     = conf.environment.get('portal_url', portal_url)

    for skin in skins:
        portal.changeSkin(skin) #temporarily changes current skin

        #toggle these two lines when we want to support multiple skins
        #dest = base   #only one skin
        dest = os.path.join(base, skin)

        if not os.path.exists(dest):
            logging.debug("%s does not exists. Creating it." % dest)
            os.makedirs(dest)

        if not getattr(registry, 'concatenatedresources', None):
            logging.warning("No concatenated resources in registry")
            continue

        for name in registry.concatenatedresources:
            try:
                content = getResourceContent(registry, name, registry)
            except KeyError:
                #this is for DTML base_properties problem
                logging.warning("Could not generate content "
                                "for %s in skin %s" % (name, skin))
                continue

            if isinstance(content, str):
                content = content.decode('utf-8', 'ignore')

            content = localize(content, default_url, portal_url)

            try:
                fpath = os.path.join(dest, name)
                parent = os.path.dirname(fpath)
                if not os.path.exists(parent):
                    logging.debug("%s does not exists. Creating it." % dest)
                    os.makedirs(parent)

                f = codecs.open(fpath, 'w', 'utf-8')
                f.write(content)
                f.close()
                logging.debug("Wrote %s on disk." % fpath)
            except IOError:
                logging.warning("Could not write %s on disk." % fpath)

    if script:
        res = subprocess.call([script, base])
        if res != 0:
            raise ValueError("Unsuccessful synchronisation of disk resources")

    logger.info(u"Finished saving resources on disk for registry %s" % registry)


def getResourceContent(registry, item, context, original=False):
    """Fetch resource content for delivery."""

    self = registry

    # Save the RESPONSE headers
    headers = self.REQUEST.RESPONSE.headers.copy()

    ids = self.concatenatedresources.get(item, None)
    resources = self.getResourcesDict()
    if ids is not None:
        ids = ids[:]
    output = u""
    if len(ids) > 1:
        output = output + self.merged_output_prefix

    portal = getToolByName(context, 'portal_url').getPortalObject()

    if context == self and portal is not None:
        context = portal

    default_charset = 'utf-8'

    for res_id in ids:
        try:
            if portal is not None:
                obj = context.restrictedTraverse(res_id)
            else:
                #Can't do anything other than attempt a getattr
                obj = getattr(context, res_id)
        except (AttributeError, KeyError):
            output += u"\n/* ERROR -- could not find '%s'*/\n" % res_id
            content = u''
            obj = None
        except Unauthorized:
            #If we're just returning a single resource, raise an Unauthorized,
            #otherwise we're merging resources in which case just log an error
            if len(ids) > 1:
                #Object probably isn't published yet
                output += (
                u"\n/* ERROR -- access to '%s' not authorized */\n" % res_id)
                content = u''
                obj = None
            else:
                raise

        if obj is not None:
            if isinstance(obj, z3_Resource):
                content = get_resource_content(obj, self, default_charset)
            elif hasattr(aq_base(obj),'meta_type') and  obj.meta_type in \
                ['DTML Method', 'Filesystem DTML Method']:
                content = obj(client=self.aq_parent, REQUEST=self.REQUEST,
                              RESPONSE=self.REQUEST.RESPONSE)
                contenttype = self.REQUEST.RESPONSE.headers.get('content-type',
                        '')
                contenttype = getCharsetFromContentType(contenttype,
                        default_charset)
                content = unicode(content, contenttype)
            elif hasattr(aq_base(obj),'meta_type') and \
                    obj.meta_type == 'Filesystem File':
                obj._updateFromFS()
                content = obj._readFile(0)
                contenttype = getCharsetFromContentType(obj.content_type,
                        default_charset)
                content = unicode(content, contenttype)
            elif hasattr(aq_base(obj),'meta_type') and obj.meta_type in \
                    ('ATFile', 'ATBlob'):
                f = obj.getFile()
                contenttype = getCharsetFromContentType(f.getContentType(),
                        default_charset)
                content = unicode(str(f), contenttype)
            # We should add more explicit type-matching checks
            elif hasattr(aq_base(obj), 'index_html') and \
                    callable(obj.index_html):
                #self._removeCachingHeaders()
                content = obj.index_html(self.REQUEST,
                                         self.REQUEST.RESPONSE)
                if not isinstance(content, unicode):
                    content = unicode(content, default_charset)
            elif callable(obj):
                try:
                    content = obj(self.REQUEST, self.REQUEST.RESPONSE)
                except TypeError:
                    # Could be a view or browser resource
                    content = obj()
                except AttributeError, err:
                    logger.exception(err)
                    content = u''

                if IStreamIterator.providedBy(content):
                    content = content.read()

                if content and not isinstance(content, unicode):
                    content = unicode(content, default_charset)
            else:
                content = str(obj)
                content = unicode(content, default_charset)

        # Add start/end notes to the resource for better
        # understanding and debugging
        if content:
            output += u'\n/* - %s - */\n' % (res_id,)
            if original:
                output += content
            else:
                output += self.finalizeContent(resources[res_id], content)
            output += u'\n'

    # File objects and other might manipulate the headers,
    # something we don't want. we set the saved headers back
    self.REQUEST.RESPONSE.headers = headers
    return output


def get_resource_content(obj, registry, default_charset):
    """ Get resource content
    """
    self = registry
    try:
        method = obj.__browser_default__(self.REQUEST)[1][0]
    except AttributeError: # zope.app.publisher.browser.fileresource
        try:
            method = obj.browserDefault(self.REQUEST)[1][0]
        except (AttributeError, IndexError):
            try:
                method = obj.browserDefault(self.REQUEST)[0].__name__
            except AttributeError:
                method = 'GET'
    method = method in ('HEAD','POST') and 'GET' or method
    content = getattr(obj, method)()

    if not isinstance(content, unicode):
        contenttype = self.REQUEST.RESPONSE.headers.get('content-type', '')
        contenttype = getCharsetFromContentType(contenttype, default_charset)
        content = unicode(content, contenttype)

    return content


class SaveResourcesOnDisk(BrowserView):
    """ Base class to save resources on disk
    """
    tool = None

    def __call__(self):
        save_resources_on_disk(self.tool, self.request)
        return "Resources saved"

class RegenerateJS(SaveResourcesOnDisk):
    """ Call this to save on disk JS resources
    """
    @property
    def tool(self):
        """ Tool
        """
        return getToolByName(self.context, "portal_javascripts")

class RegenerateCSS(SaveResourcesOnDisk):
    """ Call this to save on disk CSS resources
    """
    @property
    def tool(self):
        """ Tool
        """
        return getToolByName(self.context, "portal_css")

class RegenerateKSS(SaveResourcesOnDisk):
    """ Call this to save on disk KSS resources
    """
    @property
    def tool(self):
        """ Tool
        """
        return getToolByName(self.context, "portal_kss")


class GoPDB(BrowserView):
    """pdb view 
    """

    def __call__(self):
        #mtool = getToolByName(self.context, 'portal_membership')
        #has = mtool.checkPermission("Manage portal", self.context)
        #if has:
        import pdb
        pdb.set_trace()

        return "Ok"
