""" Extend catalog functionallity
"""
import logging
import transaction
from datetime import datetime, timedelta
from zope.component import queryUtility
from Products.Five.browser import BrowserView
from plone.app.async.interfaces import IAsyncService
logger = logging.getLogger('EEAPloneAdmin')


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
                obj = context.www.unrestrictedTraverse(path)
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
                obj = context.www.unrestrictedTraverse(path)
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
    # Schedule new async cleanup job
    #
    if run_async:
        schedule = datetime.now().replace(hour=23, minute=55) + timedelta(days=1)
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
    cleanup = set()
    for index, brain in enumerate(brains):
        path = brain.getPath()
        if 'portal_factory' in path:
            cleanup.add(path)
            continue

        try:
            brain.getObject()
        except Exception as err:
            cleanup.add(path)
        if index % 10000 == 0:
            logger.warn("Searching for orphan brains: %s/%s", index, total)

    count = len(cleanup)
    logger.warn("Orphan brains: %s", count)
    for path in cleanup:
        logger.warn("Removing orphan brain: %s", path)
        try:
            context._catalog.uncatalogObject(path)
        except Exception as err:
            logger.exception(err)
    #
    # Schedule new async cleanup job
    #
    if run_async:
        schedule = datetime.now().replace(hour=23, minute=5) + timedelta(days=1)
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
        "\n".join(cleanup)
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
