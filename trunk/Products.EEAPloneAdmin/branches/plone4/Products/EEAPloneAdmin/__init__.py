#from Products.GenericSetup import EXTENSION #, BASE
#from Products.GenericSetup import profile_registry
#from config import GLOBALS
#from zExceptions import NotFound, MethodNotAllowed


#TODO: plone4 this is actually monkeypatching, should move to patches.zcml
from Products.LinguaPlone import config
config.AUTO_NOTIFY_CANONICAL_UPDATE = 0


## MONKEY PATCH
#TODO plone4: make sure the patch is not needed anymore
## this is fixed in zope 2.10, but as we have 2.9 now we need this fix
## we need it because we use zope3 widgets which use the publisher
## and the zope2 and zope3 publishers differ somewhat
#def getHeader(self, name):
    #""" zope3 uses 'Content-Type' but in self.headers we have 'content-type'
        #so we have to make sure we find it. """
    #key = name.lower()
    #return self.headers.get(key, None)

#from ZPublisher.BaseResponse import BaseResponse
#BaseResponse.getHeader = getHeader


## MONKEY PATCH
##plone4: is this patch still needed? Probably not
## this should be fixed in ATContentTypes to take in consideration
## the case of zope3 view as default page. Also a fix should be
## done for Five.BrowserView in order to handle HEAD requests
## for all zope3 views.
#def HEAD(self, REQUEST, RESPONSE):
    #"""Overwrite HEAD method for HTTP HEAD requests

    #Returns 404 Not Found if the default view can't be acquired or 405
    #Method not allowed if the default view has no HEAD method.

    #Added proxy HTTP HEAD requests for zope3 views.
    #"""
    #view_id = self.getDefaultPage() or self.getLayout()
    #view_method = getattr(self, view_id, None)
    #if view_method is None:
        #try:
            ## check if any zope3 view as default page
            #z3view = getMultiAdapter((self, REQUEST), name=view_id)
            #return WebdavResoure.HEAD(z3view.context, REQUEST, RESPONSE)
        #except ComponentLookupError:
            ## view method couldn't be acquired
            #raise NotFound, "View method %s for requested resource is not " \
                             #"available." % view_id
    #if getattr(aq_base(view_method), 'HEAD', None) is not None:
        ## view method has a HEAD method
        #return view_method.__of__(self).HEAD(REQUEST, RESPONSE)
    #else:
        #raise MethodNotAllowed, 'Method not supported for this resource.'

#from Acquisition import aq_base
#from webdav.Resource import Resource as WebdavResoure
#from zope.component.interfaces import ComponentLookupError
#from zope.component import getMultiAdapter
#from Products.ATContentTypes.content.base import ATCTFolderMixin
#ATCTFolderMixin.HEAD = HEAD

