import logging
import transaction
logger = logging.getLogger('EEAPloneAdmin')

#
# Start a debugger on your catalog
#
def debug(self):
    import pdb; pdb.set_trace()
    return 'Done'

#
# Remove rid from catalog indexes
#
def _unindexObject(catalog, rid):
    indexes = catalog.indexes.keys()
    for name in indexes:
        x = catalog.getIndex(name)
        if hasattr(x, 'unindex_object'):
            try:
                x.unindex_object(rid)
            except Exception as err:
                logger.debug(err)

#
# Helper method to avoid errors like:
#    RuntimeError: the bucket being iterated changed size
#
def iterbatch(iset, steps=1):
    length = len(iset)
    batches = range(0, length, steps)
    if steps > 1 and length % steps != 0:
        batches += [length,]

    start = 0
    for end in batches:
        if end == 0:
            continue
        try:
            for key, val in iset.items()[start:end]:
                yield (key, val)
        except Exception as err:
            logger.warn("Skipping inconsistent items between %s and %s", start, end)
            logger.exception(err)
        start = end

#
# Sync Catalog UIDs from PATHs
#
def _syncFromPaths(self):
    paths = self._catalog.paths
    uids = self._catalog.uids
    data = self._catalog.data

    count = 0
    dcount = 0

    res = iterbatch(paths)
    for rid, path in res:
        try:
            uids[path]
        except KeyError as err:
            uids[path] = rid
            count += 1

        try:
            data[rid]
        except KeyError as err:
            logger.warn("Missing data for rid %s:", err)
            data[rid] = ()
            dcount += 1

    msg = "Fixed broken uids: \t %s \t empty brain data: \t %s" % (count, dcount)
    logger.warn(msg)
    return msg

#
# Sync Catalog PATHs from UIDs
#
def _syncFromUids(self):
    paths = self._catalog.paths
    uids = self._catalog.uids
    data = self._catalog.data

    count = 0
    dcount = 0

    res = iterbatch(uids)
    for path, rid in res:
        try:
            paths[rid]
        except KeyError as err:
            paths[rid] = path
            count += 1

        try:
            data[rid]
        except KeyError as err:
            logger.warn("Missing data for rid: %s", err)
            data[rid] = ()
            dcount += 1

    msg = "Fixed broken paths: \t %s \t empty brain data: \t %s" % (count, dcount)
    logger.warn(msg)
    return msg

#
# Uncatalog orphan brains
#
def _cleanupIndexes(self):
    if self.meta_type == "Plone Catalog Tool":
        brains = self(Language='all')
    else:
        brains = self()

    count = 0
    dcount = 0
    for brain in brains:
        rid = brain.getRID()
        try:
            self._catalog.paths[rid]
        except Exception as err:
            logger.warn(err)
            count += 1
            try:
                data = self._catalog.data[rid]
            except Exception as e:
                logger.debug(e)
                dcount += 1
            else:
                logger.warn(data)
            _unindexObject(self._catalog, rid)

    msg = "Un-indexed broken brains: \t %s \t missing brain metadata: \t %s" % (count, dcount)
    logger.warn(msg)
    return msg

#
# Use this method to sync Catalog UIDs and Paths
#
def sync(self):
    logger.warn("Syncing from UIDS")
    msg = []
    msg.append(_syncFromUids(self))
    transaction.savepoint(optimistic=True)
    msg.append(_syncFromPaths(self))
    return "\n".join(msg)

#
# Sync and Cleanup catalog
#
def cleanup(self):
    logger.warn("Full catalog cleanup started: %s", self)
    msg = []
    msg.append(_syncFromPaths(self))
    transaction.savepoint(optimistic=True)
    msg.append(_syncFromUids(self))
    transaction.savepoint(optimistic=True)
    msg.append(_cleanupIndexes(self))
    return "\n".join(msg)

#
# Reindex missing catalog brains metadata
#
def reindexData(self):
    data = self._catalog.data
    count = 0
    broken = 0
    for rid, val in data.items():
        if val:
            continue

        try:
            path = self._catalog.paths[rid]
            obj = self.www.unrestrictedTraverse(path)
            newDataRecord = self._catalog.recordify(obj)
        except Exception, err:
            logger.exception(err)
            broken += 1
        else:
            count += 1
            logger.warn("New data record for %s: %s", rid, newDataRecord)
            data[rid] = newDataRecord
    return "Fixed %s data records. Still broken: %s" % (count, broken)


#
# Uncomment following lines if you know what you're doing.
# Never run it directly on production. I didn't run it at all :)
#

# from BTrees.OIBTree import OIBTree
# from BTrees.IOBTree import IOBTree
# import BTrees.Length

#def _rebuildUIDS(self):
#    uids = OIBTree()
#    self._length = BTrees.Length.Length()
#    logger.warn("Rebuilding catalog uids: %s", self)
#    count = 0
#    for key, val in iterbatch(self._catalog.uids):
#        uids[key] = val
#        self._length.change(1)
#        count += 1
#
#    self.uids = uids
#    msg = "Rebuilded %s catalog uids" % count
#    logger.warn(msg)
#    return msg
#
#
#def _rebuildPaths(self):
#    paths = IOBTree()
#    logger.warn("Rebuilding catalog paths: %s", self)
#    count = 0
#    for key, val in iterbatch(self._catalog.paths):
#        paths[key] = val
#        count += 1
#
#    self.paths = paths
#    msg = "Rebuilded %s catalog paths" % count
#    logger.warn(msg)
#    return msg
#
#
#def rebuild(self):
#    logger.warn("Rebuilding catalog started: %s", self)
#    msg = []
#    msg.append(_rebuildPaths(self))
#    transaction.savepoint()
#    msg.append(_rebuildUIDS(self))
#
#    return "\n".join(msg)
#
