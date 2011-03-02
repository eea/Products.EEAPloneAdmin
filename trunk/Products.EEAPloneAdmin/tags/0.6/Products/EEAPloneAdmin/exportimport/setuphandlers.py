from zope.interface import alsoProvides
from Products.CMFCore.utils import getToolByName

from Products import SecureMaildropHost
from Products.GenericSetup.utils import importObjects
from Products.CMFPlone.browser.interfaces import INavigationRoot


def setupVarious(context):
    # only run this step if we are in EEAPloneAdmin profile
    # learned from Aspelis book, Professional Plone Development
    if context.readDataFile('eeaploneadmin_various.txt') is None:
        return

    logger = context.getLogger('eea')

    site = context.getSite()
    if not hasattr(site, 'SITE'):
        site.invokeFactory('Folder', id='SITE')
        alsoProvides(site.SITE, INavigationRoot)
        logger.info("eeaploneadmin: created main folder SITE and set INavigationRoot")

    setupMailhost(context)
    setupImageTypes(context)

def setupMailhost(context):
    """ Replaces Secure mail host with Secure Mail drop host. """

    # remove old mail host
    site = context.getSite()
    mailhost = site.MailHost

    # if we have a mail drop host already, we don't need to do anything
    if isinstance(mailhost, SecureMaildropHost.SecureMaildropHost):
        return

    site.manage_delObjects(['MailHost'])
    SecureMaildropHost.manage_addSecureMaildropHost(site, 'MailHost')

def setupImageTypes(context):
    site = context.getSite()
    portal_atct = getToolByName(site, 'portal_atct')

    types = portal_atct.getProperty('image_types', ())
    for type_ in ('Highlight', 'PressRelease', 'Promotion', 'Speech', 'File'):
        if type_ not in types:
            types = types + (type_,)
    portal_atct.manage_changeProperties(image_types=types)

def eeaMigration(context):
    if context.readDataFile('eeaploneadmin_migration.txt') is None:
        return
    
    logger = context.getLogger('eea')
    logger.info("eeamigration_various: running eea migration step")

    logger.info('migrates themecentre layout and default page')
    migration = site.unrestrictedTraverse('@@migrateThemeLayoutAndDefaultPage')
    migration() 

def setupSkins(context):
    """ Load skins path """
    site = context.getSite()
    tool = getToolByName(site, 'portal_skins')
        
    importObjects(tool, '', context)

