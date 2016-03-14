""" Monkey patches for BaseRegistryTool
"""
from time import time
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent

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
    event = ObjectModifiedEvent(self)
    event.force = True
    notify(event)

