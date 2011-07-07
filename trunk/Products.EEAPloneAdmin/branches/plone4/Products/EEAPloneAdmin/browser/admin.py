from App.config import getConfiguration
from Products.ATContentTypes.config import MX_TIDY_OPTIONS
from Products.ATContentTypes.lib.validators import unwrapValueFromHTML
from Products.CMFCore.FSDTMLMethod import FSDTMLMethod
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
import logging
import os
import re
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
    mx_tidy = lambda x,**y:x

OBJNAME=  re.compile('(.*)-([A-Za-z]{2})([.][A-Za-z]{3})*$')


class LinguaPlone(BrowserView):
    """ 
    """

    def getNameParts(self, nid):
        parts = OBJNAME.findall(nid)
        cid = lang = ending = ''            
        if len(parts) == 1:
            cid, lang, ending = parts[0]
        return cid, lang, ending
    
    def fixTranslations(self):
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

    def tidyAll(self):
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


def save_resources_on_disk(registry, request=None):
    """Reads merged resources from registry and saves them on disk"""

    if request == None:
        request = registry.REQUEST

    portal = getToolByName(registry, 'portal_url').getPortalObject()
    skins = getToolByName(registry, 'portal_skins').getSkinSelections()
    conf = getConfiguration()
    base = conf.environment['saved_resources']
    
    #remove this line when we want to support multiple skins
    skins = [skins[0]]

    for skin in skins:
        portal.changeSkin(skin) #temporarily changes current skin

        #toggle these two lines when we want to support multiple skins
        dest = base
        #dest = os.path.join(base, urllib.quote(skin))

        if not os.path.exists(dest):
            logging.debug("%s does not exists. Creating it." % dest)
            os.makedirs(dest)

        for name in registry.concatenatedresources:
            try:
                content = registry.getInlineResource(name, portal)
            except Exception:
                try:
                    f = getattr(portal, name)
                    if isinstance(f, FSDTMLMethod):
                        content = f.__call__(client=portal, request=request)
                    else:   #we try to get the content somehow
                        content = f()
                except Exception:
                    logger.warning("Could not get content for resource %s "
                                   "in skin %s" % (name, skin))
                    continue

            try:
                fpath = os.path.join(dest, name)
                f = open(fpath, "w+")
                cont = content.encode('utf-8')
                f.write(cont)
                f.close()
                logging.debug("Wrote %s on disk." % fpath)
            except IOError:
                logging.warning("Could not write %s on disk." % fpath)


class SaveResourcesOnDisk(BrowserView):
    """Base class to save resources on disk
    """
    tool = None

    def __call__(self):
        save_resources_on_disk(self.tool, self.request)
        return "Resources saved"


class RegenerateJS(SaveResourcesOnDisk):
    """Call this to save on disk JS resources
    """

    @property
    def tool(self):
        return getToolByName(self.context, "portal_javascripts")


class RegenerateCSS(SaveResourcesOnDisk):
    """Call this to save on disk CSS resources
    """

    @property
    def tool(self):
        return getToolByName(self.context, "portal_css")
