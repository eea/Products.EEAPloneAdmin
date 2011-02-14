from Products.Five import BrowserView
from Products.ATContentTypes.config import MX_TIDY_OPTIONS
from Products.ATContentTypes.lib.validators import unwrapValueFromHTML
try:
    from mx.Tidy import tidy as mx_tidy
except:
    mx_tidy = None
    
import re

OBJNAME=  re.compile('(.*)-([A-Za-z]{2})([.][A-Za-z]{3})*$')

class LinguaPlone(BrowserView):
    """ 
    """

    def getNameParts(self, id):
        parts = OBJNAME.findall(id)
        cid = lang = ending = ''            
        if len(parts) == 1:
            cid, lang, ending = parts[0]
        return cid, lang, ending
    
    def fixTranslations(self):
        canonicals = {}
        context = self.context
        for obj in context.contentValues():
            id = obj.getId()
            cid, lang, ending = self.getNameParts(id)
            lang = lang.lower()
            if lang == 'en':
                obj.setLanguage('')
                obj.setCanonical()
                obj.setLanguage('en')
                canonicals[ cid ] = obj

        for obj in context.contentValues():
            id = obj.getId()
            cid, lang, ending = self.getNameParts(id)
            lang = lang.lower()            
            canonical = canonicals.get(cid, None)
            if canonical and lang != 'en':
                obj.setLanguage('')
                obj.setLanguage(lang)
                obj.addTranslationReference(canonical)
        return [ { 'canonical' : k,
                   'translations' : v.getTranslationLanguages() } for k,v in canonicals.items() ]
            

class TidyContent(BrowserView):

    def tidyAll(self):
        fixed = {'ok' : [],
                 'err' : [] }
        context = self.context
        for obj in context.contentValues():
            if hasattr(obj, 'getRawText') and hasattr(obj, 'setText'):
                value = obj.getRawText()
                result = mx_tidy(value, **MX_TIDY_OPTIONS)
                nerrors, nwarnings, outputdata, errordata = result

                try:
                    outputdata = unwrapValueFromHTML(outputdata)
                    if outputdata != '' and outputdata is not None:
                        obj.setText(outputdata)
                        fixed['ok'].append(obj.getId())
                except:
                    fixed['err'].append(obj.absolute_url())
        return fixed
