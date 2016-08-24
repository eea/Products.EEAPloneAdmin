""" Utilities
"""
import logging
import transaction
from eventlet.timeout import Timeout
from zope.interface import implementer
from zope.component.hooks import getSite
from Products.CMFCore.utils import getToolByName
from Products.CMFEditions.ZVCStorageTool import Removed
from Products.EEAPloneAdmin.upgrades.history import PORTAL_TYPES
from Products.EEAPloneAdmin.interfaces import IZVCleanup
logger = logging.getLogger('Products.EEAPloneAdmin')


@implementer(IZVCleanup)
class ZVCleanup(object):
    """ Zope Version Control Cleanup utility
    """
    _portal_types = {}
    _removed_items = set()
    _storage = None

    @property
    def storage(self):
        """ History storage
        """
        if self._storage is None:
            site = getSite()
            self._storage = getToolByName(site, 'portal_historiesstorage')
        return self._storage

    @property
    def portal_types(self):
        """ Mapping between history id and portal_type
        """
        if self._portal_types:
            return self._portal_types

        shadow = self.storage._getShadowStorage()
        histIds = shadow._storage

        self._portal_types = dict(PORTAL_TYPES.items())
        for hid in histIds.keys():
            if hid in self._portal_types:
                continue

            with Timeout(10):
                ob = self.storage.retrieve(hid).object.object

            if not ob:
                logger.warn("Timeout raised for history id: %s", hid)
                continue

            if isinstance(ob, Removed):
                continue

            ptype = ob.getPortalTypeName()
            logger.warn("Adding hid - portal_type mapping: %s = %s", hid, ptype)
            self._portal_types[hid] = ptype

        return self._portal_types

    @property
    def removed_items(self):
        """ Get history ids for removed items
        """
        if self._removed_items:
            return self._removed_items

        site = getSite()
        handler = getToolByName(site, "portal_historyidhandler")

        length = len(self.portal_types)
        for count, hid in enumerate(self.portal_types):
            working = handler.unrestrictedQueryObject(hid)
            if working is not None:
                continue
            self._removed_items.add(hid)

            if count % 100 == 0:
                logger.warn(
                    "ZVCleanup: Finding removed items %s/%s", count, length)

        return self._removed_items

    def _purge(self, hid):
        """Purge all versions """
        while True:
            length = len(self.storage.getHistory(hid, countPurged=False))
            if length <= 0:
                break

            self.storage.purge(hid, 0,  metadata={'sys_metadata': {
                'comment': "Products.EEAPloneAdmin.upgrades:evolve140"}
            }, countPurged=False)

    def cleanup_removed(self):
        """ Purge history for removed items
        """
        logger.warn("ZVCleanup history for removed items STARTED!!!")

        length = len(self.removed_items)
        for count, hid in enumerate(self.removed_items):
            self._purge(hid)
            if count % 100 == 0:
                logger.warn(
                    "ZVCleanup history for removed items: %s/%s", count, length)

        logger.warn(
            "ZVCleanup: Cleaned-up history for %s removed items", length)

    def cleanup_portal_type(self, portal_type):
        """ Purge history for given Portal Type
        """
        logger.warn(
            "ZVCleanup history for portal_type %s STARTED!!!", portal_type)

        count = 0
        for hid, ptype in self.portal_types.items():
            if ptype != portal_type:
                continue

            self._purge(hid)
            count += 1

            if count % 100 == 0:
                logger.warn("ZVCleanup portal_type %s: %s", portal_type, count)
        logger.warn("ZVCleanup portal_type %s: Cleaned-up history for %s items",
                    portal_type, count)

    def cleanup_attributes(self, portal_type=None, *attributes):
        """ Clear large object attributes within history
        """
        zvc_repo = self.storage._getZVCRepo()

        logger.warn(
            "ZVCleanup history attributes %s for portal_type %s STARTED!!!",
            attributes, portal_type)

        count = 0
        for hid, ptype in self.portal_types.items():
            if portal_type and ptype != portal_type:
                continue

            zvc_hid, _vers = self.storage._getZVCAccessInfo(hid, None, True)
            zvc_history = zvc_repo.getVersionHistory(zvc_hid)
            versions = getattr(zvc_history, '_versions', {})
            length = len(versions)

            count += 1
            logger.warn("%s. ZVCleanup attributes: history_id %s, versions %s",
                        count, hid, length)

            for vid in versions:
                version = zvc_history.getVersionById(vid)
                data = version._data

                ob = data.getWrappedObject()
                ob = getattr(ob, 'object', None)
                if ob is None:
                    continue

                for attribute in attributes:
                    val = getattr(ob, attribute, None)
                    if not val:
                        continue

                    if isinstance(val, dict):
                        val.clear()
                        ob._p_changed = True
                        continue

                    if attribute == '__annotations__':
                        val.clear()
                        ob._p_changed = True
                        continue

                    delattr(ob, attribute)

            transaction.commit()

        logger.warn("ZVCleanup attributes %s for portal_type %s: "
                    "Cleaned-up history for %s items",
                    attributes, portal_type, count)
