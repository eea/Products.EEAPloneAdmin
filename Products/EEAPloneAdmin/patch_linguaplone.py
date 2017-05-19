""" Lingua Plone
"""
from archetypes.schemaextender import extender

from Products.CMFCore.utils import getToolByName
from Products.LinguaPlone.browser.defaultpage import DefaultPage


def clearSchemaCache(context):
    """ Clear
    """
    if hasattr(context.REQUEST, extender.CACHE_KEY):
        delattr(context.REQUEST, extender.CACHE_KEY)


def _patched_getFieldsToCopy(self, *args, **kwargs):
    """ Fields to copy
    """
    clearSchemaCache(self.context)
    return self._old_getFieldsToCopy(*args, **kwargs)


def _patched_getDefaultPage(self):
    """ Get the translation of the folder default page in current language
    """
    default_page = super(DefaultPage, self).getDefaultPage()
    if not default_page:
        return default_page

    page = self.context.unrestrictedTraverse([default_page])
    languageTool = getToolByName(self.context, 'portal_languages')
    current = languageTool.getPreferredLanguage()
    if page.hasTranslation(current):
        return page.getTranslation(current).getId()
    return default_page
