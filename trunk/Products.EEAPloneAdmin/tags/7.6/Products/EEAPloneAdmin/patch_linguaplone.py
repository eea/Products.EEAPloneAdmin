from archetypes.schemaextender import extender


def clearSchemaCache(context):
    if hasattr(context.REQUEST, extender.CACHE_KEY):
        delattr(context.REQUEST, extender.CACHE_KEY)


def _patched_getFieldsToCopy(self, *args, **kwargs):
    clearSchemaCache(self.context)
    return self._old_getFieldsToCopy(*args, **kwargs)
