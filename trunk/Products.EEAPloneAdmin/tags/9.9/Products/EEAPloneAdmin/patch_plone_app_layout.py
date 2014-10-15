""" Patch plone.app.layout ver 2.2.7, due to #9518
"""
from plone.app.layout.navigation import root as nav_root
from Products.CMFCore.utils import getToolByName
from zope.component.hooks import getSite


def getNavigationRootObject(context, portal):
    """ Patched getNavigationRootObject in order to return site root
    """
    if context is None:
        return None

    ### patch #9518 return root + context language as navigationRootObject
    # #16662 define portal as it might be an empty parameter when using a
    # dexterity object
    portal = portal or getSite()
    portal_url = '/'.join(portal.getPhysicalPath())
    if portal_url[-1] != '/':
        portal_url += '/'
    lang = context.Language()
    # check if portal_url is /www as this code could be reached from tests
    # where we don't have SITE
    if portal_url != '/www/':
        return portal
    if lang:
        # use  same logic for getting the navigationRootObject like the
        # one used and explained in getNavigationRoot
        context_path_root = context.getPhysicalPath()
        context_path_root = context_path_root[2] if \
                    len(context_path_root) > 2 else context_path_root[-1]
        lang = lang if lang != 'en' else 'SITE'
        if context_path_root != lang:
            return portal.get(context_path_root)
        else:
            return portal.get(lang)
    return portal
    ### end patch


def getNavigationRoot(context, relativeRoot=None):
    """Get the path to the root of the navigation tree.

    If a relativeRoot argument is provided, navigation root is computed from
    portal path and this relativeRoot.

    If no relativeRoot argument is provided, and there is a root value set in
    portal_properties, navigation root path is computed from
    portal path and this root value.

    IMPORTANT !!!
    Previous paragraphs imply relativeRoot is relative to the Plone portal.

    Else, a root must be computed : loop from the context to the portal,
    through parents, looking for an object implementing INavigationRoot.
    Return the path of that root.
    """
    portal_url = getToolByName(context, 'portal_url')

    if relativeRoot is None:
        # fetch from portal_properties
        portal_properties = getToolByName(context, 'portal_properties')
        navtree_properties = getattr(portal_properties, 'navtree_properties')
        relativeRoot = navtree_properties.getProperty('root', None)

    ### Original code:

    ## if relativeRoot has a meaningful value,
    #if relativeRoot and relativeRoot != '/':
    #    # use it
    #
    #    # while taking care of case where
    #    # relativeRoot is not starting with a '/'
    #    if relativeRoot[0] != '/':
    #        relativeRoot = '/' + relativeRoot

    #    portalPath = portal_url.getPortalPath()
    #    return portalPath + relativeRoot

    ### Start patch

    if relativeRoot:
        if relativeRoot[0] != '/':
            relativeRoot = '/' + relativeRoot

        portalPath = portal_url.getPortalPath()
        # return old logic if portalPath isn't /www
        if portalPath != '/www':
            return portalPath + relativeRoot
        lang = context.Language()
        portal = portal_url.getPortalObject()
        if lang:
            lang = lang if lang != 'en' else 'SITE'
            context_path_root = context.getPhysicalPath()
            # check if length of physicalPath is greater than 2 as we might
            # get a result where we are on the root path and it results in
            # ('', 'www')
            context_path_root = context_path_root[2] if \
                    len(context_path_root) > 2 else context_path_root[-1]
            # context_path_root will return the path after www, from the
            # context, if it is not equal to lang then it means that the
            # context is of different language from the root of the context
            # but we should use that context_path_root in order to preserve
            # correct listing ex: /www/SITE/tests/romanian-page should return
            # /www/SITE as the navigationRoot and not /www/ro even thou the
            # page is romanian since it is created in the /www/SITE english
            # folder
            if context_path_root != lang:
                return portalPath + '/' + context_path_root
            else:
                return portalPath + '/' + lang
        return portalPath + relativeRoot
    ### End patch

    else:
        # compute the root
        portal = portal_url.getPortalObject()
        root = getNavigationRootObject(context, portal)
        return '/'.join(root.getPhysicalPath())

nav_root.getNavigationRoot = getNavigationRoot
nav_root.getNavigationRootObject = getNavigationRootObject
