""" Migrate ImageFS to Image"""
#from Products.contentmigration.basemigrator import walker
#from plone.app.blob.migrations import ATImageToBlobImageMigrator
from zope.component import getUtility
from Products.CMFCore.interfaces import ISiteRoot
#from StringIO import StringIO
#from plone.app.blob.migrations import migrate
from Products.CMFCore.utils import getToolByName
#from Products.Archetypes.interfaces import IReferenceable


#from plone.app.blob.migrations import migrateATBlobImages
#from plone.app.blob.migrations import ATImageToBlobImageMigrator
from Products.Archetypes.ArchetypeTool import getType
from Acquisition import aq_base
from Acquisition import aq_parent
from Acquisition import aq_inner
from plone.locking.interfaces import ILockable


#from OFS.interfaces import IOrderedContainer
from Products.Archetypes.interfaces import IReferenceable
from Products.contentmigration.basemigrator.migrator import METADATA_MAPPING
from Products.contentmigration.basemigrator.migrator import getPermissionMapping
from Products.Archetypes.config import REFERENCE_ANNOTATION
from Products.Archetypes.Referenceable import Referenceable

from Products.contentmigration.common import _createObjectByType
#from Products.CMFPlone.utils import _createObjectByType
#from zope.component import createObject
from plone.app.blob.content import addATBlobImage
from ZODB.POSException import ConflictError
import transaction

import logging
logger = logging.getLogger('Products.EEAPloneAdmin')

def ImageFS2Image(self):
    """ Migrate ImageFS to Image"""
    portal = getUtility(ISiteRoot)

    ctool = getToolByName(portal, 'portal_catalog')
    brains = ctool.unrestrictedSearchResults(Title='img135')
    total = len(brains)
    logger.info(('Migrating %s instances of '
                 'ImageFS to Image'), total)

    dst_portal_type = 'Image'
    dst_meta_type = 'ATBlob'
    only_fields_map = False
    fields_map = {}
    mymap = {}
    accessor_getter = 'getEditAccessor'
    for index, brain in enumerate(brains[0:5]):
        logger.info('\t Migration status: %s/%s', index+1, total)
        img = brain.getObject()


        tmp_obj = {}
        _marker = []

        old_obj = aq_inner(img)

        orig_id = old_obj.getId()
        old_id = '%s_MIGRATION_' % orig_id

        parent = aq_parent(img)
        """
        while hasattr(aq_base(parent), old_id):
            old_id += 'X'

        """
#unlock
        lockable = ILockable(old_obj, None)
        if lockable and lockable.locked():
            lockable.unlock()
        """
#before
    #allowDiscussion
        if (getattr(aq_base(old_obj), 'allowDiscussion', _marker) is
            not _marker):
            tmp_obj['isDiscussable'] = old_obj.allowDiscussion()
    #at_uuid
        if IReferenceable.providedBy(old_obj):
            tmp_obj['UID'] = old_obj.UID()
#            old_obj._uncatalogUID(parent)
        else:
            tmp_obj['UID'] = None
    #cmf_uid
        uidhandler = getToolByName(parent, 'portal_uidhandler',
                                   None)
        if uidhandler is not None:
            tmp_obj['uid'] = uidhandler.queryUid(old_obj, default=None)
    #dc
        for accessor, mutator in METADATA_MAPPING:
            oldAcc = getattr(old_obj, accessor)
            oldValue = oldAcc()
            tmp_obj[mutator] = oldValue
    #discussion
        tmp_obj['talkback'] = getattr(old_obj.aq_inner.aq_explicit,
                                'talkback', _marker)
    #localroles
        tmp_obj['__ac_local_roles__'] = old_obj.__ac_local_roles__
        if hasattr(old_obj, '__ac_local_roles_block__'):
            tmp_obj['__ac_local_roles_block__'] = (
                old_obj.__ac_local_roles_block__)
    #owner
        if hasattr(aq_base(old_obj), 'getWrappedOwner'):
            tmp_obj['owner'] = old_obj.getWrappedOwner()
        else:
            tmp_obj['_owner'] = old_obj.getOwner(info = 1)
    #permission_settings
        tmp_obj['ac_inherited_permissions'] = getPermissionMapping(
            old_obj.ac_inherited_permissions(1))
    #properties
        _properties_ignored = ('title', 'description', 'content_type')
        if hasattr(aq_base(old_obj), 'propertyIds'):
            for my_id in old_obj.propertyIds():
                if my_id in _properties_ignored:
                    # migrated by dc or other
                    continue

                value = old_obj.getProperty(my_id)
                typ = old_obj.getPropertyType(my_id)

                tmp_obj['_properties'] += ({'id': my_id,
                                      'type': typ,
                                      'value': value},)

    #references
        old_obj._v_cp_refs = 1
        # Move the references annotation storage
        if hasattr(old_obj, REFERENCE_ANNOTATION):
            at_references = getattr(old_obj, REFERENCE_ANNOTATION)
            tmp_obj[REFERENCE_ANNOTATION] = at_references
    #schema
        old_schema = old_obj.Schema()

        typesTool = getToolByName(parent, 'portal_types')
        fti = typesTool.getTypeInfo(dst_portal_type)
        archetype = getType(dst_meta_type, fti.product)
        new_schema = archetype['klass'].schema

        if only_fields_map:
            old_field_names = fields_map.keys()
        else:
            old_field_names = old_schema.keys()

        for omit_field_name in ['id', 'creation_date',
                                'modification_date']:
            if omit_field_name in old_field_names:
                old_field_names.remove(omit_field_name)

        kwargs = {}
        for old_field_name in old_field_names:
            old_field = old_obj.getField(old_field_name)
            new_field_name = fields_map.get(old_field_name,
                                            old_field_name)

            if new_field_name is None:
                continue

            new_field = new_schema.get(new_field_name, None)
            if new_field is None:
                continue

            if ('r' in old_field.mode and 'w' in new_field.mode):
                accessor = (
                    getattr(old_field, accessor_getter)(old_obj)
                    or old_field.getAccessor(old_obj))
                value = accessor()
                kwargs[new_field_name] = value
        tmp_obj['schema'] = kwargs
    #storeDates
        tmp_obj['old_creation_date'] = old_obj.CreationDate()
        tmp_obj['old_mod_date'] = old_obj.ModificationDate()
    #withmap
        for oldKey, newKey in mymap.items():
            if not newKey:
                newKey = oldKey

            oldVal = getattr(old_obj, oldKey)
            if callable(oldVal):
                value = oldVal()
            else:
                value = oldVal

            tmp_obj['newKey'] = value

    #workflow
        tmp_obj['workflow_history'] = getattr(old_obj, 'workflow_history',
                                        None)


#order
#        need_order = IOrderedContainer.providedBy(old_obj)
#        if need_order:
#            _position = old_obj.parent.getObjectPosition(orig_id)

        """
