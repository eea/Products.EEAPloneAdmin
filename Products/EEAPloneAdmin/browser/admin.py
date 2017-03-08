""" Admin
"""
import logging
import subprocess
from pprint import pprint

import codecs
import os
import re

from App.config import getConfiguration
from Products.ATContentTypes.config import MX_TIDY_OPTIONS
from Products.ATContentTypes.lib.validators import unwrapValueFromHTML
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from zExceptions import Unauthorized
try:
    from mx.Tidy import tidy
    has_tidy = True
except ImportError:
    has_tidy = False

logger = logging.getLogger('Products.EEAPloneAdmin')


if has_tidy:
    mx_tidy = tidy
else:
    mx_tidy = lambda x, **y: x

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
                canonicals[cid] = obj

        for obj in context.contentValues():
            oid = obj.getId()
            cid, lang, _ending = self.getNameParts(oid)
            lang = lang.lower()
            canonical = canonicals.get(cid, None)
            if canonical and lang != 'en':
                obj.setLanguage('')
                obj.setLanguage(lang)
                obj.addTranslationReference(canonical)
        return [{'canonical' : k,
                 'translations' : v.getTranslationLanguages()}
                                for k, v in canonicals.items()]

class TidyContent(BrowserView):
    """ Tidy content
    """
    def tidyAll(self):
        """ Tidy all
        """
        fixed = {'ok' : [],
                 'err' : []}
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
    if request is None:
        request = getattr(registry, "REQUEST", None)

    if request is None:
        return

    logger.info(
        u"Starting to save resources on disk for registry %s", registry)

    portal_url_tool = getToolByName(registry, 'portal_url')
    portal_url = portal_url_tool()
    #portal          = portal_url_tool.getPortalObject()
    skins = getToolByName(registry, 'portal_skins').getSkinSelections()
    conf = getConfiguration()

    if not hasattr(conf, 'environment'):
        return  #this happens during unit tests, we skip this procedure

    base = conf.environment.get('saved_resources',
                                os.environ.get('saved_resources'))
    script = conf.environment.get('sync_resources')
    default_url = conf.environment.get('portal_url', portal_url)


    for skin in skins:
        if skin not in ['EEADesign2006', 'EEADesignCMS']:
            continue
        #portal.changeSkin(skin) #temporarily changes current skin

        dest = os.path.join(base, skin)

        if not os.path.exists(dest):
            logger.debug("%s does not exists. Creating it.", dest)
            os.makedirs(dest)

        if not getattr(registry, 'concatenatedResourcesByTheme', None):
            logger.warning("No concatenated resources in registry")
            continue

        resources = registry.concatenatedResourcesByTheme[skin]

        for name in resources:
            try:
                content = registry.getResourceContent(name,
                                            context=registry, theme=skin)
            except TypeError:
                continue    #old merged resource
            except (KeyError, AttributeError, AssertionError), e:
                if not str(e).strip():   #on empty error, content is saved
                    continue
                #this is for DTML base_properties problem
                logger.warning("Could not generate content for %s in skin %s "
                               "because: %s", name, skin, e)
                continue

            if isinstance(content, str):
                content = content.decode('utf-8', 'ignore')

            content = localize(content, default_url, portal_url)

            try:
                fpath = os.path.join(dest, name)
                parent = os.path.dirname(fpath)
                if not os.path.exists(parent):
                    logger.debug("%s does not exists. Creating it.", dest)
                    os.makedirs(parent)

                f = codecs.open(fpath, 'w', 'utf-8')
                f.write(content)
                f.close()
                # logger.info("Wrote %s on disk.", fpath)
            except IOError:
                logger.warning("Could not write %s on disk.", fpath)
        logger.info(u"Finished saving %s resources on disk for registry %s",
                    len(resources), registry)

    if script:
        res = subprocess.call([script, base])
        if res != 0:
            raise ValueError("Unsuccessful synchronisation of disk resources")

    logger.info(u"Finished saving resources on disk for registry %s", registry)

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

        #this code is helpful in debugging inheritance trees
        #pyflakes complains that it's unused, so we disable it here
        #enable if you need it
#       def classtree(cls, indent):
#           """ method used in conjunction with instantree to display class
#               tree
#           """
#           print '.'*indent, cls.__name__        # print class name here
#           for supercls in cls.__bases__:        # recur to all superclasses
#               classtree(supercls, indent+3)     # may visit super > once

#       def instancetree(inst):
#           """ Helper method to recursively print all superclasses
#           """
#           print 'Tree of', inst                 # show instance
#           classtree(inst.__class__, 3)          # climb to its class

        import pdb
        pdb.set_trace()

        return "Ok"

class FindBrokenObjects(BrowserView):
    """ View for finding objects that are deleted but still cataloged
        use /find_broken_objects?type=Folder if you want to search for specific
        portal types
    """

    def __call__(self):
        catalog = self.context.portal_catalog

        res = []

        request = self.context.REQUEST
        param = request.get('type')
        query = {'Language': "all"}
        if param:
            query.update({"portal_type": param})
        search = catalog.searchResults(**query)

        for b in search:
            try:
                b.getObject()
            except Unauthorized:
                logger.info("Item %s raised Unauthorized", b.getURL())
            except KeyError:
                res.append(b.getURL())

        logger.warning("Broken Objects %s", pprint(res))
        return "%d are broken \n %s", (len(res), res)
