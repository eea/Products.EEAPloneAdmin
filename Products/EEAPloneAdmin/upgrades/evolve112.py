""" Migrating HelpCenter Content-Types to Dexterity objects.
"""
import logging
from zExceptions import BadRequest
from Products.contentmigration.basemigrator.migrator import CMFFolderMigrator
from Products.contentmigration.basemigrator.migrator import CMFItemMigrator
from Products.contentmigration.basemigrator.walker import CatalogWalker
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from plone.app.textfield.value import RichTextValue
logger = logging.getLogger('Products.EEAPloneAdmin')


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
    def migrate_layout(self):
        """ Migrate fields
        """
        try:
            self.new._setProperty('layout', 'folder_listing', 'string')
        except BadRequest:
            logger.warn('%s update. Old layout: %s. New layout: folder_listing',
                        self.new.title_or_id(), self.new.layout)
            self.new._updateProperty('layout', 'folder_listing')


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
    dst_portal_type = 'Folder'
    dst_meta_type = 'ATFolder'


def migrate_glossary(portal):
    """ Migrate Help Center Definition items
    """
    return migrate(portal, HelpCenterGlossary)

class HelpCenterFAQ(ATCTContentMigrator):
    """ Migrator for Help Center FAQ
    """
    src_portal_type = 'HelpCenterFAQ'
    src_meta_type = 'HelpCenterFAQ'
    dst_portal_type = 'helpcenter_faq'
    dst_meta_type = None  # not used

    def migrate_schema_fields(self):
        """ Migrate fields
        """
        # Text
        field = self.old.getField('text')
        mime_type = field.getContentType(self.old)
        raw_text = safe_unicode(field.getRaw(self.old))
        if raw_text.strip() == '':
            return
        richtext = RichTextValue(raw=raw_text, mimeType=mime_type,
                                 outputMimeType='text/x-html-safe')
        self.new.text = richtext

        # Sections
        field = self.old.getField('sections')
        sections = [s.strip() for s in field.getAccessor(self.old)()
                              if s.strip()]
        self.new.sections = sections


def migrate_faq(portal):
    """ Migrate Help Center FAQ items
    """
    return migrate(portal, HelpCenterFAQ)


class HelpCenterFAQFolder(ATCTFolderMigrator):
    """ Migrator for Help Center FAQ Folder
    """
    src_portal_type = 'HelpCenterFAQFolder'
    src_meta_type = 'HelpCenterFAQFolder'
    dst_portal_type = 'Folder'
    dst_meta_type = 'ATFolder'

    def migrate_schema_fields(self):
        """ Properties
        """
        # Sections
        field = self.old.getField('sectionsVocab')
        sections = field.getAccessor(self.old)()
        self.new.sectionsVocab = sections


def migrate_faqfolder(portal):
    """ Migrate Help Center FAQ Folder items
    """
    return migrate(portal, HelpCenterFAQFolder)


class HelpCenterVideo(ATCTContentMigrator):
    """ Migrator for Help Center FAQ
    """
    src_portal_type = 'HelpCenterInstructionalVideo'
    src_meta_type = 'HelpCenterInstructionalVideo'
    dst_portal_type = 'File'
    dst_meta_type = 'ATBlob'

    def migrate_schema_fields(self):
        """ Migrate schema
        """
        old_file = self.old.getField('video_file').getAccessor(self.old)()
        self.new.getField('file').getMutator(self.new)(old_file)


def migrate_video(portal):
    """ Migrate Help Center FAQ items
    """
    return migrate(portal, HelpCenterVideo)


class HelpCenterVideoFolder(ATCTFolderMigrator):
    """ Migrator for Help Center Video Folder
    """
    src_portal_type = 'HelpCenterInstructionalVideoFolder'
    src_meta_type = 'HelpCenterInstructionalVideoFolder'
    dst_portal_type = 'Folder'
    dst_meta_type = 'ATFolder'


def migrate_videofolder(portal):
    """ Migrate Help Center FAQ Folder items
    """
    return migrate(portal, HelpCenterVideoFolder)


class HelpCenter(ATCTFolderMigrator):
    """ Migrator for Help Center
    """
    src_portal_type = 'HelpCenter'
    src_meta_type = 'HelpCenter'
    dst_portal_type = 'Folder'
    dst_meta_type = 'ATFolder'


def migrate_helpcenter(portal):
    """ Migrate Help Center items
    """
    return migrate(portal, HelpCenter)


def migrate_to_dexterity(context):
    """ Migrate Help Center ctypes to Dexterity
    """
    portal = getToolByName(context, 'portal_url').getPortalObject()

    logger.info('Migrating HelpCenter Definition => Dexterity')
    migrate_definition(portal)

    logger.info('Migrating HelpCenter Glossary => Folder')
    migrate_glossary(portal)

    logger.info('Migrating HelpCenter FAQ => Dexterity')
    migrate_faq(portal)

    logger.info('Migrating HelpCenter FAQ Folder => Folder')
    migrate_faqfolder(portal)

    logger.info('Migrating HelpCenter Video => File')
    migrate_video(portal)

    logger.info('Migrating HelpCenter Video Folder => Folder')
    migrate_videofolder(portal)

    logger.info('Migrating HelpCenter => Folder')
    migrate_helpcenter(portal)

def cleanup_broken_brains(context):
    """ uncatalog broken brains objects
    """
    ctool = getToolByName(context, 'portal_catalog')
    brains = ctool(portal_type=[
        'HelpCenterDefinition',
        'HelpCenterGlossary',
        'HelpCenterFAQ',
        'HelpCenterFAQFolder',
        'HelpCenterInstructionalVideo',
        'HelpCenterInstructionalVideoFolder',
        'HelpCenter'
    ])

    for brain in brains:
        path = brain.getURL()
        if 'rdfstype' in path:
            logger.info('Cleanup %s', path)
            ctool.uncatalog_object(brain.getPath())
