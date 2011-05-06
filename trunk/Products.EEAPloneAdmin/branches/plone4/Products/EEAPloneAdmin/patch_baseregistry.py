""" Monkey patches for BaseRegistryTool
"""
from time import time

def generateId(self, *args, **kwargs):
    """ Better unique ids for js/css resources
    """
    now = "%.09f" % time()
    now = now.replace('.', '')
    return '%s%s%s' % (self.filename_base, now, self.filename_appendix)
