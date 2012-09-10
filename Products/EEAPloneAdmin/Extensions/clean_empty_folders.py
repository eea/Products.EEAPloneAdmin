""" The problem with translated emtpy folders
is that they appeared in the site map confusing the users, 
it is better to cancel all of them
"""

import logging
import transaction
from zope.component import queryUtility
from Products.CMFCore.interfaces import IPropertiesTool

# Log info 
logger = logging.getLogger("Delete empty folder: ")
info = logger.info
info_exception = logger.exception

def clean_folder(self):
    """find folders that are empty and delete them
       the loop run recursively until there is no more 
       folders to cancel
    """

    # We need to disable link integrity check to avoid the 
    # LinkIntegrityNotificationException error if folders 
    # have a link pointing to them
    ptool = queryUtility(IPropertiesTool)
    props = getattr(ptool, 'site_properties', None)
    old_check = props.getProperty('enable_link_integrity_checks', False)
    props.enable_link_integrity_checks = False
    
    catalog = self.portal_catalog
    total = 0
    transaction_threshold = 20

    # var for infinite loop
    empty_count = 42 

    # Start information log
    info("START")

    while empty_count != 0:

        # Secure infinite loop
        empty_count = 0 

        # Get all folders 
        folders = catalog.unrestrictedSearchResults({
                                    'portal_type': ('ATFolder', 'Folder')
                                    })

        # Find empty folders and delete them
        for folder in folders:
            obj =  folder._unrestrictedGetObject()
            if len(obj.getFolderContents()) == 0:
                empty_count += 1
                total += 1
                obj.aq_parent.manage_delObjects([folder.id])
                info(obj.absolute_url())

                # Commiting transaction
                if empty_count % transaction_threshold == 0:
                    info("Commit: delete %s folders" % transaction_threshold)
                    transaction.commit()

    # End information log
    info("COMPLETE, %s folders deleted" % total)

    # We put back the link integrity check
    props.enable_link_integrity_checks = old_check

    return total

