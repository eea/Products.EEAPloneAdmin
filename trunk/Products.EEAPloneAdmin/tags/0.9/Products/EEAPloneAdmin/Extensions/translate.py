from Products.CMFPlone import PloneMessageFactory
from eea.translations import _ as eeaTranslationFactory
from zope.i18n import translate 

def translateHelper(domain, msgid, language):
    if domain == 'plone':
        return translate(PloneMessageFactory(msgid), target_language=language).encode('utf8')
    elif domain == 'eea.translations':
        return translate(eeaTranslationFactory(msgid), target_language=language).encode('utf8')

    return msgid
