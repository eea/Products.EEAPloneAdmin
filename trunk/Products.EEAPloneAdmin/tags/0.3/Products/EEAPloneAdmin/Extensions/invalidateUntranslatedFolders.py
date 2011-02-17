from Products.CMFCore.utils import getToolByName


COMMENT = "Was not able to translate the title of this folder automatically. \
        One needs to be set manually."


def invalidateUntranslatedFolders(context):
    """Invalidate folder translations that have the same title as the original.
    """
    plone_utils = getToolByName(context, 'plone_utils')
    urltool = getToolByName(context, 'portal_url')
    portal = urltool.getPortalObject()
    wf = getToolByName(context, 'portal_workflow')
    ct = getToolByName(context, 'portal_catalog')

    results = ct({'portal_type': ['Folder', 'ATFolder'], 'Language': 'en'})

    for b in results:
        folder = b.getObject()
        for lang in folder.getTranslations().values():
            translated = lang[0]
            if translated == folder:
                continue
            if translated.Title() == folder.Title():
                print "invalidating", translated.Title()
                lingua = wf.linguaflow
                lingua.doActionFor(translated, 'invalidate', comment=COMMENT)
