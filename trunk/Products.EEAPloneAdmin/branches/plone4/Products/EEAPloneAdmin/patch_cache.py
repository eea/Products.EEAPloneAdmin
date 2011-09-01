""" Patch for plone.app.caching
"""

import plone.app.caching.operations.utils
from plone.app.caching.operations.utils import formatDateTime, getExpiration

def doNotCache(published, request, response):
    """ Added extra `` no-store``, ``no-cache``, ``post-check``,
        ``pre-check`` and ``Pragma`` on headers """
        
    if response.getHeader('Last-Modified'):
        del response.headers['last-modified']

    response.setHeader('Expires', formatDateTime(getExpiration(0)))
    response.setHeader('Cache-Control', 'max-age=0, must-revalidate, no-store, no-cache, post-check=0, pre-check=0, private')
    response.setHeader('Pragma', 'no-cache')
    
plone.app.caching.operations.utils.doNotCache = doNotCache

def cacheInBrowser(published, request, response, etag=None, lastModified=None):
    """ Added extra `` no-store``, ``no-cache``, ``post-check``,
        ``pre-check`` and ``Pragma`` on headers """
        
    if etag is not None:
        response.setHeader('ETag', '"%s"' %etag, literal=1)
        
    if lastModified is not None:
        response.setHeader('Last-Modified', formatDateTime(lastModified))
    elif response.getHeader('Last-Modified'):
        del response.headers['last-modified']
    
    response.setHeader('Expires', formatDateTime(getExpiration(0)))
    response.setHeader('Cache-Control', 'max-age=0, must-revalidate, no-store, no-cache, post-check=0, pre-check=0, private')
    response.setHeader('Pragma', 'no-cache')
    
plone.app.caching.operations.utils.cacheInBrowser = cacheInBrowser

