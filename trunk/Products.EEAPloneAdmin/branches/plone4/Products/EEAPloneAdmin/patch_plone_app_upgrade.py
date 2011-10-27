""" Monkey patch for plone.app.upgrade
"""
from Products.CMFCore.utils import getToolByName
from Products.GenericSetup.rolemap import RolemapExportConfigurator

def add_siteadmin_role(context):
    portal = getToolByName(context, 'portal_url').getPortalObject()

    # add the role to the site
    immediate_roles = list( getattr(portal, '__ac_roles__', []) )
    if 'Site Administrator' not in immediate_roles:
        immediate_roles.append('Site Administrator')
        immediate_roles.sort()
        portal.__ac_roles__ = tuple(immediate_roles)

    # add the Site Administrators group
    uf = getToolByName(context, 'acl_users')
    gtool = getToolByName(context, 'portal_groups')
    if not uf.searchGroups(id='Site Administrators'):
        gtool.addGroup('Site Administrators', title='Site Administrators', roles=['Site Administrator'])

    # update rolemap:
    # add Site Administrator role to permissions that have the Manager role,
    # plus some additional ones that only have Manager as a default role
    rolemap_exporter = RolemapExportConfigurator(portal)
    permissions = rolemap_exporter.listPermissions()
    extra_permissions = set([
        'Access arbitrary user session data',
        'Access contents information',
        'Access inactive portal content',
        'Access session data',
        'Add portal content',
        'Add portal events',
        'Change local roles',
        'Change portal events',
        'Copy or Move',
        'Mail forgotten password',
        'Modify portal content',
        'Review portal content',
        'Search ZCatalog',
        'Use Database Methods',
        'Use mailhost services',
        'Use version control',
        'View',
        'View History',
        'WebDAV Lock items',
        'WebDAV Unlock items',
        'WebDAV access',
        ])
    try:
        import Products.kupu
    except ImportError:
        pass
    else:
        extra_permissions.update([
        'Kupu: Manage libraries',
        'Kupu: Query libraries',
        ])
    exclude_permissions = set([
        'Manage portal',
        'View management screens',
        ])
    for permission_info in permissions:
        if permission_info['name'] in exclude_permissions:
            continue
        is_extra = permission_info['name'] in extra_permissions
        if is_extra:
            extra_permissions.remove(permission_info['name'])
        if is_extra or 'Manager' in permission_info['roles']:
            roles = permission_info['roles']
            roles.append('Site Administrator')
            roles.sort()
            portal.manage_permission(permission_info['name'],
                                     roles,
                                     permission_info['acquire'])
    for permission_id in extra_permissions:
        portal.manage_permission(permission_id, ['Site Administrator',], True)

    # update workflows:
    # add Site Administrator role where Manager already is;
    wtool = getToolByName(portal, 'portal_workflow')
    for workflow_id in wtool.getWorkflowIds():
        workflow = wtool[workflow_id]
        for state_id in workflow.states:
            state = workflow.states[state_id]
            #patch: do it only if permission are not scquired
            if state.permission_roles:
                for permission_id, roles in state.permission_roles.items():
                    if 'Manager' in roles:
                        new_roles = list(roles)
                        new_roles.append('Site Administrator')
                        state.setPermission(permission_id, isinstance(roles, list), new_roles)
