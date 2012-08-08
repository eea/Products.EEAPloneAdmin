""" Migrate ImageFS to Image"""
#from Products.contentmigration.basemigrator import walker
from plone.app.blob.migrations import ATImageToBlobImageMigrator
from zope.component import getUtility
from Products.CMFCore.interfaces import ISiteRoot
#from StringIO import StringIO
#from plone.app.blob.migrations import migrate
from Products.CMFCore.utils import getToolByName
from Products.Archetypes.interfaces import IReferenceable

import logging
logger = logging.getLogger('Products.EEAPloneAdmin')

def ImageFS2Image(self):
    """ Migrate ImageFS to Image"""
    portal = getUtility(ISiteRoot)

    ctool = getToolByName(portal, 'portal_catalog')
#    brains = ctool.unrestrictedSearchResults(portal_type='ImageFS')
    brains = ctool.unrestrictedSearchResults(Title='img16')
    total = len(brains)
    logger.info(('Migrating %s instances of '
                 'ImageFS to Image'), total)

    for index, brain in enumerate(brains[0:5]):
        logger.info('\t Migration status: %s/%s', index+1, total)
        try:
            img = brain.getObject()
            migrator = imageMigrator(img)
            migrator.migrate()
            migrator.new.reindexObject()
        except Exception, err:
            logger.exception(err)

    logger.info(('Finish migration of %s instances of '
                 'ImageFS to Image'), total)


class imageMigrator(ATImageToBlobImageMigrator):
    """ Migrator """
    def migrate_at_uuid(self):
        """ migrate at uuid """
        if not IReferenceable.providedBy(self.old):
            return  # old object doesn't support AT uuids
        uid = self.old.UID()
        self.old._uncatalogUID(self.parent)
#        import pdb; pdb.set_trace()
        self.new._setUID(uid)
