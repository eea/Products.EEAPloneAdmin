""" Cleanup Zope Versions Control
"""
import logging
from zope.component import queryMultiAdapter
from zope.component.hooks import getSite
logger = logging.getLogger("Products.EEAPloneAdmin")


def cleanup_catalogs(context):
    """ Add async jobs to cleanup catalogs daily
    """
    site = getSite()
    request = getattr(site, 'REQUEST', None)
    for catalog in site.objectValues(['ZCatalog', 'Plone Catalog Tool']):
        cleanup = queryMultiAdapter((catalog, request), name='cleanup')
        if cleanup:
            cleanup(async=True)
    return 'Done'


def sync_catalogs(context):
    """ Add async jobs to sync catalogs daily
    """
    site = getSite()
    request = getattr(site, 'REQUEST', None)
    for catalog in site.objectValues(['ZCatalog', 'Plone Catalog Tool']):
        sync = queryMultiAdapter((catalog, request), name='sync')
        if sync:
            sync(async=True)

    return 'Done'
