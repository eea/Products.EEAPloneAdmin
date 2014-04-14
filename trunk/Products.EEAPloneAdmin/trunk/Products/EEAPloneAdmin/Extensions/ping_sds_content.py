#Ping SDS to update content and their aliases

from DateTime import DateTime
from zope.component import queryMultiAdapter

def ping_all(self):
    """ find objects of a certain portal_type and their aliases and pings them
        to update the information on the SDS
    """

    request = getattr(self, 'REQUEST', None)
    meta_type = request.get('meta-type')

    ping_cr_view = queryMultiAdapter((self, request), name="ping_cr")
    now = DateTime()

    cat = self.portal_catalog
    pubs=cat.searchResults({ 'review_state': 'published',
                         'effectiveRange' : now,
                         'Language':'all',
                         'portal_type':meta_type,
                         'sort_on':'effective',
                         'sort_order':'reverse'})
    aliases = []
    for pub in pubs:
        local_view = pub.getObject().restrictedTraverse("@@manage-aliases")
        aliases += [x['redirect'] for x in local_view.redirects()]

    results = [pub.getURL() for pub in pubs] + aliases

    for result in results:
        ping_cr_view(result)
