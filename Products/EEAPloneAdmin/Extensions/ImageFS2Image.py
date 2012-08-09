""" Migrate ImageFS to Image"""
#from Products.contentmigration.basemigrator import walker
from plone.app.blob.migrations import ATImageToBlobImageMigrator
from zope.component import getUtility
from Products.CMFCore.interfaces import ISiteRoot
#from StringIO import StringIO
#from plone.app.blob.migrations import migrate
from Products.CMFCore.utils import getToolByName
#from Products.Archetypes.interfaces import IReferenceable


#from plone.app.blob.migrations import migrateATBlobImages
from plone.app.blob.migrations import ATImageToBlobImageMigrator
from Products.Archetypes.ArchetypeTool import getType
from Acquisition import aq_base
from Acquisition import aq_parent
from Acquisition import aq_inner
from plone.locking.interfaces import ILockable

import logging
logger = logging.getLogger('Products.EEAPloneAdmin')

def ImageFS2Image(self):
    """ Migrate ImageFS to Image"""
    
    portal = getUtility(ISiteRoot)

    ctool = getToolByName(portal, 'portal_catalog')
#    uid_cat = getToolByName(portal, 'uid_catalog')
#    import pdb; pdb.set_trace()
#    brains = ctool.unrestrictedSearchResults(portal_type='ImageFS')
#    uc = getToolByName(container, config.UID_CATALOG)
    brains = ctool.unrestrictedSearchResults(Title='img100')
    total = len(brains)
    logger.info(('Migrating %s instances of '
                 'ImageFS to Image'), total)

    for index, brain in enumerate(brains[0:5]):
        logger.info('\t Migration status: %s/%s', index+1, total)
        img = brain.getObject()

        old_obj = aq_inner(img)
        orig_id = old_obj.getId()
        old_id = '%s_MIGRATION_' % orig_id

        parent = aq_parent(img)
        while hasattr(aq_base(parent), old_id):
            old_id += 'X'


        lockable = ILockable(old_obj, None)
        if lockable and lockable.locked():
            lockable.unlock()

#        try:
#            import pdb; pdb.set_trace()
#            migrator = imageMigrator(img)
#            migrator.migrate()
#            migrator.new._at_uid = migrator.old._at_uid
#            migrator.new.reindexObject()
#        except Exception, err:
#            logger.exception(err)
    
    logger.info(('Finish migration of %s instances of '
                 'ImageFS to Image'), total)
    return "Done"


class imageMigrator(ATImageToBlobImageMigrator):
    """ Migrator """

    src_portal_type = "ImageFS"
    src_meta_type = "ATImage"
#    only_fields_map = True
    def _migrate_at_uuid(self):
        """ migrate at uuid """
#        pass
        self.old._uncatalogUID(self.parent)
        self.new._at_uid = self.old.UID()
    def _migrate_data(self):
        """ docs"""
        pass
    def _migrate_extension_fields(self):
        """ docs"""
        pass
    def _migrate_references(self):
        """ docs"""
        pass
    def _last_migrate_reindex(self):
        """ docs"""
        pass
        

    def _beforeChange_schema(self):
        """Load the values of fields according to fields_map if present.

        Each key in fields_map is a field in the old schema and each
        value is a field in the new schema.  If fields_map isn't a
        mapping, each field in the old schema will be migrated into
        the new schema.  Obeys field modes for readable and writable
        fields.  These values are then passed in as field kwargs into
        the constructor in the createNew method."""

        old_schema = self.old.Schema()

        typesTool = getToolByName(self.parent, 'portal_types')
        fti = typesTool.getTypeInfo(self.dst_portal_type)
        archetype = getType(self.dst_meta_type, fti.product)
        new_schema = archetype['klass'].schema

        if self.only_fields_map:
            old_field_names = self.fields_map.keys()
        else:
            old_field_names = old_schema.keys()

        # Let the migrator handle the id and dates
        for omit_field_name in ['id', 'creation_date',
                                'modification_date', 'title']:
            if omit_field_name in old_field_names:
                old_field_names.remove(omit_field_name)

        kwargs = getattr(self, 'schema', {})
        for old_field_name in old_field_names:
            old_field = self.old.getField(old_field_name)
            new_field_name = self.fields_map.get(old_field_name,
                                                 old_field_name)

            if new_field_name is None:
                continue

            new_field = new_schema.get(new_field_name, None)
            if new_field is None:
                continue

            if ('r' in old_field.mode and 'w' in new_field.mode):
                accessor = (
                    getattr(old_field, self.accessor_getter)(self.old)
                    or old_field.getAccessor(self.old))
                value = accessor()
                kwargs[new_field_name] = value
        self.schema = kwargs

#        self.new.reindexObject()
#        if not IReferenceable.providedBy(self.old):
#            return  # old object doesn't support AT uuids
#        uid = self.old.UID()
#        self.old._uncatalogUID(self.parent)
#        import pdb; pdb.set_trace()
#        self.new._setUID(uid)
