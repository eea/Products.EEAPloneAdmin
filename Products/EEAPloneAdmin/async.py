""" Async jobs
"""
import os
import datetime
import pytz
import logging
from zope.interface import Interface
from zope.component import queryUtility
from Products.GenericSetup.context import TarballExportContext
try:
    from plone.app.async.interfaces import IAsyncService
except ImportError:
    class IAsyncService(Interface):
        """ No async """

logger = logging.getLogger("Products.EEAPloneAdmin")
PATH = '/data/blobstorage/backup/profiles'


def _backup_profiles(context):
    """ Backup all profiles
    """
    steps = context.listExportSteps()
    result = TarballExportContext(context)
    marker = object()

    for step_id in steps:
        handler = context.getExportStep(step_id, marker)
        if handler is marker:
            continue

        if handler is not None:
            try:
                handler(result)
            except Exception as err:
                logger.exception(
                    "Could not backup profile step %s: %s", step_id, err)
                continue

    filename = result.getArchiveFilename()
    tarball = result.getArchive()

    if not os.path.isdir(PATH):
        os.makedirs(PATH)

    path = os.path.join(PATH, filename)
    with open(path, 'w') as ofile:
        ofile.write(tarball)

def backup_profiles(context):
    """ Backup all profiles asynchronousl
    """
    try:
        _backup_profiles(context)
    except Exception as err:
        logger.exception(err)

    async_service = queryUtility(IAsyncService)
    if async_service is None:
        logger.warn("Can't schedule profiles backup. "
                    "plone.app.async NOT installed!")
        return "Backup complete. Could not schedule new profiles backup."

    before = datetime.datetime.now(pytz.UTC)
    delay = before + datetime.timedelta(days=7)
    async_queue = async_service.getQueues()['']
    async_service.queueJobInQueueWithDelay(
        None, delay,
        async_queue, ('default',),
        backup_profiles, context
    )
    return "Backup complete. Scheduled new profiles backup for next week."
