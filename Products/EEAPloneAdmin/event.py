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
    ptype = obj.portal_type
    # skip changes for CallForInterest since the open and close
    # date properties of the object is populating the expiration
    # and publishing date
    if ptype == "CallForInterest" or ptype == "CallForTender":
        return
    if obj.effective_date:
        obj.setEffectiveDate('None')


def handle_workflow_change(obj, event):
    """ Handle object workflow change and remove effectiveDate
        if the review_state is no longer published
    """
    # 20827 remove effective date from object if review_state is
    # no longer published.
    # This event is triggered also when there is an object clone
    # after the object copied event and before the object is cloned
    # skip changes for CallForInterest since the open and close
    # date properties of the object is populating the expiration
    # and publishing date
    ptype = obj.portal_type
    if ptype == "CallForInterest" or ptype == "CallForTender":
        return
    review_state = event.status['review_state']
    # set effectiveDate to that of the EEAFigure for all EEAFigureFiles
    # when EEAFigure is published 20827
    if review_state == "published":
        parent_date = obj.effective_date
        if ptype == "EEAFigure":
            query = {'portal_type': 'EEAFigureFile'}
            cur_path = '/'.join(obj.getPhysicalPath())
            query['path'] = {'query': cur_path, 'depth': 1}
            figbrains = obj.portal_catalog(query)
            for brain in figbrains:
                figure = brain.getObject()
                figure.setEffectiveDate(parent_date)
    else:
        if obj.effective_date:
            obj.setEffectiveDate('None')


