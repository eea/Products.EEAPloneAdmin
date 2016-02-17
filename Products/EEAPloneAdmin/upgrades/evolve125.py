""" RSS2 changes
"""
import logging
import transaction
logger = logging.getLogger('Products.EEAPloneAdmin')


def remove_rss2_for_eea(context):
    """ Cleanup RSS2 for EEA option
    """
    logger.info('Cleanup RSS2 for EEA option')
    registry = context.portal_registry
    registry['Products.CMFPlone.interfaces.syndication.'
             'ISiteSyndicationSettings.allowed_feed_types'] = (
        u'rss.xml|RSS 2.0', u'atom.xml|Atom', u'itunes.xml|iTunes',
        u'RSS|RSS 1.0')

    logger.info("Removed RSS2 for EEA from portal_registry")
    transaction.commit()


def modify_rss2_condition(context):
    """ Modify RSS2 url expression and condition
    """
    portal_actions = context.portal_actions
    document_actions = portal_actions.document_actions
    rss2 = document_actions.rss2
    rss2.url_expr = "string:$object_url/rss.xml"
    rss2.available_expr = "object/@@syndication-util/context_enabled"
    transaction.commit()
