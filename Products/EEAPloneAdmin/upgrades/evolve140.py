""" Cleanup Zope Versions Control
"""
import logging
from Products.CMFCore.utils import getToolByName
from Products.CMFEditions.ZVCStorageTool import Removed
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


def cleanup_zvc_helpcenter(context):
    """ Cleanup history for removed HelpCenter content-types
    """
    storage = getToolByName(context, 'portal_historiesstorage')
    tool = getToolByName(context, 'portal_historiesstorage')
    shadow = tool._getShadowStorage()
    histIds = shadow._storage

    count = 0
    total = 0
    to_delete = set()

    for hid in histIds.keys():
        shadowStorage = tool._getShadowHistory(hid)
        size, _sizeState = shadowStorage.getSize()
        try:
            ob = tool.retrieve(hid).object.object
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

    for idx, hid in enumerate(to_delete):
        logger.info('Cleanup ZVC for %s at %s. ', ptype, hid)
        _purge(storage, hid)

    size = total / 1048576 # MB
    logger.info("Cleaned up %s HelpCenter history. Size: %s MB", count, size)

    raise NotImplementedError


def cleanup_zvc_removed(context):
    """ Cleanup history for Removed objects
    """
    raise NotImplementedError


def cleanup_zvc_figurefile(context):
    """ Cleanup history for EEA Figure File
    """
    raise NotImplementedError
