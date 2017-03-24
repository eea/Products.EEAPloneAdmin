""" Helper methods to debug catalog """
import logging
import transaction
# from BTrees.OIBTree import OIBTree
# from BTrees.IOBTree import IOBTree
# import BTrees.Length
# from pprint import pformat
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

# #
# # Remove rid from catalog indexes
# #
# def _unindexObject(catalog, rid):
#     indexes = catalog.indexes.keys()
#     for name in indexes:
#         x = catalog.getIndex(name)
#         if hasattr(x, 'unindex_object'):
#             try:
#                 x.unindex_object(rid)
#             except Exception as err:
#                 logger.debug(err)

# #
# # Helper method to avoid errors like:
# #    RuntimeError: the bucket being iterated changed size
# #
# def iterbatch(iset, steps=1):
#     length = len(iset)
#     batches = range(0, length, steps)
#     if steps > 1 and length % steps != 0:
#         batches += [length,]
#
#     start = 0
#     for end in batches:
#         if end == 0:
#             continue
#         try:
#             for key, val in iset.items()[start:end]:
#                 yield (key, val)
#         except Exception as err:
#              logger.warn(
#                  "Skipping inconsistent items between %s and %s", start, end)
#             logger.exception(err)
#         start = end

# #
# # Uncatalog orphan brains
# #
# def _cleanupIndexes(self):
#     if self.meta_type == "Plone Catalog Tool":
#         brains = self(Language='all')
#     else:
#         brains = self()
#
#     count = 0
#     dcount = 0
#     for brain in brains:
#         rid = brain.getRID()
#         try:
#             self._catalog.paths[rid]
#         except Exception as err:
#             logger.warn(err)
#             count += 1
#             try:
#                 data = self._catalog.data[rid]
#             except Exception as e:
#                 logger.debug(e)
#                 dcount += 1
#             else:
#                 logger.warn(data)
#             _unindexObject(self._catalog, rid)
#
#     msg = ("Un-indexed broken brains: "
#            "\t %s \t missing brain metadata: \t %s" % (count, dcount))
#     logger.warn(msg)
#     return msg



# #
# # Sync and Cleanup catalog
# #
# def cleanup(self):
#     logger.warn("Full catalog cleanup started: %s", self)
#     msg = []
#     msg.append(_syncFromPaths(self))
#     transaction.savepoint(optimistic=True)
#     msg.append(_syncFromUids(self))
#     transaction.savepoint(optimistic=True)
#     msg.append(_cleanupIndexes(self))
#     return "\n".join(msg)

# #
# # Reindex missing catalog brains metadata
# #
# def reindexData(self):
#     data = self._catalog.data
#     count = 0
#     broken = 0
#     for rid, val in data.items():
#         if val:
#             continue
#
#         try:
#             path = self._catalog.paths[rid]
#             obj = self.www.unrestrictedTraverse(path)
#             newDataRecord = self._catalog.recordify(obj)
#         except Exception, err:
#             logger.exception(err)
#             broken += 1
#         else:
#             count += 1
#             logger.warn("New data record for %s: %s", rid, newDataRecord)
#             data[rid] = newDataRecord
#     return "Fixed %s data records. Still broken: %s" % (count, broken)

