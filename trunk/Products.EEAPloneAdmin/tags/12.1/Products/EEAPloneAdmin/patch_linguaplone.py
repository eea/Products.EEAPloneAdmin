""" Lingua Plone
"""
from archetypes.schemaextender import extender

def clearSchemaCache(context):
    """ Clear
    """
    if hasattr(context.REQUEST, extender.CACHE_KEY):
        delattr(context.REQUEST, extender.CACHE_KEY)


def _patched_getFieldsToCopy(self, *args, **kwargs):
    """ Fields to copy
    """
    clearSchemaCache(self.context)
    return self._old_getFieldsToCopy(*args, **kwargs)
