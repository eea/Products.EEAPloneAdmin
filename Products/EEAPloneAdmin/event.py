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
    if obj.effective_date:
        obj.setEffectiveDate()


def handle_workflow_change(obj, event):
    """ Handle object workflow change and remove effectiveDate
        if the review_state is no longer published
    """
    # 20827 remove effective date from object if review_state is
    # no longer published.
    # This event is triggered also when there is an object clone
    # after the object copied event and before the object is cloned
    uid = obj.UID()
    if not uid:
        pass
    review_state = event.status['review_state']
    if review_state != "published":
        if obj.effective_date:
            obj.setEffectiveDate()


