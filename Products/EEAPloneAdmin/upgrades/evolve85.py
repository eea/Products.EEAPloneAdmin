""" Upgrade steps for 8.5
"""
import logging
from Products.CMFCore.utils import getToolByName
import transaction

logger = logging.getLogger("Products.EEAPloneAdmin.upgrades")


def update_role_mappings(context):
    """Update role mappings for objects"""
    catalog = getToolByName(context, 'portal_catalog')
    wf = getToolByName(context, 'portal_workflow')
    wf_def = wf.getWorkflowById('CallForTender')
    count = 0

    if wf_def:
        query = {'portal_type': ('CallForTender', 'CallForInterest',
                                 'CallForProposal', "NegotiatedProcedure"),
                 'Language': 'all'}
        brains = catalog(**query)

        for brain in brains:
            obj = brain.getObject()
            wf_def.updateRoleMappingsFor(obj)

            obj.reindexObject(idxs=['allowedRolesAndUsers', 'review_state'])
            logger.info('Updated role mapping for %s', brain.getURL())

            count += 1
            total = len(brains)

            if count % 100 == 0:
                logger.info('INFO: Subtransaction committed to zodb (%s/%s)',
                            count, total)
                transaction.commit()

        logger.info('Role mapping update complete!')
