from config import GLOBALS

from Products.GenericSetup import EXTENSION, BASE
from Products.GenericSetup import profile_registry

from Products.LinguaPlone import config
config.AUTO_NOTIFY_CANONICAL_UPDATE = 0

import setup

def initialize(context):


    profile_registry.registerProfile('default',
                                     'EEA WWW',
                                     'Extension profile for EEA Plone site.',
                                     'profiles/default',
                                     'EEAPloneAdmin',
                                     EXTENSION)


    profile_registry.registerProfile('local-site',
                                     'EEA local sites',
                                     'Extension profile to create and configure local sites.',
                                     'profiles/local-site',
                                     'EEAPloneAdmin',
                                     EXTENSION)

    profile_registry.registerProfile('optimize',
                                     'EEA WWW (CSS/JS reorder)',
                                     'Optimize order of CSS/JS for EEA website',
                                     'profiles/optimize',
                                     'EEAPloneAdmin',
                                     EXTENSION)


# MONKEY PATCH
# this is fixed in zope 2.10, but as we have 2.9 now we need this fix
# we need it because we use zope3 widgets which use the publisher
# and the zope2 and zope3 publishers differ somewhat
def getHeader(self, name):
    """ zope3 uses 'Content-Type' but in self.headers we have 'content-type'
        so we have to make sure we find it. """
    key = name.lower()
    return self.headers.get(key, None)

from ZPublisher.BaseResponse import BaseResponse
BaseResponse.getHeader = getHeader

# MONKEY PATCH
# this should be fixed in ATContentTypes to take in consideration
# the case of zope3 view as default page. Also a fix should be
# done for Five.BrowserView in order to handle HEAD requests
# for all zope3 views.
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

from Acquisition import aq_base
from webdav.Resource import Resource as WebdavResoure
from zope.component.interfaces import ComponentLookupError
from zope.component import getMultiAdapter
from Products.ATContentTypes.content.base import ATCTFolderMixin
ATCTFolderMixin.HEAD = HEAD

# MONKEY PATCH
# CMF Squid Tool patched to accept squid server list parameter not linked
# to formation of purge URLs. See more under #3728
import patch_cmfsquidtool

# MONKEY PATCH
# BaseRegistry patched to generate a better unique id for js/css resources
# See more under #3962
import patch_baseregistry

# MONKEY PATCH
# PloneLanguageTool patched to add 'Montenegrin' language
import patch_PloneLanguageTool

# MONKEY PATCH
# If parent has more then 50 children reorder will be restricted in order
# to avoid heavy wake up of objects. See more under #2803
from Products.CMFPlone.PloneTool import PloneTool
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.permissions import ModifyPortalContent
from Products.CMFPlone.utils import log

def reindexOnReorder(self, parent):
    """ Catalog ordering support """

    if len(parent.objectIds()) > 50:
        log('This context has more then 50 children and reorder is restricted. Path %s' %
            parent.absolute_url(1))
        return

    mtool = getToolByName(self, 'portal_membership')
    if not mtool.checkPermission(ModifyPortalContent, parent):
        return

    cat = getToolByName(self, 'portal_catalog')
    cataloged_objs = cat(path = {'query':'/'.join(parent.getPhysicalPath()),
                                 'depth': 1})
    for brain in cataloged_objs:
        obj = brain.getObject()
        # Don't crash when the catalog has contains a stale entry
        if obj is not None:
            cat.reindexObject(obj,['getObjPositionInParent'],
                                                update_metadata=0)
        else:
            # Perhaps we should remove the bad entry as well?
            log('Object in catalog no longer exists, cannot reindex: %s.'%
                                brain.getPath())

PloneTool.reindexOnReorder = reindexOnReorder
