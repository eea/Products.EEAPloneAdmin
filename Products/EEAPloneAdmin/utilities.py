""" Utilities
"""
import logging
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
        site = getSite()
        handler = getToolByName(site, "portal_historyidhandler")
        count = 0
        for hid in self.portal_types:
            working = handler.unrestrictedQueryObject(hid)
            if working is not None:
                continue

            self._purge(hid)
            count += 1

            if count % 100 == 0:
                logger.info("ZVCleanup removed %s", count)

    def cleanup_portal_type(self, portal_type):
        """ Purge history for given Portal Type
        """
        count = 0
        for hid, ptype in self.portal_types.items():
            if ptype != portal_type:
                continue

            self._purge(hid)
            count += 1

            if count % 100 == 0:
                logger.info("ZVCleanup portal_type %s: %s", portal_type, count)
