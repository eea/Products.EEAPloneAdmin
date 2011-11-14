""" Monkey patches for BaseRegistryTool
"""
from time import time
from Products.EEAPloneAdmin.browser.admin import save_resources_on_disk
from Products.CMFCore.utils import getToolByName

def generateId(self, *args, **kwargs):
    """ Better unique ids for js/css resources
    """
    now = "%.09f" % time()
    now = now.replace('.', '')
    return '%s%s%s' % (self.filename_base, now, self.filename_appendix)

def _initResources(self, node):
    """ Init Resources
    """
    self._old__initResources(node)
    registry = getToolByName(self.context, self.registry_id)
    save_resources_on_disk(registry)
