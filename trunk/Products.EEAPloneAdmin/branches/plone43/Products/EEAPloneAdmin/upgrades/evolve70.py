""" Upgrade to version 7.0
"""
import logging
import transaction
from Products.CMFCore.utils import getToolByName
from zope.component import getUtility
from plone.registry.interfaces import IRegistry
from Products.CMFPlone.interfaces.syndication import ISyndicatable
from Products.CMFPlone.interfaces.syndication import (
    ISiteSyndicationSettings, IFeedSettings)
from Products.ZCTextIndex.interfaces import IZCTextIndex


logger = logging.getLogger("Products.EEAPloneAdmin.upgrades")
info = logger.info
info_exception = logger.exception


def enable_rss2(context):
    """ Enable the new-style RSS2 feed #14323
    """
    portal = getToolByName(context, 'portal_url').getPortalObject()
    catalog = getToolByName(portal, 'portal_catalog')
    at_tool = getToolByName(portal, 'archetype_tool')

    logger.info('Enabling new RSS2')

    registry = getUtility(IRegistry)
    synd_settings = registry.forInterface(ISiteSyndicationSettings)

    custom_rss2 = u'RSS2|RSS 2.0 EEA'
    current_allowed = synd_settings.allowed_feed_types
    if custom_rss2 not in current_allowed:
        new_allowed = current_allowed + (custom_rss2, )
        new_allowed = tuple(unicode(x) for x in new_allowed)
        synd_settings.allowed_feed_types = new_allowed

    logger.info('Adding RSS2 to allowed views')

    folder_types = set([])
    for _type in at_tool.listPortalTypesWithInterfaces([ISyndicatable]):
        folder_types.add(_type.getId())
    folder_types = folder_types
    for brain in catalog(portal_type=tuple(folder_types)):
        obj = brain.getObject()
        try:
            settings = IFeedSettings(obj)
        except TypeError:
            continue
        if settings.enabled:
            current_feeds = list(settings.feed_types)
            new_feeds = [u'RSS2']
            current_feeds.extend(new_feeds)
            settings.feed_types = tuple(set(current_feeds))
            message = 'Enabling RSS2 for %s' % brain.getURL()
            logger.info(message)


def bulkReindexObjects(self, brains, idxs=[]):
    """ Bulk reindex objects using multi-transactions """
    total = len(brains)
    info('INFO: Start reindexing')
    info('INFO: reindexing %s brains', total)
    for index, brain in enumerate(brains):
        try:
            obj = brain.getObject()
            if idxs:
                obj.reindexObject(idxs=idxs)
            else:
                obj.reindexObject()
            if index % 100 == 0:
                transaction.commit()
                info('INFO: Subtransaction committed to zodb (%s/%s)', index, total)
        except Exception, err:
            info('ERROR: error during reindexing')
            info_exception('Exception: %s ', err)
    info('INFO: Done reindexing')


def reindexZCTextIndex(context):
    portal = getToolByName(context, 'portal_url').getPortalObject()
    catalog = getToolByName(portal, 'portal_catalog')
    query = {'Language': 'all'}
    brains = catalog(**query)
    indexes = catalog.Indexes.objectValues()
    idxs = []
    for index in indexes:
        if IZCTextIndex.providedBy(index):
            idxs.append(index.getId())

    bulkReindexObjects(context, brains, idxs)
