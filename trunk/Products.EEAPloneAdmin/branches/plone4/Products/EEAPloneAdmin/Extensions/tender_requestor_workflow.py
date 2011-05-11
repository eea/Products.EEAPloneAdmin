""" Tender requestor workflow
"""
from Products.CMFCore.WorkflowTool import addWorkflowFactory
from Products.DCWorkflow.DCWorkflow import DCWorkflowDefinition
from Products.ExternalMethod.ExternalMethod import ExternalMethod
from Products.EEAContentTypes.config import PROJECTNAME as productname

def setuptender_requestor_workflow(self, workflow):
    """Define the tender_requestor_workflow workflow.
    """

    workflow.setProperties(title='tender_requestor_workflow')

    for s in ['new', 'submitted']:
        workflow.states.addState(s)

    for t in ['submit']:
        workflow.transitions.addTransition(t)

    for v in ['review_history', 'comments', 'time', 'actor', 'action']:
        workflow.variables.addVariable(v)

    workflow.addManagedPermission('Modify portal content')
    workflow.addManagedPermission('View')
    workflow.addManagedPermission('Access contents information')
    workflow.addManagedPermission('Delete objects')

    for l in []:
        if not l in workflow.worklists.objectValues():
            workflow.worklists.addWorklist(l)

    ## Initial State

    workflow.states.setInitialState('new')

    ## States initialization

    stateDef = workflow.states['new']
    stateDef.setProperties(title="""New""",
                           transitions=['submit'])
    stateDef.setPermission('Modify portal content',
                           0,
                           ['Manager', 'Anonymous'])

    stateDef = workflow.states['submitted']
    stateDef.setProperties(title="""Submitted""",
                           transitions=[])
    stateDef.setPermission('Modify portal content',
                           0,
                           ['Manager'])
    stateDef.setPermission('View',
                           0,
                           ['Manager'])
    stateDef.setPermission('Access contents information',
                           0,
                           ['Anonymous'])
    stateDef.setPermission('Delete objects',
                           0,
                           ['Manager'])

    ## Transitions initialization

    ## Creation of workflow scripts
    for wf_scriptname in ['sendCFTLink']:
        if not wf_scriptname in workflow.scripts.objectIds():
            workflow.scripts._setObject(wf_scriptname,
                ExternalMethod(wf_scriptname, wf_scriptname,
                productname + '.tender_requestor_workflow_scripts',
                wf_scriptname))

    transitionDef = workflow.transitions['submit']
    transitionDef.setProperties(title="""submit""",
                                new_state_id="""submitted""",
                                trigger_type=1,
                                script_name="""""",
                                after_script_name="""sendCFTLink""",
                                actbox_name="""submit""",
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

def createtender_requestor_workflow(self, cid):
    """Create the workflow for EEAContentTypes.
    """

    ob = DCWorkflowDefinition(cid)
    setuptender_requestor_workflow(self, ob)
    return ob

addWorkflowFactory(createtender_requestor_workflow,
                   id='tender_requestor_workflow',
                   title='tender_requestor_workflow')
