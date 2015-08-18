""" Update EEAFigureFile local workflow policy for Images
"""
from Products.CMFCore.utils import getToolByName
import logging

logger = logging.getLogger('EEAPloneAdmin.updatelocalpolicy')
info = logger.info
info_exception = logger.exception

def updateLocalPolicy(self):
    """ Set EEAFigureFile local workflow policy for Images
        to eeafigurefile_image_workflow
    """
    context = self
    ppw = getToolByName(context, 'portal_placeful_workflow')
    cat = getToolByName(context, 'portal_catalog')
    info('Starting local policy update')

    query = {'portal_type': 'EEAFigureFile'}
    brains = cat(**query)

    for brain in brains:
        fig_object = brain.getObject()
        info('Adding local workflow policy for %s', brain.getId)
        config = ppw.getWorkflowPolicyConfig(fig_object)
        if not config:
            fig_object.manage_addProduct['CMFPlacefulWorkflow'].\
                manage_addWorkflowPolicyConfig()
            config = ppw.getWorkflowPolicyConfig(fig_object)

        config.setPolicyBelow('eeafigurefile_image_workflow', False)

    info('Done local policy update')
