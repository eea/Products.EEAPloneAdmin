""" Helper methods to debug and fix catalog
"""
import logging
import transaction
logger = logging.getLogger('EEAPloneAdmin')


#
# Start a debugger on your catalog
#
def debug(self):
    """ Debug """
    import pdb; pdb.set_trace()
    return 'Done'


#
# Sync Catalog UIDs from PATHs
#
def _syncFromPaths(self):
    """ Sync catalog from Paths """
    count = 0
    dcount = 0
    for rid, path in self._catalog.paths.iteritems():
        try:
            self._catalog.uids[path]
        except KeyError as err:
            self._catalog.uids[path] = rid
            count += 1

        try:
            self._catalog.data[rid]
        except KeyError as err:
            logger.warn("Missing data for rid: %s. Trying to fix it", err)
            dcount += 1
            try:
                obj = self.www.unrestrictedTraverse(path)
                newDataRecord = self._catalog.recordify(obj)
            except Exception as derr:
                logger.exception(derr)
            else:
                self._catalog.data[rid] = newDataRecord

    msg = "Fixed broken uids: \t%s\t empty brain data: \t %s" % (count, dcount)
    logger.warn(msg)
    return msg


#
# Sync Catalog PATHs from UIDs
#
def _syncFromUids(self):
    """ Sync catalog from UIDS """
    count = 0
    dcount = 0
    for path, rid in self._catalog.uids.iteritems():
        try:
            self._catalog.paths[rid]
        except KeyError as err:
            self._catalog.paths[rid] = path
            count += 1

        try:
            self._catalog.data[rid]
        except KeyError as err:
            logger.warn("Missing data for rid: %s. Trying to fix it", err)
            dcount += 1
            try:
                obj = self.www.unrestrictedTraverse(path)
                newDataRecord = self._catalog.recordify(obj)
            except Exception as derr:
                logger.exception(derr)
            else:
                self._catalog.data[rid] = newDataRecord

    msg = "Fixed broken paths: \t%s\t empty brain data: \t %s" % (count, dcount)
    logger.warn(msg)
    return msg


#
# Use this method to sync Catalog UIDs and Paths
#
def sync(self):
    """ Sync """
    logger.warn("Syncing _catalog uids / paths")
    msg = []
    msg.append(_syncFromUids(self))
    transaction.savepoint(optimistic=True)
    msg.append(_syncFromPaths(self))
    return "\n".join(msg)


def cleanup_key(self, key):
    """ Unindex orphan key from catalog indexes """
    if not isinstance(key, int):
        key = int(key)

    path = self._catalog.paths.get(key)
    data = self._catalog.data.get(key)
    uid = [(k, v) for k, v in self._catalog.uids.iteritems() if v == key]

    if path or data or uid:
        return ("Can't remove valid "
                "key {key}, path: {path}, data: {data}, uid: {uid}".format(
            key=key, path=path, data=data, uid=uid))

    path = '/www/dummy-cleanup-brain'
    self._catalog.paths[key] = path
    self._catalog.uids[path] = key
    self._catalog.data[key] = ()
    self._catalog._length.change(1)
    self._catalog.uncatalogObject(path)
