""" Upgrade steps for Products.EEAPloneAdmin
"""

from Products.CMFCore.utils import getToolByName


def add_workflow_properties(context):
    """ #135801 add workflow states and transitions where EffectiveDate is set
       if no value is set to the field
    """
    pprop = getToolByName(context, 'portal_properties')
    sprops = pprop.get('site_properties')
    sprops._setProperty('pub_date_set_on_workflow_transition_or_state',
                       'publish', 'lines')
