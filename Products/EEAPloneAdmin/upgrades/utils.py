""" Util scripts for updates
"""
import logging
import transaction

from zope.interface import noLongerProvides

from Products.CMFCore.utils import getToolByName
from zope.component import ComponentLookupError
from zope.component.interface import nameToInterface

try:
    from p4a.subtyper.interfaces import ISubtyped
    HAS_Subtyper = True
except ImportError:
    HAS_Subtyper = False


logger = logging.getLogger("Products.EEAPloneAdmin.upgrades")


def bulkReindexObjects(context, brains, idxs=None):
    """ Bulk reindex objects using multi-transactions
    """
    total = len(brains)
    logger.info('Start reindexing')
    logger.info('reindexing %s brains', total)
    inames = [
            "p4a.video.interfaces.IAnyVideoCapable",
            "p4a.video.interfaces.IPossibleVideoContainer",
            "p4a.video.interfaces.IPossibleVideo",
            "p4a.plonevideoembed.interfaces.IAnyVideoLinkCapable",
            "p4a.video.interfaces.IVideoEnhanced",
            "p4a.video.interfaces.IVideoContainerEnhanced"
            ]
    ifaces = []
    for iname in inames:
        try:
            ifaces.append(nameToInterface(context, iname))
        except ComponentLookupError as err:
            logger.debug(err)
    if HAS_Subtyper:
        inames.append("p4a.video.interfaces.IVideoContainerEnhanced")
        ifaces.append(ISubtyped)

    if ifaces and idxs and isinstance(idxs, list):
        idxs.append('object_provides')

    index = 0
    for index, brain in enumerate(brains):
        if index and index % 100 == 0:
            transaction.commit()
            logger.info("Subtransaction committed to zodb (%s/%s)",
                    index, total)
        try:
            obj = brain.getObject()
            if not idxs:
                obj.reindexObject()
                continue

            for iface in ifaces:
                if iface.providedBy(obj):
                    try:
                        noLongerProvides(obj, iface)
                    except ValueError as nerr:
                        logger.debug(nerr)
            obj.reindexObject(idxs=idxs)
        except Exception as err:
            logger.warn("Couldn't reindex: %s", brain.getURL(1))
            logger.exception(err)
    logger.info('Done reindexing %s items', index)


def bulkReindexObjectsSecurity(context, brains, wf_id):
    """ Bulk reindex objects security using multi-transactions
    """
    total = len(brains)
    logger.info('Start reindexing')
    logger.info('Reindexing %s brains', total)

    wf = getToolByName(context, 'portal_workflow')
    wf_def = wf.getWorkflowById(wf_id)
    count = 0

    if wf_def:
        for brain in brains:
            obj = brain.getObject()
            wf_def.updateRoleMappingsFor(obj)

            obj.reindexObject(idxs=['allowedRolesAndUsers', 'review_state'])
            logger.info('Updated role mapping for %s', brain.getURL())

            count += 1
            total = len(brains)

            if count % 100 == 0:
                logger.info('Subtransaction committed to zodb (%s/%s)',
                            count, total)
                transaction.commit()
    else:
        logger.warn('ERROR: %s workflow not found', wf_id)

    logger.info('Done reindexing')
