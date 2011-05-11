""" Call For Tender
"""
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.WorkflowTool import addWorkflowFactory
from Products.DCWorkflow.DCWorkflow import DCWorkflowDefinition
from Products.ExternalMethod.ExternalMethod import ExternalMethod
from Products.EEAContentTypes.config import PROJECTNAME as productname

def setupCallForTender(self, workflow):
    """Define the CallForTender workflow.
    """
    # Add additional roles to portal
    portal = getToolByName(self,'portal_url').getPortalObject()
    data = list(portal.__ac_roles__)
    for role in ['Editor']:
        if not role in data:
            data.append(role)
    portal.__ac_roles__ = tuple(data)

    workflow.setProperties(title='CallForTender')

    for s in ['private', 'open', 'closed', 'completed']:
        workflow.states.addState(s)

    for t in ['close', 'make private', 'open', 'complete']:
        workflow.transitions.addTransition(t)

    for v in ['review_history', 'comments', 'time', 'actor', 'action']:
        workflow.variables.addVariable(v)

    workflow.addManagedPermission('Modify portal content')
    workflow.addManagedPermission('View')
    workflow.addManagedPermission('Access contents information')
    workflow.addManagedPermission('Copy or Move')
    workflow.addManagedPermission('Add CFTRequestor')
    workflow.addManagedPermission('Add portal content')

    for l in []:
        if not l in workflow.worklists.objectValues():
            workflow.worklists.addWorklist(l)

    ## Initial State

    workflow.states.setInitialState('private')

    ## States initialization

    stateDef = workflow.states['private']
    stateDef.setProperties(title="""Private""",
                           transitions=['open'])
    stateDef.setPermission('Modify portal content',
                           0,
                           ['Manager', 'Editor'])
    stateDef.setPermission('View',
                           0,
                           ['Manager', 'Editor'])
    stateDef.setPermission('Access contents information',
                           0,
                           ['Manager', 'Editor'])

    stateDef = workflow.states['open']
    stateDef.setProperties(title="""Open""",
                           transitions=['close', 'make private'])
    stateDef.setPermission('Modify portal content',
                           0,
                           ['Manager', 'Editor'])
    stateDef.setPermission('Copy or Move',
                           0,
                           ['Anonymous'])
    stateDef.setPermission('Access contents information',
                           0,
                           ['Anonymous'])
    stateDef.setPermission('Add CFTRequestor',
                           0,
                           ['Anonymous'])
    stateDef.setPermission('Add portal content',
                           0,
                           ['Anonymous'])

    stateDef = workflow.states['closed']
    stateDef.setProperties(title="""Closed""",
                           transitions=['complete', 'open'])
    stateDef.setPermission('Add CFTRequestor',
                           0,
                           ['Manager'])
    stateDef.setPermission('Modify portal content',
                           0,
                           ['Manager'])

    stateDef = workflow.states['completed']
    stateDef.setProperties(title="""Completed""",
                           transitions=['close'])

    ## Transitions initialization

    transitionDef = workflow.transitions['close']
    transitionDef.setProperties(title="""close""",
                                new_state_id="""closed""",
                                trigger_type=1,
                                script_name="""""",
                                after_script_name="""""",
                                actbox_name="""close""",
                                actbox_url="""""",
                                actbox_category="""workflow""",
                                props={},
                                )

    transitionDef = workflow.transitions['make private']
    transitionDef.setProperties(title="""make private""",
                                new_state_id="""private""",
                                trigger_type=1,
                                script_name="""""",
                                after_script_name="""""",
                                actbox_name="""make private""",
                                actbox_url="""""",
                                actbox_category="""workflow""",
                                props={},
                                )

    ## Creation of workflow scripts
    for wf_scriptname in ['moveObject']:
        if not wf_scriptname in workflow.scripts.objectIds():
            workflow.scripts._setObject(wf_scriptname,
                ExternalMethod(wf_scriptname, wf_scriptname,
                productname + '.CallForTender_scripts',
                wf_scriptname))

    transitionDef = workflow.transitions['open']
    transitionDef.setProperties(title="""open""",
                                new_state_id="""open""",
                                trigger_type=1,
                                script_name="""""",
                                after_script_name="""moveObject""",
                                actbox_name="""open""",
                                actbox_url="""""",
                                actbox_category="""workflow""",
                                props={},
                                )

    transitionDef = workflow.transitions['complete']
    transitionDef.setProperties(title="""complete""",
                                new_state_id="""completed""",
                                trigger_type=1,
                                script_name="""""",
                                after_script_name="""""",
                                actbox_name="""complete""",
                                actbox_url="""""",
                                actbox_category="""workflow""",
                                props={},
                                )

    ## State Variable
    workflow.variables.setStateVar('review_state')

    ## Variables initialization
    variableDef = workflow.variables['review_history']
    variableDef.setProperties(
        description="""Provides access to workflow history""",
        default_value="""""",
        default_expr="""state_change/getHistory""",
        for_catalog=0,
        for_status=0,
        update_always=0,
        props={'guard_permissions': 'Request review; Review portal content'})

    variableDef = workflow.variables['comments']
    variableDef.setProperties(
        description="""Comments about the last transition""",
        default_value="""""",
        default_expr="""python:state_change.kwargs.get('comment', '')""",
        for_catalog=0,
        for_status=1,
        update_always=1,
        props=None)

    variableDef = workflow.variables['time']
    variableDef.setProperties(
        description="""Time of the last transition""",
        default_value="""""",
        default_expr="""state_change/getDateTime""",
        for_catalog=0,
        for_status=1,
        update_always=1,
        props=None)

    variableDef = workflow.variables['actor']
    variableDef.setProperties(
        description="""The ID of the user who performed the last transition""",
        default_value="""""",
        default_expr="""user/getId""",
        for_catalog=0,
        for_status=1,
        update_always=1,
        props=None)

    variableDef = workflow.variables['action']
    variableDef.setProperties(
        description="""The last transition""",
        default_value="""""",
        default_expr="""transition/getId|nothing""",
        for_catalog=0,
        for_status=1,
        update_always=1,
        props=None)

def createCallForTender(self, oid):
    """Create the workflow for EEAContentTypes.
    """

    ob = DCWorkflowDefinition(oid)
    setupCallForTender(self, ob)
    return ob

addWorkflowFactory(createCallForTender,
                   id='CallForTender',
                   title='CallForTender')
