""" Migrate ImageFS to Image"""
from Products.contentmigration.basemigrator import walker
from plone.app.blob.migrations import ATImageToBlobImageMigrator
from zope.component import getUtility
from Products.CMFCore.interfaces import ISiteRoot
from StringIO import StringIO
from plone.app.blob.migrations import migrate

def ImageFS2Image(self):
    """ Migrate ImageFS to Image"""
    portal = getUtility(ISiteRoot)
    migrate(portal, 'ImageFS')

class imageMigrator(ATImageToBlobImageMigrator):
    """ Migrator """
    src_portal_type = 'ImageFS'
    src_meta_type = 'ImageFS'