#        self.renameOld()
        orig_uid = old_obj.UID()
        old_obj.unindexObject()
        old_obj._uncatalogUID(parent)
        parent.manage_delObjects([orig_id])
        transaction.commit()


#        import pdb; pdb.set_trace()

#        self.createNew()
#        new_obj = getattr(aq_inner(parent).aq_explicit, orig_id)
#        new_obj = _createObjectByType(dst_portal_type, parent, orig_id)
#        addATBlobImage(parent, orig_id)
#        new_obj = getattr(aq_inner(parent).aq_explicit, orig_id)
#        addATBlobImage(parent, orig_id)

#        _createObjectByType("ImageFS", parent, orig_id)
#        orig_id = "x2"
        parent.invokeFactory("Image", orig_id)
        new_obj = getattr(aq_inner(parent).aq_explicit, orig_id)
#        new_obj._setUID(old_obj.UID())
#        new_obj._setUID(orig_uid)
        xxx = new_obj.Title()
        new_obj._at_uid = orig_uid
#        new_obj._at_uid = "123456"
        xxx = new_obj.Title()
        new_obj.reindexObject(idxs=['object_provides', 'portal_type',
            'Type', 'UID'])

#after
    #at_uuid
#        new_obj._setUID(tmp_obj['UID'])
#        new_obj._setUID("11111")
        """
    #cmf_uid
        uid = tmp_obj['uid']
        if uid is not None:
            uidhandler.setUid(new_obj, uid, check_uniqueness=False)


    #data
    #discussion
    #extension_fields
        new_obj.update(**tmp_obj['schema'])

    #localroles
    #marker_interfaces
    #owner
    #permission_settings
    #properties
        if not hasattr(aq_base(old_obj), 'propertyIds') or \
          not hasattr(aq_base(new_obj), '_delProperty'):
            # no properties available
            return None

        for my_id in old_obj.propertyIds():
            if my_id in ('title', 'description', 'content_type', ):
                # migrated by dc or other
                continue
            value = old_obj.getProperty(my_id)
            typ = old_obj.getPropertyType(my_id)
#            __traceback_info__ = (new_obj, my_id, value, typ)
            if new_obj.hasProperty(my_id):
                new_obj._delProperty(my_id)
            # continue if the object already has this attribute
            if getattr(aq_base(new_obj), my_id, _marker) is not _marker:
                continue
            try:
                new_obj._setProperty(my_id, value, typ)
            except ConflictError:
                raise
            except:
                pass

    #references
        at_references = tmp_obj.get(REFERENCE_ANNOTATION, None)
        if at_references:
            setattr(new_obj, REFERENCE_ANNOTATION, at_references)
        # Run the reference manage_afterAdd to transition all copied
        # references
        is_cp = getattr(old_obj, '_v_is_cp', _marker)
        new_obj._v_is_cp = 0
        Referenceable.manage_afterAdd(new_obj, new_obj,
                                      new_obj.__parent__)
        if is_cp is not _marker:
            new_obj._v_is_cp = is_cp
        else:
            del new_obj._v_is_cp

    #user_roles
    #withmap
    #workflow
    #custom
    #finalize
    #last_migrate_date
    #last_migrate_reindex

#        self.reorder()
#        self.removeOld()
        """
    logger.info(('Finish migration of %s instances of '
                 'ImageFS to Image'), total)
    return "Done"


