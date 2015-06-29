""" The problem with translated emtpy folders
    is that they appeared in the site map confusing the users,
    it is better to cancel all of them
"""

import logging
import transaction
from plone.app.linkintegrity.exceptions import \
    LinkIntegrityNotificationException
from plone.app.linkintegrity.interfaces import ILinkIntegrityInfo
from StringIO import StringIO

logger = logging.getLogger("Delete empty folder: ")
info = logger.info
info_exception = logger.exception

def clean_folder(self):
    """ find folders that are empty and delete them
        the loop run recursively until there is no more
        folders to cancel
    """
    catalog = self.portal_catalog
    total = 0
    transaction_threshold = 20

    # var for infinite loop
    empty_count = 42

    # Start information log
    info("START")
    out = StringIO()

    forced_delete = []

    while empty_count != 0:

        # Secure infinite loop
        empty_count = 0

        # Get all folders
        folders = catalog.unrestrictedSearchResults({
                                    'portal_type': ('ATFolder', 'Folder')
                                    })

        # Find empty folders and delete them
        for folder in folders:
            obj = folder._unrestrictedGetObject()
            if len(obj.getFolderContents()) == 0:
                empty_count += 1
                total += 1
                refs = obj.getBRefs(relationship='isReferencing')
                try:
                    obj.aq_parent.manage_delObjects([folder.id])
                except LinkIntegrityNotificationException:
                    li = ILinkIntegrityInfo(self.REQUEST)
                    self.REQUEST.environ['link_integrity_info'] = \
                        li.encodeConfirmedItems([obj])
                    forced_delete.append((obj.absolute_url(), refs))

                info(obj.absolute_url())

                # Commiting transaction
                if empty_count % transaction_threshold == 0:
                    info("Commit: delete %s folders", transaction_threshold)
                    transaction.savepoint()

    # End information log
    info("COMPLETE, %s folders deleted", total)
    print >> out, ("The following linkintegrity conflicts were encountered:")
    print >> out, ("The conflicting objects have been deleted, "
                   "but the referencing pages should be updated.")

    for failed, referencing in forced_delete:
        print >> out, "This object failed reference integrity: ", failed
        print >> out, "It was referenced by:"
        for r in referencing:
            print >> out, r.absolute_url()

    print >> out, "Total objects deleted %s" % total
    out.seek(0)

    return out.read()
