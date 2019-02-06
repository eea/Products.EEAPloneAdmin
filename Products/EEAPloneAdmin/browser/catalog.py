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

    path = path.split('/')
    parent = getSite()

    if (aq_get(parent, 'REQUEST', None) is None and
            _GLOBALREQUEST_INSTALLED and _REQUESTCONTAINER_EXISTS):
        request = getRequest()
        request_container = RequestContainer(REQUEST=request)
        parent = aq_base(parent).__of__(request_container)
    return parent.unrestrictedTraverse(path)


#
# Sync Catalog UIDs from PATHs
#
def _syncFromPaths(context):
    """ Sync catalog from Paths """
    count = 0
    dcount = 0
    for rid, path in context._catalog.paths.iteritems():
        try:
            context._catalog.uids[path]
        except KeyError as err:
            context._catalog.uids[path] = rid
            count += 1

        try:
            context._catalog.data[rid]
        except KeyError as err:
            logger.warn("Missing data for rid: %s. Trying to fix it", err)
            dcount += 1
            try:
                obj = getObject(path=path)
                newDataRecord = context._catalog.recordify(obj)
            except Exception as derr:
                logger.exception(derr)
            else:
                context._catalog.data[rid] = newDataRecord

    msg = "Fixed broken uids: \t%s\t empty brain data: \t %s" % (count, dcount)
    logger.warn(msg)
    return msg


#
# Sync Catalog PATHs from UIDs
#
def _syncFromUids(context):
    """ Sync catalog from UIDS """
    count = 0
    dcount = 0
    for path, rid in context._catalog.uids.iteritems():
        try:
            context._catalog.paths[rid]
        except KeyError as err:
            context._catalog.paths[rid] = path
            count += 1

        try:
            context._catalog.data[rid]
        except KeyError as err:
            logger.warn("Missing data for rid: %s. Trying to fix it", err)
            dcount += 1
            try:
                obj = getObject(path=path)
                newDataRecord = context._catalog.recordify(obj)
            except Exception as derr:
                logger.exception(derr)
            else:
                context._catalog.data[rid] = newDataRecord

    msg = "Fixed broken paths: \t%s\t empty brain data: \t %s" % (count, dcount)
    logger.warn(msg)
    return msg


#
# Use this method to sync Catalog UIDs and Paths
#
def sync(context, run_async=True):
    """ Sync """
    logger.warn("Syncing _catalog uids / paths")
    msg = []
    msg.append(_syncFromUids(context))
    transaction.savepoint(optimistic=True)
    msg.append(_syncFromPaths(context))
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
            context
        )
    return "\n".join(msg)


#
# Cleanup broken brains
#
def cleanup(context, run_async=True):
    """ Cleanup broken brains
    """
    query = {'show_inactive': True}
    if 'Language' in context._catalog.indexes:
        query['Language'] = 'all'

    brains = context(**query)
    total = len(brains)
    paths = set()
    for index, brain in enumerate(brains):
        path = brain.getPath()
        if 'portal_factory' in path:
            paths.add(path)
            continue

        try:
            getObject(brain=brain)
        except Exception as err:
            paths.add(path)
        if index % 10000 == 0:
            logger.warn("Searching for orphan brains: %s/%s", index, total)

    count = len(paths)
    logger.warn("Orphan brains: %s", count)
    for path in paths:
        logger.warn("Removing orphan brain: %s", path)
        try:
            context._catalog.uncatalogObject(path)
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
            context
        )
    #
    # Return
    #
    return "Removed orphan brains: %s\n%s" % (
        count,
        "\n".join(paths)
    )


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
