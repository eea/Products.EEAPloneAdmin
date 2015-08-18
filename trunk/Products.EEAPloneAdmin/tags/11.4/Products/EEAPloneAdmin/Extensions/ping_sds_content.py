#Ping SDS to update content and their aliases

import logging
from DateTime import DateTime
from zope.component import queryMultiAdapter
import transaction

logger = logging.getLogger('eea.bulkping')

def ping_all(self):
    """ find objects of a certain portal_type and their aliases and pings them
        to update the information on the SDS
    """
    results = []
    portalUrl = 'http://www.eea.europa.eu'
    request = getattr(self, 'REQUEST', None)
    meta_type = request.get('meta_type', None)
    if not meta_type:
        return

    ping_cr_view = queryMultiAdapter((self, request), name="ping_cr")
    now = DateTime()

    cat = self.portal_catalog
    pubs = cat.searchResults({
        'review_state': 'published',
        'effectiveRange' : now,
        'Language': 'all',
        'portal_type': meta_type,
        'sort_on': 'effective',
        'sort_order': 'reverse'
    })

    aliases = []
    for pub in pubs:
        pub_url = ''
        obj = pub.getObject()
        local_view = obj.restrictedTraverse("@@manage-aliases")
        aliases += [x['redirect'] for x in local_view.redirects()]
        # Make proper URLs for objects
        obj_url = obj.absolute_url()
        if portalUrl in obj_url:
            pub_url = obj_url
        else:
            url_index = obj_url.find('/www/SITE/')
            if url_index != -1:
                pub_url = portalUrl + obj_url[url_index+9:]
            else:
                pub_url = portalUrl + obj_url[25:]
        results.append("%s/@@rdf" % pub_url)

    # Make proper URLs for aliases
    for alias in aliases:
        alias_url = ''
        if '/SITE/' in alias:
            alias_url = portalUrl + alias[9:]
        else:
            alias_url = portalUrl + alias[4:]
        results.append("%s/@@rdf" % alias_url)

    results_len = len(results)
    index = 0
    logger.info(results_len)
    logger.info('------')
    for result in results:
        index += 1
        try:
            ping_cr_view(result)
        except Exception:
            logger.error('Error: not able to ping')
            logger.info('Ping CR for: %s', result)
        if not index % 100:
            transaction.commit()
            logger.info('Progress %s/%s', index, results_len)

    logger.info('Done bulk ping.')
