""" Fix versionIds
"""
import transaction
import logging
from eea.versions.versions import assign_new_version_id

logger = logging.getLogger("EEAPloneAdmin.versionfix")


def fix_versionids(self):
    """ fix_versionids
    """
    catalog = self.portal_catalog
    brains = catalog.searchResults(missing=True, Language="all")

    i = 0
    for brain in brains:
        try:
            if not brain.getVersionId:
                obj = brain.getObject()
                assign_new_version_id(obj, event=None)
                obj.reindexObject(idxs=['getVersionId'])
                #print "reindexed", brain.getURL()
                #logger.debug("Fixed %s", brain.getURL())

            i += 1
            if i % 100 == 0:
                transaction.commit()
                print "savepoint at ", i
                #logger.info("Savepoint at %s", i)
        except Exception:
            print "Exception on ", brain.getURL()

    #logger.info("Done fixing versionids")
    print "done"
    return "Done"

