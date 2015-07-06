""" Themecentre extenal methods
"""
from Products.CMFCore.utils import getToolByName
import transaction

def fix_themecentre_intro_pages(self):
    """ reindex intro pages and make sure they aren't default pages anymore
    """
    query = {'object_provides' :
            'eea.themecentre.interfaces.IThemeCentre',
                'path' :
            {'query': '/www/SITE/themes', 'depth': 1}}
    res = getToolByName(self, 'portal_catalog').searchResults(query)
    res = [obj.getObject() for obj in res]
    for obj in res:
        translations = obj.getTranslations()
        values = translations.values()
        for trans in values:
            item = trans[0]
            if hasattr(item, 'intro'):
                intro = item.intro
            else:
                intro = item.restrictedTraverse(
                                            item.getProperty('default_page'))

            if item.hasProperty('layout'):
                item.manage_changeProperties({'layout' : 'themecentre_view'})
            else:
                item.manage_addProperty('layout', 'themecentre_view', 'string')
            if item.hasProperty('default_page'):
                item.manage_delProperties(['default_page'])
            if intro.hasProperty('layout'):
                intro.manage_delProperties(['layout'])
            intro.reindexObject(idxs=['is_default_page'])
        transaction.savepoint()
    return "Done"
