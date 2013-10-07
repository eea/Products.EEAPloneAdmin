""" Util scripts for upgrades
"""
import logging
import transaction
from zope.component import ComponentLookupError
from zope.component.interface import nameToInterface
from zope.interface import noLongerProvides
HAS_Subtyper = True
try:
    from p4a.subtyper.interfaces import ISubtyped
except ImportError:
    HAS_Subtyper = False
from ZODB.POSException import POSKeyError


logger = logging.getLogger("Products.EEAPloneAdmin.upgrades")
info = logger.info
info_exception = logger.exception


def bulkReindexObjects(context, brains, idxs=None):
    """ Bulk reindex objects using multi-transactions """
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

    if idxs and type(idxs) == list:
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
        except Exception, err:
            info('ERROR: error during reindexing of %s', brain.getURL(1))
            if type(err) != POSKeyError:
                import pdb; pdb.set_trace()
    info('INFO: Done reindexing')
