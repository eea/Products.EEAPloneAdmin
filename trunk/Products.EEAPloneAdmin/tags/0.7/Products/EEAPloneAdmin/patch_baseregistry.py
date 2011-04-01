""" Monkey patches for BaseRegistryTool
"""
from time import time
from Products.ResourceRegistries.tools.BaseRegistry import BaseRegistryTool
from collective.monkey.monkey import Patcher

def generateId(self, *args, **kwargs):
    """ Better unique ids for js/css resources
    """
    now = "%.09f" % time()
    now = now.replace('.', '')
    return '%s%s%s' % (self.filename_base, now, self.filename_appendix)

ToolPatcher = Patcher('EEA')
ToolPatcher.wrap_method(BaseRegistryTool, 'generateId', generateId)
