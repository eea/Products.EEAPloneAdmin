""" Migrating HelpCenter Content-Types to Dexterity objects.
"""
from Products.contentmigration.basemigrator.migrator import CMFFolderMigrator
from Products.contentmigration.basemigrator.migrator import CMFItemMigrator
from Products.contentmigration.basemigrator.walker import CatalogWalker
from Products.CMFCore.utils import getToolByName


def migrate(portal, migrator):
    """ Run migration
    """
    walker = CatalogWalker(portal, migrator)
    return walker.go()


class ATCTContentMigrator(CMFItemMigrator):
    """Base for contentish ATCT
    """


class ATCTFolderMigrator(CMFFolderMigrator):
    """Base for folderish ATCT
    """


class HelpCenterDefinition(ATCTContentMigrator):
    """ Migrator for Help Center Definition
    """
    src_portal_type = 'HelpCenterDefinition'
    src_meta_type = 'HelpCenterDefinition'
    dst_portal_type = 'helpcenter_definition'
    dst_meta_type = None  # not used


def migrate_definition(portal):
    """ Migrate Help Center Definition items
    """
    return migrate(portal, HelpCenterDefinition)


class HelpCenterGlossary(ATCTFolderMigrator):
    """ Migrator for Help Center Glossary
    """
    src_portal_type = 'HelpCenterGlossary'
    src_meta_type = 'HelpCenterGlossary'
    dst_portal_type = 'helpcenter_glossary'
    dst_meta_type = None  # not used


def migrate_glossary(portal):
    """ Migrate Help Center Definition items
    """
    return migrate(portal, HelpCenterGlossary)


def migrate_to_dexterity(context):
    """ Migrate Help Center ctypes to Dexterity
    """
    portal = getToolByName(context, 'portal_url').getPortalObject()
    migrate_definition(portal)
    migrate_glossary(portal)
