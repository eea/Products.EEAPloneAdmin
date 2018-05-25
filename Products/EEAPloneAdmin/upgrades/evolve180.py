""" Cleanup Zope Versions Control
"""
import logging
from zope.component import getUtility
from plone.app.viewletmanager.interfaces import IViewletSettingsStorage

logger = logging.getLogger("Products.EEAPloneAdmin")

def cleanup_traceview(context):
    """ Cleanup traceview from viewletmanager
    """
    storage = getUtility(IViewletSettingsStorage)
    for skin, managers in storage._order.items():
        for manager, order in managers.items():
            if 'traceview.top' in order or 'traceview.buttom' in order:
                logger.warn(
                    "Cleanup traceview from viewlet storage: %s",
                    managers.pop(manager)
                )

