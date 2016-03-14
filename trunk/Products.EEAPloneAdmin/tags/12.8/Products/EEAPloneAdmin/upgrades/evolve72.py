""" Upgrade steps for 7.2
"""

import logging
from Products.CMFCore.utils import getToolByName
from zope.component import getUtility
from plone.registry.interfaces import IRegistry
from Products.CMFPlone.interfaces.syndication import ISyndicatable
from Products.CMFPlone.interfaces.syndication import (
    ISiteSyndicationSettings, IFeedSettings)
from Products.ZCTextIndex.interfaces import IZCTextIndex
from Products.EEAPloneAdmin.upgrades import utils
import transaction

logger = logging.getLogger("Products.EEAPloneAdmin.upgrades")

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
    index = 0
    for brain in catalog(portal_type=tuple(folder_types), Language='all'):
        obj = brain.getObject()
        try:
            settings = IFeedSettings(obj)
        except TypeError:
            continue
        if settings.enabled:
            current_feeds = list(settings.feed_types)
            if u'RSS2' in current_feeds:
                continue
            new_feeds = [u'RSS2']
            current_feeds.extend(new_feeds)
            settings.feed_types = tuple(set(current_feeds))
            message = 'Enabling RSS2 for %s' % brain.getURL()
            logger.info(message)
        if index % 100 == 0:
            transaction.commit()
            logger.info('Transaction commited')
        index += 1
    logger.info('Done enable RSS2')


def reindexZCTextIndex(context):
    """ Reindex ZCTextIndex
    """
    portal = getToolByName(context, 'portal_url').getPortalObject()
    catalog = getToolByName(portal, 'portal_catalog')
    query = {'Language': 'all'}
    brains = catalog(**query)
    indexes = catalog.Indexes.objectValues()
    idxs = []
    for index in indexes:
        if IZCTextIndex.providedBy(index):
            idxs.append(index.getId())

    utils.bulkReindexObjects(context, brains, idxs)

def cleanupBrokenP4AObjects(self):
    """ uncatalog broken p4a objects
    """
    catalog = self.portal_catalog
    objs = ['/www/portal_factory/HelpCenter/rdfstype/faq',
            '/www/portal_factory/HelpCenter/rdfstype/how-to',
            '/www/portal_factory/HelpCenter/rdfstype/tutorial',
            '/www/portal_factory/HelpCenter/rdfstype/manual',
            '/www/portal_factory/HelpCenter/rdfstype/error',
            '/www/portal_factory/HelpCenter/rdfstype/link',
            '/www/portal_factory/HelpCenter/rdfstype/glossary']
    for obj in objs:
        catalog.uncatalog_object(obj)
    return "DONE with removal of %s" % objs

