""" MONKEY PATCH
 this should be fixed in ATContentTypes to take in consideration
 the case of zope3 view as default page. Also a fix should be
 done for Five.BrowserView in order to handle HEAD requests
 for all zope3 views.
"""

from zExceptions import NotFound, MethodNotAllowed
from Acquisition import aq_base
from webdav.Resource import Resource as WebdavResoure
from zope.component.interfaces import ComponentLookupError
from zope.component import getMultiAdapter

def HEAD(self, REQUEST, RESPONSE):
    """Overwrite HEAD method for HTTP HEAD requests

    Returns 404 Not Found if the default view can't be acquired or 405
    Method not allowed if the default view has no HEAD method.

    Added proxy HTTP HEAD requests for zope3 views.
    """
    view_id = self.getDefaultPage() or self.getLayout()
    view_method = getattr(self, view_id, None)
    if view_method is None:
        try:
            # check if any zope3 view as default page
            z3view = getMultiAdapter((self, REQUEST), name=view_id)
            return WebdavResoure.HEAD(z3view.context, REQUEST, RESPONSE)
        except ComponentLookupError:
            # view method couldn't be acquired
            raise NotFound, "View method %s for requested resource is not " \
                             "available." % view_id
    if getattr(aq_base(view_method), 'HEAD', None) is not None:
        # view method has a HEAD method
        return view_method.__of__(self).HEAD(REQUEST, RESPONSE)
    else:
        raise MethodNotAllowed, 'Method not supported for this resource.'


