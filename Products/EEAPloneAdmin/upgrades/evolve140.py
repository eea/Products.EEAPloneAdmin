""" Cleanup Zope Versions Control
"""
import logging
from Products.CMFCore.utils import getToolByName
from Products.CMFEditions.ZVCStorageTool import Removed
from Products.EEAPloneAdmin.upgrades.utils import timeout
logger = logging.getLogger('Products.EEAPloneAdmin')


def _purge(storage, hid):
    """Purge all versions """
    while True:
        length = len(storage.getHistory(hid, countPurged=False))
        if length <= 0:
            break

        storage.purge(hid, 0,  metadata={'sys_metadata': {
            'comment': "Products.EEAPloneAdmin.upgrades:evolve140"}
        }, countPurged=False)

@timeout
def _getHistoryObject(tool, hid):
    """ Get history by id
    """
    return tool.retrieve(hid).object.object

def cleanup_zvc_helpcenter(context):
    """ Cleanup history for removed HelpCenter content-types
    """
    storage = getToolByName(context, 'portal_historiesstorage')
    tool = getToolByName(context, 'portal_historiesstorage')
    shadow = tool._getShadowStorage()
    histIds = shadow._storage
    length = len(histIds)

    count = 0
    total = 0
    to_delete = set()

    logger.info(
        "Cleanup ZVC Searching for HelpCenter ctypes within %s entries", length)
    for idx, hid in enumerate(histIds.keys()):
        shadowStorage = tool._getShadowHistory(hid)
        size, _sizeState = shadowStorage.getSize()

        if idx % 100 == 0:
            logger.info("Cleanup ZVC Searching for HelpCenter progress %s/%s",
                        idx, length)

        try:
            ob = _getHistoryObject(tool, hid)
        except Exception, err:
            logger.exception(err)
            continue

        if isinstance(ob, Removed):
            continue

        ptype = ob.getPortalTypeName()
        if not ptype.startswith('HelpCenter'):
            continue

        to_delete.add(hid)
        total += size

    length = len(to_delete)
    logger.info(
        "Cleanup ZVC Removing history for %s HelpCenter objects", length)

    for idx, hid in enumerate(to_delete):
        logger.info('%s. Cleanup ZVC HelpCenter history_id: %s. ', idx, hid)
        _purge(storage, hid)

    size = total / 1048576 # MB
    logger.info("Cleaned up %s HelpCenter history. Size: %s MB", length, size)

    raise NotImplementedError


def cleanup_zvc_removed(context):
    """ Cleanup history for Removed objects
    """
    raise NotImplementedError


def cleanup_zvc_figurefile(context):
    """ Cleanup history for EEA Figure File
    """
    raise NotImplementedError
