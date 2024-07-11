""" Export users with local groups and roles as CSV
"""
import csv
from plone import api
from zExceptions import Unauthorized


def users(self):
    """ Export users with local roles as CSV """
    mdata = api.portal.get_tool('portal_memberdata')
    mtool = api.portal.get_tool('portal_membership')
    portal = api.portal.get()
    if not mtool.checkPermission("Manage portal", portal):
        raise Unauthorized("You are not allowed to export users")
    groups = getattr(portal.acl_users.source_groups, '_groups', [])
    local_groups = [g for g in groups]

    members = getattr(mdata, '_members', [])
    self.REQUEST.RESPONSE.setHeader('Content-Type', 'application/csv')
    self.REQUEST.RESPONSE.setHeader(
        'Content-Disposition', 'attachment; filename="users.csv"')
    writer = csv.writer(self.REQUEST.RESPONSE)
    writer.writerow([
        'index', 'username', 'fullname', 'email',
        'last_login_time', "login_time", 'roles', 'groups'])
    for idx, member in enumerate(sorted(members.keys())):
        user = mtool.getMemberById(member)
        if user is not None:
            fullname = user.getProperty('fullname')
            email = user.getProperty('email')
            last_seen = user.getProperty('last_login_time')
            login_time = user.getProperty("login_time")
            groups = ', '.join([g for g in user.getGroups()
                                if g in local_groups])
            roles = ', '.join([r for r in user.getRoles()
                               if r not in ['Member', 'Authenticated']])
            writer.writerow([
                idx, member, fullname, email,
                last_seen, login_time, roles, groups
            ])
    return ''
