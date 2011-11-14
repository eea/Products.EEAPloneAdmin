""" Monkey patches for BaseRegistryTool
"""

from Products.EEAPloneAdmin.browser.admin import save_resources_on_disk
from Products.ResourceRegistries.tools.BaseRegistry import BaseRegistryTool
from Products.ResourceRegistries.exportimport.resourceregistry import \
        ResourceRegistryNodeAdapter
from collective.monkey.monkey import Patcher
from time import time
from Products.CMFCore.utils import getToolByName


def generateId(self, *args, **kwargs):
    """ Better unique ids for js/css resources
    """
    now = "%.09f" % time()
    now = now.replace('.', '')
    return '%s%s%s' % (self.filename_base, now, self.filename_appendix)

ToolPatcher = Patcher('EEA')
ToolPatcher.wrap_method(BaseRegistryTool, 'generateId', generateId)


def _initResources(self, node):
    self._old__initResources(node)
    registry = getToolByName(self.context, self.registry_id)
    save_resources_on_disk(registry)

ResourceRegistryNodeAdapter._old__initResources = \
        ResourceRegistryNodeAdapter._initResources
ToolPatcher.wrap_method(ResourceRegistryNodeAdapter, '_initResources', 
                        _initResources)

