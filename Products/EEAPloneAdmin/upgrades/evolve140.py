""" Cleanup Zope Versions Control
"""
import logging
from Products.CMFCore.utils import getToolByName
from Products.CMFEditions.ZVCStorageTool import Removed
logger = logging.getLogger('Products.EEAPloneAdmin')


def cleanup_zvc_helpcenter(context):
    """ Cleanup history for removed HelpCenter content-types
    """
    tool = getToolByName(context, 'portal_historiesstorage')
    shadow = tool._getShadowStorage()
    histIds = shadow._storage

    count = 0
    total = 0
    for hid in histIds.keys():
        shadowStorage = tool._getShadowHistory(hid)
        size, _sizeState = shadowStorage.getSize()
        ob = tool.retrieve(hid).object.object
        if isinstance(ob, Removed):
            continue
        ptype = ob.getPortalTypeName()
        if not ptype.startswith('HelpCenter'):
            continue

        count += 1
        total += size

        logger.info('Cleanup ZVC for %s:%s at %s. ', ptype, ob.id, hid)

    size = total / 1048576
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
