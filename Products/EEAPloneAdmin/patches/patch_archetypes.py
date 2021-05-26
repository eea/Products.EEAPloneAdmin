""" Archetypes
"""
import logging
import time
from zope.component import queryAdapter
from zope.annotation.interfaces import IAnnotations
from plone.uuid.interfaces import IUUID
logger = logging.getLogger("Products.EEAPloneAdmin")

def SearchableText(self):
    """ Cache SearchableText for long operations """
    start = time.time()
    uid = queryAdapter(self, IUUID, default='')
    key = "SearchableText-{uid}".format(uid=uid)
    request = getattr(self, 'REQUEST', None)
    cache = queryAdapter(request, IAnnotations, default={})
    data = cache.get(key, None)
    if data is None:
        data = self._old_SearchableText()
        end = time.time()
        delta = end - start
        # Cache calls longer than 2 seconds to speed up content creation,
        # especially content with PDF attached.
        # We don't cache operations faster than 2 seconds because this
        # can lead to incomplete data (file not attached yet)
        if delta > 2:
            cache[key] = data

    logger.debug("SearchableText called for key %s and it took %s seconds",
                key, time.time() - start)
    return data
