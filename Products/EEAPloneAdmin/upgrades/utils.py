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
info = logger.info
info_exception = logger.exception

def bulkReindexObjects(context, brains, idxs=None):
    """ Bulk reindex objects using multi-transactions
    """
    total = len(brains)
    info('INFO: Start reindexing')
    info('INFO: reindexing %s brains', total)
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
        except ComponentLookupError:
            info_exception('Cant find interface from %s name', iname)
    # add ISubtyped since for some reason it gives a ComponentLookupError
    if HAS_Subtyper:
        inames.append("p4a.video.interfaces.IVideoContainerEnhanced")
        ifaces.append(ISubtyped)

    if idxs and isinstance(idxs, list):
        idxs.append('object_provides')

    for index, brain in enumerate(brains):
        try:
            obj = brain.getObject()
            if idxs:
                for iface in ifaces:
                    if iface.providedBy(obj):
                        try:
                            noLongerProvides(obj, iface)
                        except ValueError:
                            pass
                obj.reindexObject(idxs=idxs)
            else:
                obj.reindexObject()
            if index % 100 == 0:
                transaction.commit()
                msg = 'INFO: Subtransaction committed to zodb (%s/%s)'
                info(msg, index, total)
        except Exception:
            info('ERROR: error during reindexing of %s', brain.getURL(1))
        #except Exception, err:
            #from ZODB.POSException import POSKeyError
            #if type(err) != POSKeyError:
            #    import pdb; pdb.set_trace()

    info('INFO: Done reindexing')


def bulkReindexObjectsSecurity(context, brains, wf_id):
    """ Bulk reindex objects security using multi-transactions
    """
    total = len(brains)
    info('INFO: Start reindexing')
    info('INFO: reindexing %s brains', total)

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
                logger.info('INFO: Subtransaction committed to zodb (%s/%s)',
                            count, total)
                transaction.commit()
    else:
        info('ERROR: %s workflow not found', wf_id)

    info('INFO: Done reindexing')
