""" Setuphandlers
"""
from Products.CMFCore.utils import getToolByName
from plone.app.layout.navigation.interfaces import INavigationRoot
from zope.interface import alsoProvides


def setupVarious(context):
    """ Only run this step if we are in EEAPloneAdmin profile
        learned from Aspelis book, Professional Plone Development
    """
    if context.readDataFile('eeaploneadmin_various.txt') is None:
        return

    logger = context.getLogger('eea')

    site = context.getSite()
    if not hasattr(site, 'SITE'):
        site.invokeFactory('Folder', id='SITE')
        alsoProvides(site.SITE, INavigationRoot)
        logger.info("eeaploneadmin: created main folder SITE and set \
                     INavigationRoot")

    configureWorkflow(site)
    setupImageTypes(context)


def configureWorkflow(portal):
    """ Configure what can't be configured with generic setup
    """
    wf = getToolByName(portal, 'portal_workflow')
    if wf is not None:
        wf['eea_default_workflow'].manager_bypass = True


def setupImageTypes(context):
    """ Setup image types
    """
    site = context.getSite()
    portal_atct = getToolByName(site, 'portal_atct')

    types = portal_atct.getProperty('image_types', ())
    for type_ in ('Highlight', 'PressRelease', 'Promotion', 'Speech', 'File'):
        if type_ not in types:
            types = types + (type_,)
    portal_atct.manage_changeProperties(image_types=types)

def clear_registries(context):
    """Clear resource registries
    """
    site = context.getSite()
    jstool  = getToolByName(site, 'portal_javascripts')
    csstool = getToolByName(site, 'portal_javascripts')

    for tool in (jstool, csstool):
        tool.cookedresources = ()
        tool.concatenatedresources = {}
        tool.resources = ()
