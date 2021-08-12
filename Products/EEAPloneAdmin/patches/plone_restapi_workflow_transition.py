from DateTime import DateTime
from zope.component import queryMultiAdapter
from plone.restapi.interfaces import IDeserializeFromJson
from Products.CMFCore.interfaces import IFolderish
from Products.CMFCore.utils import getToolByName
import logging

logger = logging.getLogger()


def patched_recurse_transition(
        self, objs, comment, publication_dates, include_children=False
):
    logger.info('called plone.restapi patch')
    transition_id = self.transition
    pprops = getToolByName(self, 'portal_properties')
    sprops = pprops.site_properties
    transitions_or_states = sprops.getProperty(
        'pub_date_set_on_workflow_transition_or_state', ['publish'])
    for obj in objs:
        if publication_dates:
            deserializer = queryMultiAdapter(
                (obj, self.request), IDeserializeFromJson
            )
            deserializer(data=publication_dates)

        # set effective date only if transition is publish and we have no date
        if obj.EffectiveDate() == "None" and transition_id in \
                transitions_or_states:
            obj.setEffectiveDate(DateTime())

        self.wftool.doActionFor(obj, transition_id, comment=comment)
        if include_children and IFolderish.providedBy(obj):
            self.recurse_transition(
                obj.objectValues(), comment, publication_dates, include_children
            )
