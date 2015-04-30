""" Custom PURGE policy
"""
from zope.interface import implements
from zope.component import adapts
from zope.component import getUtility
from zope.component import queryUtility
from plone.registry.interfaces import IRegistry
from z3c.caching.interfaces import IPurgePaths
from Products.CMFCore.interfaces import IDynamicType
from plone.app.caching.interfaces import IPloneCacheSettings
from Products.EEAPloneAdmin.interfaces import IEEACacheSettings

try:
    from plone.cachepurging.interfaces import IPurger
    from plone.cachepurging.interfaces import IPurgePathRewriter
    from plone.cachepurging.interfaces import ICachePurgingSettings
    PLONE_APP_CACHING_INSTALLED = True
except ImportError:
    PLONE_APP_CACHING_INSTALLED = False

import logging
logger = logging.getLogger("Products.EEAPloneAdmin")


class EEAContentPurgePaths(object):
    """ Paths to purge for content items to include the templates defined
        under 'Caching operations' on Site setup -> caching
    """
    implements(IPurgePaths)
    adapts(IDynamicType)

    def __init__(self, context):
        """ init
        """
        self.context = context

    def getRelativePaths(self):
        """ Get relative paths
        """
        prefix = self.context.absolute_url_path()
        portal_type = getattr(self.context, 'portal_type', None)

        self.registry = getUtility(IRegistry)
        self.ploneSettings = self.registry.forInterface(IPloneCacheSettings)

        contentTypeRulesetMapping = self.ploneSettings.contentTypeRulesetMapping
        templateRulesetMapping = self.ploneSettings.templateRulesetMapping

        ruleset = contentTypeRulesetMapping.get(portal_type)

        templates = []
        if ruleset:
            # Purge all custom templates
            templates.extend(templateRulesetMapping.keys())

            # Purge all scales
            image_scales = ['image_icon', 'image_tile', 'image_large',
                            'image_wide', 'image_preview', 'image_listing',
                            'image_thumb', 'image_mini']
            templates.extend(image_scales)

            # Purge eea.facetednavigation specific
            faceted_templates = ['faceted_counter', 'faceted_query',
                                 'tagscloud_counter']
            templates.extend(faceted_templates)

        for template in set(templates):
            yield prefix + '/' + template

    def getAbsolutePaths(self):
        """ Get absolute paths
        """
        return []


def _purge_handler(obj, event):
    """ Purge
    """
    registry = queryUtility(IRegistry)
    if registry:
        settings = registry.forInterface(ICachePurgingSettings, check=False)
        eeaSettings = registry.forInterface(IEEACacheSettings, check=False)
        contentTypeURLMapping = getattr(eeaSettings,
                                        "contentTypeURLMapping", {})

        if contentTypeURLMapping is None:
            return

        request = getattr(obj, 'REQUEST', None)
        if not request:
            logging.info('Purge failed: no request found for %s',
                         obj.absolute_url())
            return

        purger = getUtility(IPurger)
        rewriter = IPurgePathRewriter(request, None)
        caching_proxies = settings.cachingProxies

        to_purge = contentTypeURLMapping.get(obj.portal_type, [])

        if caching_proxies:
            for template_url in to_purge:
                paths_to_purge = rewriter(template_url)
                for path_to_purge in paths_to_purge:
                    for caching_proxy in caching_proxies:
                        full_path = '%s%s' % (caching_proxy, path_to_purge)
                        purger.purgeAsync(full_path)

def purge_handler(obj, event):
    """ Purge handler
    """
    if PLONE_APP_CACHING_INSTALLED:
        _purge_handler(obj, event)
        return
