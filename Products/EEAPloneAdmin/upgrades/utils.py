""" Util scripts for upgrades
"""
import logging
import transaction
from zope.component import ComponentLookupError
from zope.component.interface import nameToInterface
from zope.interface import noLongerProvides


logger = logging.getLogger("Products.EEAPloneAdmin.upgrades")
info = logger.info
info_exception = logger.exception


def bulkReindexObjects(context, brains, idxs=None):
    """ Bulk reindex objects using multi-transactions """
    total = len(brains)
    info('INFO: Start reindexing')
    info('INFO: reindexing %s brains', total)
    inames = [
        "p4a.subtyper.interfaces.ISubtyped",
        "p4a.video.interfaces.IAnyVideoCapable",
        "p4a.video.interfaces.IPossibleVideoContainer",
        "p4a.video.interfaces.IPossibleVideo",
        "p4a.plonevideoembed.interfaces.IAnyVideoLinkCapable",
    ]
    ifaces = []
    for iname in inames:
        try:
             ifaces.append(nameToInterface(context, iname))
        except ComponentLookupError:
            info_exception('Cant find interface from %s name', iname)

    if idxs and type(idxs) == list:
        idxs.append('object_provides')

    for index, brain in enumerate(brains):
        try:
            obj = brain.getObject()
            if idxs:
                for iface in ifaces:
                    if iface.providedBy(obj):
                        noLongerProvides(obj, iface)
                obj.reindexObject(idxs=idxs)
            else:
                obj.reindexObject()
            if index % 100 == 0:
                transaction.commit()
                msg = 'INFO: Subtransaction committed to zodb (%s/%s)'
                info(msg, index, total)
        except Exception, err:
            info('ERROR: error during reindexing')
            info_exception('Exception: %s ', err)
    info('INFO: Done reindexing')
