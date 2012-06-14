""" Monkey patches for BaseRegistryTool
"""

from time import time
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent

#from Products.CMFCore.utils import getToolByName
#from Products.EEAPloneAdmin.browser.admin import save_resources_on_disk


def generateId(self, *args, **kwargs):
    """ Better unique ids for js/css resources
    """
    now = "%.09f" % time()
    now = now.replace('.', '')
    return '%s%s%s' % (self.filename_base, now, self.filename_appendix)


def patch_cookResources(self):
    """Patch for cookResources to trigger the ObjectModifiedEvent
    """
    self._old_cookResources()
    notify(ObjectModifiedEvent(self))


#def _initResources(self, node):
    #""" Init Resources
    #"""
    #registry = getToolByName(self.context, self.registry_id)
    #self._old__initResources(node)
    #save_resources_on_disk(registry)

