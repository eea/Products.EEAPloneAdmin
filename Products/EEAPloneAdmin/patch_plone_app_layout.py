""" Patch plone.app.layout ver 2.2.7, due to #9518
"""

from plone.app.layout.navigation.root import getNavigationRootObject
from plone.app.layout.navigation import root 
from Products.CMFCore.utils import getToolByName


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
        portalPath = portal_url.getPortalPath()
        lang = context.Language()
        # set relativeRoot to be the language of the context
        relativeRoot = relativeRoot + lang if lang != 'en' else '/SITE'
        return portalPath + relativeRoot
    ### End patch

    else:
        # compute the root
        portal = portal_url.getPortalObject()
        root = getNavigationRootObject(context, portal)
        return '/'.join(root.getPhysicalPath())

root.getNavigationRoot = getNavigationRoot
