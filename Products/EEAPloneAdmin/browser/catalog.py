""" Extend catalog functionallity
"""
import logging
import pytz
import transaction
from random import randint
from datetime import datetime, timedelta
from pkg_resources import DistributionNotFound
from pkg_resources import get_distribution
from zope.component import queryUtility
from zope.component.hooks import getSite
from zope.globalrequest import getRequest
from Acquisition import aq_base
from Acquisition import aq_get
from OFS.Uninstalled import BrokenClass
from Products.Five.browser import BrowserView
from plone.app.async.interfaces import IAsyncService

try:
    get_distribution('five.globalrequest')
except DistributionNotFound:
    _GLOBALREQUEST_INSTALLED = False
else:
    _GLOBALREQUEST_INSTALLED = True

try:
    from ZPublisher.BaseRequest import RequestContainer
except ImportError:
    # BBB: Zope 4 removes RequestContainer
    _REQUESTCONTAINER_EXISTS = False
else:
    _REQUESTCONTAINER_EXISTS = True

logger = logging.getLogger('EEAPloneAdmin')


#
# Get path by UID
#
def getPath(uid):
    """ Return path by given UID
    """
    site = getSite()
    catalog = getattr(site, 'uid_catalog', None)
    if not catalog:
        return None

    rids = catalog._catalog.indexes['UID']._index.get(uid, ())
    if isinstance(rids, int):
        rids = (rids, )

    for rid in rids:
        return catalog._catalog.paths[rid]
    return None


#
# Get object from ZCatalog brain or path
#
def getObject(brain=None, path=None):
    """Return the object for brain record

    Will return None if the object cannot be found via its cataloged path
    (i.e., it was deleted or moved without recataloging).

    This method mimicks a subset of what publisher's traversal does,
    so it allows access if the final object can be accessed even
    if intermediate objects cannot.
    """
    if brain is not None:
        path = brain.getPath()

    if not path:
        return None

    # Handle portal_factory
    if 'portal_factory' in path:
        return None

    # Handle relatedItems brains
    at_reference = None
    if '/at_references/' in path:
        path, at_reference = path.split('/at_references/')

    # Handle plone.app.discussion brains
    discussion = None
    if '/++conversation++default/' in path:
        path, discussion = path.split('/++conversation++default/')

    path = path.split('/')

    # Remove empty string from begining of the path
    if not path[0]:
        path = path[1:]

    if not path:
        return None

    # Remove site id from begining of the path
    parent = getSite()
    if path[0] == parent.getId():
        path = path[1:]

    if not path:
        return parent

    # Try to add REQUEST if not present
    if (aq_get(parent, 'REQUEST', None) is None and
            _GLOBALREQUEST_INSTALLED and _REQUESTCONTAINER_EXISTS):
        request = getRequest()
        if request is not None:
            request_container = RequestContainer(REQUEST=request)
            parent = aq_base(parent).__of__(request_container)

    obj = parent.unrestrictedTraverse(path)
    if isinstance(obj, BrokenClass):
        logger.warn('BrokenClass found at %s', path)
        return None

    # Handle relatedItems
    if at_reference is not None:
        at_references = getattr(obj, 'at_references', {})
        return at_references.get(at_reference, None)

    # Handle plone.app.discussion
    if discussion is not None:
        anno = getattr(obj, '__annotations__', {})
        discussions = anno.get('plone.app.discussion:conversation', {})
        return discussions.get(discussion, None)

    return obj


#
# Sync Catalog UIDs from PATHs
#
def _syncFromPaths(catalog):
    """ Sync catalog from Paths """
    count = 0
    dcount = 0
    for rid, path in catalog._catalog.paths.iteritems():
        try:
            catalog._catalog.uids[path]
        except KeyError as err:
            catalog._catalog.uids[path] = rid
            count += 1

        try:
            catalog._catalog.data[rid]
        except KeyError as err:
            logger.warn("Missing data for rid: %s. Trying to fix it", err)
            dcount += 1
            try:
                obj = getObject(path=path)
                newDataRecord = catalog._catalog.recordify(obj)
            except Exception as derr:
                logger.exception(derr)
            else:
                catalog._catalog.data[rid] = newDataRecord

    msg = "Fixed broken uids: \t%s\t empty brain data: \t %s" % (count, dcount)
    logger.warn(msg)
    return msg


