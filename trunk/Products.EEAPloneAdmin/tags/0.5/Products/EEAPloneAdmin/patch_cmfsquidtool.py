import sys
import httplib
import urlparse
import Queue

from Products.CMFSquidTool.utils import (
    Queue,
    Worker,
    logger,
    Producer,
    pruneAsync,
    pruneUrl,
    _producer
)

from Products.CMFSquidTool import utils
from Products.CMFSquidTool import config
from Products.CMFSquidTool import queue
from Products.CMFSquidTool.queue import in_commit

from Products.CMFSquidTool.queue import Queue as CMFQueue
from Products.CMFSquidTool.SquidTool import SquidTool
from Products.CMFCore.utils import getToolByName


############

USE_HTTP_1_1_PURGE = False
config.USE_HTTP_1_1_PURGE = USE_HTTP_1_1_PURGE

############

def computePurgeUrlsEEA(self, ob_urls):
    res = []
    for ob_url in ob_urls:
        ob_url = self.rewriteUrl(ob_url)
        res.append(ob_url)
    return res

SquidTool.computePurgeUrls = computePurgeUrlsEEA

############

def runEEA(self):
    logger.debug("%s starting", self)
    # Queue should always exist!
    q = self.producer.queues[(self.host, self.scheme)]
    connection = None
    try:
        while not self.stopping:
            item = q.get()
            if self.stopping or item is None: # Shut down thread signal
                logger.debug('Stopping worker thread for '
                             '(%s, %s).' % (self.host, self.scheme))
                break
            url, purge_type = item

            # Loop handling errors (other than connection errors) doing
            # the actual purge.
            for i in range(5):
                if self.stopping:
                    break
                # Get a connection.
                if connection is None:
                    connection = self.getConnection('%s://%s' % (self.scheme, self.host))
                    if connection is None: # stopping
                        break
                # Got an item, prune it!
                try:
                    resp, msg, err = self.producer._pruneUrl(connection,
                                                             url, purge_type)
                    # worked! See if we can leave the connection open for
                    # the next item we need to process
                    # NOTE: If we make a HTTP 1.0 request to IIS, it
                    # returns a HTTP 1.1 request and closes the
                    # connection.  It is not clear if IIS is evil for
                    # not returning a "connection: close" header in this
                    # case (ie, assuming HTTP 1.0 close semantics), or
                    # if httplib.py is evil for not detecting this
                    # situation and flagging will_close.
                    if not USE_HTTP_1_1_PURGE or resp.will_close:
                        connection.close()
                        connection = None
                    break # all done with this item!

                except (httplib.HTTPException, socket.error), e:
                    # All errors 'connection' related errors are treated
                    # the same - simply drop the connection and retry.
                    # the process for establishing the connection handles
                    # other bad things that go wrong.
                    logger.debug('Transient failure on %s for %s, '
                                 're-establishing connection and '
                                 'retrying: %s' % (purge_type, url, e))
                    connection.close()
                    connection = None
                except:
                    # All other exceptions are evil - we just disard the
                    # item.  This prevents other logic failures etc being
                    # retried.
                    connection.close()
                    connection = None
                    logger.exception('Failed to purge %s', url)
                    break
    except:
        logger.exception('Exception in worker thread '
                         'for (%s, %s)' % (self.host, self.scheme))
    logger.debug("%s terminating", self)

Worker.run = runEEA

############

def getQueueAndWorkerEEA(self, url, squid_url):
    (scheme, host, path, params, query, fragment) = urlparse.urlparse(squid_url)
    key = (host, scheme)
    if key not in self.queues:
        self.queue_lock.acquire()
        try:
            if key not in self.queues:
                logger.debug("Creating worker thread for %s://%s",
                             scheme, host)
                assert key not in self.workers
                self.queues[key] = queue = Queue.Queue(self.backlog)
                self.workers[key] = worker = Worker(queue, host, scheme, self)
                worker.start()
        finally:
            self.queue_lock.release()
    return self.queues[key], self.workers[key]

Producer.getQueueAndWorker = getQueueAndWorkerEEA

############

