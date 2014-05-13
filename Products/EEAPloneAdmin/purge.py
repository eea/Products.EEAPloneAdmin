""" Custom PURGE policy
"""
from zope.interface import implements
from zope.component import adapts
from zope.component import getUtility
from plone.registry.interfaces import IRegistry
from z3c.caching.interfaces import IPurgePaths
from Products.CMFCore.interfaces import IDynamicType
from plone.app.caching.interfaces import IPloneCacheSettings
from Products.EEAPloneAdmin.interfaces import IEEACacheSettings

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
        self.eeaSettings = self.registry.forInterface(IEEACacheSettings)

        contentTypeRulesetMapping = self.ploneSettings.contentTypeRulesetMapping
        contentTypeURLMapping = getattr(self.eeaSettings, "contentTypeURLMapping", {})
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

            for url in contentTypeURLMapping.get(portal_type, []):
                yield url

        for template in set(templates):
            yield prefix + '/' + template

    def getAbsolutePaths(self):
        """ Get absolute paths
        """
        return []