#
# Sync Catalog PATHs from UIDs
#
def _syncFromUids(catalog):
    """ Sync catalog from UIDS """
    count = 0
    dcount = 0
    for path, rid in catalog._catalog.uids.iteritems():
        try:
            catalog._catalog.paths[rid]
        except KeyError as err:
            catalog._catalog.paths[rid] = path
            count += 1

        try:
            catalog._catalog.data[rid]
        except KeyError as err:
            logger.warn("Missing data for rid: %s. Trying to fix it", err)
            dcount += 1
            try:
                obj = getObject(path=path)
                newDataRecord = catalog._catalog.recordify(obj)
            except Exception as derr:
                logger.exception(derr)
            else:
                catalog._catalog.data[rid] = newDataRecord

    msg = "Fixed broken paths: \t%s\t empty brain data: \t %s" % (
        count, dcount)
    logger.warn(msg)
    return msg


#
# Use this method to sync Catalog UIDs and Paths
#
def sync(catalog, run_async=True):
    """ Sync """
    logger.warn("Syncing _catalog uids / paths")
    msg = []
    msg.append(_syncFromUids(catalog))
    transaction.savepoint(optimistic=True)
    msg.append(_syncFromPaths(catalog))
    #
    # Schedule new async job
    #
    if run_async:
        schedule = datetime.now(pytz.UTC).replace(
            hour=randint(0, 6), minute=randint(0, 59)) + timedelta(days=1)
        async = queryUtility(IAsyncService)
        queue = async.getQueues()['']
        async.queueJobInQueueWithDelay(
            None, schedule,
            queue, ('default',),
            sync,
            catalog
        )
    return "\n".join(msg)


#
# Cleanup broken brains
#
def cleanup(catalog, run_async=True):
    """ Cleanup broken brains
    """
    query = {}
    catalog_id = catalog.getId()
    if catalog_id != 'uid_catalog' and 'Language' in catalog._catalog.indexes:
        query['Language'] = 'all'

    brains = catalog(**query)
    total = len(brains)
    paths = set()
    count = 0
    for index, brain in enumerate(brains):
        if index % 10000 == 0:
            logger.warn("%s - Searching for orphan brains: %s/%s. Broken: %s",
                        catalog_id, index, total, count)

        path = brain.getPath()
        try:
            doc = getObject(brain=brain)
        except Exception as err:
            count += 1
            paths.add(path)
            continue
        # 107760 check if obj path is same of the brain path, if false remove
        # brain
        obj_path = '/' + doc.absolute_url(1)
        if not doc or obj_path != path:
            count += 1
            paths.add(path)
            continue

        # Also cleanup orphan references
        if catalog_id == 'reference_catalog':
            try:
                targetPath = getPath(brain.targetUID)
            except Exception:
                # Maybe uid_catalog is corrupted.
                # Avoid a reference_catalog massacre.
                continue
            else:
                if not targetPath:
                    continue

            try:
                doc = getObject(path=targetPath)
            except Exception as err:
                count += 1
                paths.add(path)
                continue

            if not doc:
                count += 1
                paths.add(path)

    logger.warn("%s - Found orphan brains: %s", catalog_id, count)
    for index, path in enumerate(paths):
        if index % 10000 == 0:
            logger.warn('%s - Removed orphan brains: %s/%s',
                        catalog_id, index, count)
            transaction.savepoint(optimistic=True)

        logger.warn("\t%s - Removing orphan brain: %s", catalog_id, path)
        try:
            catalog.uncatalog_object(path)
        except Exception as err:
            logger.exception(err)
    #
    # Schedule new async job
    #
    if run_async:
        schedule = datetime.now(pytz.UTC).replace(
            hour=randint(0, 6), minute=randint(0, 59)) + timedelta(days=1)
        async = queryUtility(IAsyncService)
        queue = async.getQueues()['']
        async.queueJobInQueueWithDelay(
            None, schedule,
            queue, ('default',),
            cleanup,
            catalog
        )
    #
    # Return
    #
    return "Removed orphan brains: %s" % (count)


class Catalog(BrowserView):
    """ Catalog utils
    """

    def cleanup(self, **kwargs):
        kwargs.update(self.request.form)
        run_async = kwargs.get('async', False)
        if not run_async:
            return cleanup(self.context, run_async=False)

        async = queryUtility(IAsyncService)
        queue = async.getQueues()['']
        async.queueJobInQueue(
            queue, ('default',),
            cleanup,
            self.context
        )

    def sync(self, **kwargs):
        kwargs.update(self.request.form)
        run_async = kwargs.get('async', False)
        if not run_async:
            return sync(self.context, run_async=False)

        async = queryUtility(IAsyncService)
        queue = async.getQueues()['']
        async.queueJobInQueue(
            queue, ('default',),
            sync,
            self.context
        )
