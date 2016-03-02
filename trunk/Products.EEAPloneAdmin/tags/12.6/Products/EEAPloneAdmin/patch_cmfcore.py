""" Patch Products.CMFCore due to #18138, as deleting a local user
    is a very long process which most usually endup in database conflict error
    on a live portal
"""

from difflib import unified_diff
from Products.CMFCore.utils import _checkPermission
from Products.CMFCore.permissions import ChangeLocalRoles
from Acquisition import aq_base
import transaction
import logging

logger = logging.getLogger("Products.EEAPloneAdmin.patch_cmfcore")

object_count = 0

def patched_icon(self, *args, **kwargs):
    """ Icon
    """
    icon = self._old_icon(*args, **kwargs)
    return icon.strip("/")

def patched_deleteLocalRoles(self, obj, member_ids, reindex=1, recursive=0,
                             REQUEST=None):
    """ Delete local roles of specified members.
    """
    global object_count
    object_count += 1
    if object_count % 10000 == 0:
        transaction.commit()
        logger.info('Deleting members: %s', member_ids)

    if _checkPermission(ChangeLocalRoles, obj):
        for member_id in member_ids:
            if obj.get_local_roles_for_userid(userid=member_id):
                obj.manage_delLocalRoles(userids=member_ids)
                break

    if recursive and hasattr(aq_base(obj), 'contentValues'):
        for subobj in obj.contentValues():
            self.deleteLocalRoles(subobj, member_ids, 0, 1, REQUEST)

    if reindex and hasattr(aq_base(obj), 'reindexObjectSecurity'):
        # reindexObjectSecurity is always recursive
        obj.reindexObjectSecurity()

def _getFileContent(f):
    """ File content
    """
    try:
        return f.read()
    except AttributeError:
        try:
            return f.data
        except AttributeError:
            return f._readFile(0)
    else:
        return ''

def patched_getDiff(self, item_one_path, item_two_path, reverse=0):
    """ Return a diff between one and two.
    """
    if not reverse:
        item_one = self.unrestrictedTraverse(item_one_path)
        item_two = self.unrestrictedTraverse(item_two_path)
    else:
        item_one = self.unrestrictedTraverse(item_two_path)
        item_two = self.unrestrictedTraverse(item_one_path)

    item_one_contents = _getFileContent(item_one)
    item_two_contents = _getFileContent(item_two)
    # item_one.read().splitlines()

    res = unified_diff(item_one_contents.splitlines()
                       , item_two_contents.splitlines()
                       , item_one_path
                       , item_two_path
                       , ''
                       , ''
                       , lineterm=""
                       )
    return res
