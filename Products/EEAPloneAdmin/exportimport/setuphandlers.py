""" Setuphandlers
"""
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces import INonInstallable \
    as IPloneFactoryNonInstallable
from Products.CMFQuickInstallerTool.interfaces import INonInstallable \
    as IQuickInstallerNonInstallable
from plone.app.layout.navigation.interfaces import INavigationRoot
from zope.interface import alsoProvides
from zope.interface import implements

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
    """ Clear resource registries
    """

    if context.readDataFile('eeaploneadmin-optimize.txt') is None:
        return

    site = context.getSite()
    jstool = getToolByName(site, 'portal_javascripts')
    csstool = getToolByName(site, 'portal_css')

    for tool in (jstool, csstool):
        tool.cookedresources = ()
        tool.concatenatedresources = {}
        tool.resources = ()


class HiddenProfiles(object):
    """ Hidden Profiles
    """
    implements(IQuickInstallerNonInstallable, IPloneFactoryNonInstallable)

    def getNonInstallableProfiles(self):
        """ Prevents profiles dependencies from showing up in the profile list
            when creating a Plone site.
        """
        return [u'collective.deletepermission:default',
                u'ftw.upgrade:default',
                u'Products.LDAPUserFolder:cmfldap',
                ]

    def getNonInstallableProducts(self):
        """ Prevents our dependencies from showing up in the quick
            installer's list of installable products.
        """
        return [
            'collective.deletepermission',
            'ftw.upgrade',
            'Products.LDAPUserFolder',
            ]