def pruneAsyncEEA(self, url, purge_type='PURGE', daemon=True, squid_url=''):
    (scheme, host, path, params, query, fragment) = urlparse.urlparse(url)
    __traceback_info__ = (url, purge_type, scheme, host,
                          path, params, query, fragment)

    q, w = self.getQueueAndWorker(url, squid_url)
    try:
        q.put((url, purge_type), block=False)
        msg = 'Queued %s' % url
    except Queue.Full:
        # Make a loud noise.  Ideally the queue size would be
        # user-configurable - but the more likely case is that the purge
        # host is down.

        # Warning commented as ends up in too much noise on logs

        #logger.warning("The purge queue for the URL %s is full - the "
        #               "request will be discarded.  Please check the "
        #               "server is reachable, or disable this purge host",
        #               url)

        msg = "Purge queue full for %s" % url
    return msg

Producer.pruneAsync = pruneAsyncEEA

############

def pruneUrlEEA(self, url, purge_type='PURGE', squid_url=''):
    # A synchronous one targetted at the ZMI.  - just lets exceptions happen, no retry
    # semantics, etc
    logger.debug("Starting synchronous purge of %s", url)
    try:
        conn = self.getConnection(squid_url)
        try:
            resp, xcache, xerror = self._pruneUrl(conn, url, purge_type)
            status = resp.status
        finally:
            conn.close()
    except:
        status = "ERROR"
        err, msg, tb = sys.exc_info()
        try:
            from zExceptions.ExceptionFormatter import format_exception
        except ImportError:
            from traceback import format_exception
        xerror = '\n'.join(format_exception(err, msg, tb))
        # Avoid leaking a ref to traceback.
        del err, msg, tb
        xcache = ''
    logger.debug('Finished %s for %s: %s %s'
                 % (purge_type, url, status, xcache))
    if xerror:
        logger.debug('Error while purging %s:\n%s' % (url, xerror))
    logger.debug("Completed synchronous purge of %s", url)
    return status, xcache, xerror

Producer.pruneUrl = pruneUrlEEA
utils._producer = Producer()
utils.pruneUrl = utils._producer.pruneUrl
utils.pruneAsync = utils._producer.pruneAsync

############

def _finishEEA(self):
    # Process any pending url invalidations. This should *never*
    # fail.
    for url in self.urls():
        for squid_url in self._squid_urls:
            utils.pruneAsync(url, 'PURGE', True, squid_url)
    # Empty urls queue for this thread
    self._reset()

CMFQueue._finish = _finishEEA

############

def queueEEA(self, ob):
    st = getToolByName(ob, 'portal_squid', None)
    if st is None:
        return
    ob_urls = st.getUrlsToPurge(ob)
    self._squid_urls = st.squid_urls
    purge_urls = st.computePurgeUrls(ob_urls)
    commiting = in_commit()
    for ob_url in purge_urls:
        if commiting:
            for squid_url in st.squid_urls:
                utils.pruneAsync(ob_url, 'PURGE', True, squid_url)
        else:
            self.append(ob_url)

CMFQueue.queue = queueEEA
queue.queue = CMFQueue()

############

def pruneUrlsEEA(self, ob_urls=None, purge_type="PURGE", REQUEST=None):
    # ob_url is a relative to portal url

    results = []
    purge_urls = self.squid_urls
    if ob_urls:
        purge_urls = self.computePurgeUrls(ob_urls)

    for url in purge_urls:
        # If a response was given, we do it synchronously and write the
        # results to the response.  Otherwise we just queue it up.
        for squid_url in self.squid_urls:
            if REQUEST:
                status, xcache, xerror = utils.pruneUrl(url, purge_type, squid_url)

                # NOTE: if the purge was successfull status will be 200 (OK)
                #       if the object was not in cache status is 404 (NOT FOUND)
                #       if you are not allowed to PURGE status is 403
                REQUEST.RESPONSE.write('%s\t%s\t%s\n' % (status, url, xerror or xcache))
            else:
                utils.pruneAsync(url, purge_type, daemon=True, squid_url=squid_url)
                status = "Queued"
                xcache = xerror = ""
            results.append((status, xcache, xerror))

    return results

SquidTool.pruneUrls = pruneUrlsEEA

