""" MONKEY PATCH
 this should be fixed in ATContentTypes to take in consideration
 the case of zope3 view as default page. Also a fix should be
 done for Five.BrowserView in order to handle HEAD requests
 for all zope3 views.
"""

from webdav.Resource import Resource as WebdavResoure


def HEAD(self, REQUEST, RESPONSE):
    """ Patch Five.BrowserView to have a HEAD method just like other resources
    """
    return WebdavResoure.HEAD(self.context, REQUEST, RESPONSE)
