""" Event
"""
from Products.CMFCore.utils import getToolByName
from Products.EEAPloneAdmin.browser.admin import save_resources_on_disk
from DateTime import DateTime

def handle_resourceregistry_change(obj, event):
    """ Handle resource registry modification
    """
    portal_properties = getToolByName(obj, 'portal_properties')

    site_properties = portal_properties.get('site_properties')
    if not site_properties:
        if getattr(event, 'force', False):
            save_resources_on_disk(obj)
        return

    if not site_properties.getProperty('disableResourceDiskSaving'):
        if getattr(event, 'force', False):
            save_resources_on_disk(obj)

def handle_object_copied(obj, event):
    """ Handle object copy/paste
    """
    obj.creation_date = DateTime()


def handle_object_cloned(obj, event):
    """ Handle object pasted within the final destination
    """
    obj.setEffectiveDate()
