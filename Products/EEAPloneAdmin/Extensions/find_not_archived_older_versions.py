""" Find not archived older versions
"""
from Products.CMFCore.utils import getToolByName
from eea.versions.interfaces import IGetVersions
import logging

logger = logging.getLogger('EEAPloneAdmin.find_not_archived_older_versions')
info = logger.info
info_exception = logger.exception

def find_not_archived_versions(self, p_types=[]):
    """ Find not archived older versions and return a detailed report
    """
    info('Start searching for not archived older version!')

    versionable_interface = 'eea.versions.interfaces.IVersionEnhanced'
    cat = getToolByName(self, 'portal_catalog')
    result = []

    if p_types:
        brains = cat.unrestrictedSearchResults(
                        object_provides=versionable_interface,
                        portal_type=p_types)
    else:
        brains = cat.unrestrictedSearchResults(
                        object_provides=versionable_interface)
    info('Checking %s brains.', len(brains))

    count = 0
    count_not_expired = 0
    total = len(brains)

    for brain in brains:
        count += 1
        if (count % 500) == 0:
            info('PROCESSING: %s/%s', count, total)

        # expired, skip
        if brain.ExpirationDate != 'None':
            continue

        obj = brain.getObject()
        adapter = IGetVersions(obj)

        # latest version, skip
        if adapter.isLatest():
            continue

        # if latest published versions, skip        
        latest_versions = adapter.later_versions()
        latest_published = True
        for later_ver in latest_versions:
            if later_ver['review_state'] == 'published':
                latest_published = False
                break
        if latest_published:
            continue

        info('Old version not expired: %s', brain.getURL())
        result.append(brain.getURL())
        count_not_expired += 1

    info('Found %s not expired old versions', count_not_expired)
    info('Done searching for not archived older version!')
    return result
