from Products.CMFPlone.utils import getToolByName
from StringIO import StringIO
import transaction


def getOrganisationByUrl(catalog, url):
    """ get Organisation by given url
    """

    brains = catalog.searchResults({
        'portal_type' : 'Organisation',
        'getUrl': url
    })

    if brains:
        return brains[0].getObject()


def fix_externaldataspecs(self):
    """fix external data specs
    """
    catalog = getToolByName(self, 'portal_catalog')
    brains = catalog.searchResults(portal_type="ExternalDataSpec")

    i = 0
    fixed = []

    for brain in brains:
        obj = brain.getObject()
        val = obj.getProvider_url()
        if isinstance(val, (tuple, list)):
            if len(val):
                obj.setProvider_url(val[0])
            else:
                obj.setProvider_url(None)

            obj.reindexObject()
            i += 1
            if i % 10 == 0:
                transaction.savepoint()

            fixed.append(obj)

    out = StringIO()

    for o in fixed:
        url = o.getProvider_url()
        name = o.getProvider_name()

        print >> out, "Fixed ExternalDataSpec at %s w/ provider_url to %s. "\
                      "Organisation name (the provider_name field) is %s" % \
                        (o.absolute_url(), url, name)
        org = getOrganisationByUrl(catalog, url)
        if org:
            print >> out, "The following organisation exists for " \
                          "that url: %s > %s" % (org.absolute_url(), 
                                                 org.Title())
        else:
            print >> out, "There is no organisation for that url"
        
    out.seek(0)

    return out.read()
