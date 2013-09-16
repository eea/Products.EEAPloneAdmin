from eea.versions.versions import assign_new_version_id
import transaction
import logging

logger = logging.getLogger("EEAPloneAdmin.versionfix")

def fix_versionids(context):
    catalog = context.portal_catalog
    brains = catalog.searchResults(missing=True, Language="all")

    i = 0
    for brain in brains:
        if not brain.getVersionId:
            obj = brain.getObject()
            assign_new_version_id(obj, event=None)
            obj.reindexObject(idxs=['getVersionId'])
            logger.debug("Fixed %s", brain.getURL())

        i += 1
        if i % 100 == 0:
            transaction.savepoint()
            logger.info("Savepoint at %s", i)

    logger.info("Done fixing versionids")
    return "Done"

