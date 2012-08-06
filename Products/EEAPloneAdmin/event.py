""" Event
"""
from Products.EEAPloneAdmin.browser.admin import save_resources_on_disk
from DateTime import DateTime

def handle_resourceregistry_change(obj, event):
    """ Handle resource registry modification"""
    if getattr(event, 'force', False):
        save_resources_on_disk(obj)

def handle_object_copied(obj, event):
    """ Handle object copy/paste"""
    obj.creation_date = DateTime()
