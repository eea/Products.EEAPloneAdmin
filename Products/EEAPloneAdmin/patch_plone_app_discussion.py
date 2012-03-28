""" Patch plone.app.discussion ver 2.0.10, not to fail on migrate
    workflows when "Discussion Item" has no workflow assigned
"""
import plone.app.discussion.browser.controlpanel
from Products.CMFCore.utils import getToolByName
from zope.app.component.hooks import getSite
from plone.registry.interfaces import IRecordModifiedEvent
from plone.app.controlpanel.interfaces import IConfigurationChangedEvent
from zope.component import queryUtility
from plone.app.discussion.interfaces import IDiscussionSettings
from plone.registry.interfaces import IRegistry

def notify_configuration_changed(event):
    """Event subscriber that is called every time the configuration changed.
    """
    portal = getSite()
    wftool = getToolByName(portal, 'portal_workflow', None)

    if IRecordModifiedEvent.providedBy(event):
        # Discussion control panel setting changed
        if event.record.fieldName == 'moderation_enabled':
            # Moderation enabled has changed
            if event.record.value == True:
                # Enable moderation workflow
                wftool.setChainForPortalTypes(('Discussion Item',),
                                              'comment_review_workflow')
            else:
                # Disable moderation workflow
                wftool.setChainForPortalTypes(('Discussion Item',),
                                              'one_state_workflow')

    if IConfigurationChangedEvent.providedBy(event):
        # Types control panel setting changed
        if 'workflow' in event.data:
            registry = queryUtility(IRegistry)
            settings = registry.forInterface(IDiscussionSettings, check=False)

            # Patch
            wf = wftool.getChainForPortalType('Discussion Item')
            if wf:
                if wf[0] == 'one_state_workflow':
                    settings.moderation_enabled = False
                elif wf[0] == 'comment_review_workflow':
                    settings.moderation_enabled = True
                else:
                    # Custom workflow
                    pass

plone.app.discussion.browser.controlpanel.notify_configuration_changed = \
                                                notify_configuration_changed

