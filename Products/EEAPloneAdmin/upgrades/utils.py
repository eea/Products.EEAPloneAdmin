""" Util scripts for upgrades
"""
import logging
import transaction


logger = logging.getLogger("Products.EEAPloneAdmin.upgrades")
info = logger.info
info_exception = logger.exception


def bulkReindexObjects(context, brains, idxs=[]):
    """ Bulk reindex objects using multi-transactions """
    total = len(brains)
    info('INFO: Start reindexing')
    info('INFO: reindexing %s brains', total)
    for index, brain in enumerate(brains):
        try:
            obj = brain.getObject()
            if idxs:
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
