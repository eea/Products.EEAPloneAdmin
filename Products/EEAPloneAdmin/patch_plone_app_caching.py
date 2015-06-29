""" Patch for plone.app.caching
"""
import plone.app.caching.operations.utils
from plone.app.caching.operations.utils import formatDateTime, getExpiration
from Products.CMFDynamicViewFTI.interfaces import IBrowserDefault
from Products.CMFCore.interfaces import IDynamicType

# Do not remove this import as the tests will fail
from plone.app.caching.utils import getObjectDefaultView as godv


def doNotCache(published, request, response):
    """ Added extra `` no-store``, ``no-cache``, ``post-check``,
        ``pre-check`` and ``Pragma`` on headers
    """

    if response.getHeader('Last-Modified'):
        del response.headers['last-modified']

    response.setHeader('Expires', formatDateTime(getExpiration(0)))
    response.setHeader('Cache-Control',
                       'max-age=0, must-revalidate, no-store, no-cache, \
                       post-check=0, pre-check=0, private')
    response.setHeader('Pragma', 'no-cache')

def cacheInBrowser(published, request, response,
                   etag=None, lastModified=None):
    """ Added extra `` no-store``, ``no-cache``, ``post-check``,
        ``pre-check`` and ``Pragma`` on headers
    """

    if etag is not None:
        response.setHeader('ETag', '"%s"' %etag, literal=1)

    if lastModified is not None:
        response.setHeader('Last-Modified', formatDateTime(lastModified))
    elif response.getHeader('Last-Modified'):
        del response.headers['last-modified']

    response.setHeader('Expires', formatDateTime(getExpiration(0)))
    response.setHeader('Cache-Control',
                       'max-age=0, must-revalidate, no-store, no-cache, \
                        post-check=0, pre-check=0, private')
    response.setHeader('Pragma', 'no-cache')

def stripLeadingCharacters(name):
    """Strip off leading / and/or @@
    """
    if name and name[0] == '/':
        name = name[1:]
    if name and name.startswith('@@'):
        name = name[2:]
    return name

def getObjectDefaultView(context):
    """Get the id of an object's default view
    """

    # courtesy of Producs.CacheSetup

    browserDefault = IBrowserDefault(context, None)

    if browserDefault is not None:
        try:
            return stripLeadingCharacters(browserDefault.defaultView())
        except AttributeError:
            # Might happen if FTI didn't migrate yet.
            pass

    if not IDynamicType.providedBy(context):
        return None

    fti = context.getTypeInfo()
    try:
        # XXX: This isn't quite right since it assumes
        # the action starts with ${object_url}
        action = fti.getActionInfo('object/view')['url'].split('/')[-1]
    except ValueError:
        # If the action doesn't exist, stop
        return None

    # Try resolving method aliases because we need a real template_id here
    if action:
        action = fti.queryMethodID(action, default=action, context=context)
    else:
        action = fti.queryMethodID('(Default)', default=action, context=context)

    return stripLeadingCharacters(action)

plone.app.caching.operations.utils.doNotCache = doNotCache
plone.app.caching.operations.utils.cacheInBrowser = cacheInBrowser
plone.app.caching.utils.getObjectDefaultView = getObjectDefaultView

__all__ = [
    godv.__name__,
]
