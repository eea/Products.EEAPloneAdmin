""" Ping SDS to update content and their aliases
"""
import logging
import transaction
from DateTime import DateTime
from zope.component import queryMultiAdapter

logger = logging.getLogger('eea.bulkping')

def ping_for_list(self, objects):
    """ get a list of objects and ping SDS to update the information
    """
    results_len = len(objects)
    index = 0
    logger.info(results_len)
    logger.info('------')
    request = getattr(self, 'REQUEST', None)
    ping_cr_view = queryMultiAdapter((self, request), name="ping_cr")
    for result in objects:
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

def ping_for_brains(self, brains):
    """ find aliases for given brains and pings the brains and aliases
        to update the information on the SDS
    """
    portalUrl = 'http://www.eea.europa.eu'
    results = []
    aliases = []
    for pub in brains:
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

    ping_for_list(self, brains)

def ping_all(self):
    """ find objects of a certain portal_type and their aliases and pings them
        to update the information on the SDS
    """
    request = getattr(self, 'REQUEST', None)
    meta_type = request.get('meta_type', None)
    if not meta_type:
        return

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

    ping_for_brains(self, pubs)