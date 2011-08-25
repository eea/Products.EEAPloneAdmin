""" Custom PURGE policy
"""
from zope.interface import implements
from zope.component import adapts
from zope.component import getUtility
from plone.registry.interfaces import IRegistry
from z3c.caching.interfaces import IPurgePaths
from Products.CMFCore.interfaces import IDynamicType
from plone.app.caching.interfaces import IPloneCacheSettings

class EEAContentPurgePaths(object):
    """ Paths to purge for content items to include the templates defined
        under 'Caching operations' on Site setup -> caching
    """
    implements(IPurgePaths)
    adapts(IDynamicType)

    def __init__(self, context):
        """ init """
        self.context = context

    def getRelativePaths(self):
        """ Get relative paths """
        prefix = self.context.absolute_url_path()
        portal_type = getattr(self.context, 'portal_type', None)

        self.registry = getUtility(IRegistry)
        self.ploneSettings = self.registry.forInterface(IPloneCacheSettings)
        
        contentTypeRulesetMapping = self.ploneSettings.contentTypeRulesetMapping
        templateRulesetMapping = self.ploneSettings.templateRulesetMapping
        
        ruleset = contentTypeRulesetMapping.get(portal_type)
        
        if ruleset:
            templates = []
            for tpl, rlst in templateRulesetMapping.items():
                if rlst == ruleset:
                    templates.append(tpl)
        
        for template in templates:
            yield prefix + '/' + template

    def getAbsolutePaths(self):
        """ get absolute paths """
        return []