# #
# # Re-sync catalog
# #
# def _cleanupDuplicates(self, duplicates, items):
#     for rid, path in duplicates.items():
#         logger.warn("Removing duplicate record from catalog %s %s", rid, path)
#         erid = items[path]
#         self._catalog.data[erid] = ()
#         self._catalog.uncatalogObject(path)
#         self._catalog._length.change(1)
#         self._catalog.uids[path] = rid
#         self._catalog.paths[rid] = path
#         self._catalog.data[rid] = ()
#         self._catalog.uncatalogObject(path)
#         obj = self.www.unrestrictedTraverse(path, None)
#         if obj:
#             logger.warn("Re-indexing obj at %s", path)
#             self._catalog.catalogObject(obj, path)
#
# def reSyncCatalog(self):
#     if len(self._catalog.paths) == len(self._catalog.uids):
#         logger.warn("Catalog in-sync. Nothing to do.")
#         return "Catalog in-sync. Nothing to do."
#
#     items = {}
#     duplicates = {}
#     for rid, path in self._catalog.paths.iteritems():
#         if path not in items:
#             items[path] = rid
#             continue
#
#         erid = items[path]
#         if rid != erid:
#             logger.warn(
#  'PATHS: Duplicate path %s but not rid %s. Existing rid: %s', path, rid, erid)
#             duplicates[rid] = path
#
#     for path, rid in iterbatch(self._catalog.uids):
#         if path not in items:
#             items[path] = rid
#             continue
#
#         erid = items[path]
#         if rid != erid:
#             duplicates[rid] = path
#             logger.warn(
#  'UIDS: Duplicate path %s but not rid %s. Existing rid: %s', path, rid, erid)
#
#     self._catalog.uids = OIBTree()
#     self._catalog.paths = IOBTree()
#     self._catalog._length = BTrees.Length.Length()
#     for path, rid in items.items():
#         self._catalog._length.change(1)
#         self._catalog.uids[path] = rid
#         self._catalog.paths[rid] = path
#
#     msg = "Fixed %s paths. Duplicates %s" % (len(items), pformat(duplicates))
#     logger.warn(msg)
#     transaction.savepoint()
#     _cleanupDuplicates(self, duplicates, items)
#     return msg

# def brokenBrains(self):
#     if self.meta_type == "Plone Catalog Tool":
#         brains = self(Language='all')
#     else:
#         brains = self()
#
#     count = 0
#     total = len(brains)
#     broken = {}
#     logger.info(
#               "%s: Finding broken brains within %s total brains", self, total)
#     for idx, brain in enumerate(brains):
#         try:
#             obj = brain.getObject()
#         except Exception as err:
#             logger.exception(err)
#             obj = None
#
#         if not obj:
#             try:
#                 rid = brain.getRID()
#                 path = brain.getURL()
#             except Exception as err:
#                 logger.exception(err)
#             else:
#                 logger.info('Orphan brain\t%s\t%s', rid, path)
#                 count += 1
#                 broken[path] = rid
#
#         if idx % 1000 == 0:
#             logger.info("Progress %s/%s", idx, total)
#
#     logger.info('Found %s orphan brains', count)
#     return pformat(broken)
#
# def fixEmptyData(self):
#     data = self._catalog.data
#     empty = set()
#     for rid, val in self._catalog.data.iteritems():
#         if not val:
#             empty.add(rid)
#
#     logger.warn("Found %s empty data", len(empty))
#     count = 0
#     fixed = set()
#     for rid in empty:
#         path = self._catalog.paths.get(rid)
#         if not path:
#             logger.warn("No path found for rid %s", rid)
#             continue
#
#         erid = self._catalog.uids.get(path)
#         if not erid:
#             logger.warn("No rid found within uids for path %s", path)
#             continue
#
#         if erid != rid:
#             logger.warn("Rid %s not in sync: %s", rid, erid)
#             continue
#
#         obj = self.www.unrestrictedTraverse(path, None)
#         if not obj:
#             continue
#
#         logger.warn('Fixing data for %s', path)
#         self._catalog.catalogObject(obj, path)
#         fixed.add(path)
#         count += 1
#
#     logger.warn("Fixed %s metadata", count)
#     return "\n".join(fixed)
#
# def cleanPortalFactoryBrains(self):
#     if self.meta_type == "Plone Catalog Tool":
#         brains = self(Language='all')
#     else:
#         brains = self()
#
#     broken = set()
#     logger.warn("Cleanup portal_factory brains started on catalog %s", self)
#     count = 0
#     for brain in brains:
#         rid = brain.getRID()
#         try:
#             path = self._catalog.paths[rid]
#         except Exception as err:
#             logger.exception(err)
#             continue
#
#         if 'portal_factory' in path:
#             broken.add(path)
#
#     for path in broken:
#         logger.warn('%s', path)
#         self._catalog.uncatalogObject(path)
#         count += 1
#
#     logger.warn('Unindexed %s portal_factory brains', count)
#     return '\n'.join(broken)
