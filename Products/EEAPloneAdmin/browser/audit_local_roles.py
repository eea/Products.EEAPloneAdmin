""" Audit local roles
"""
from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from Acquisition import aq_parent, aq_base
import logging

class AuditLocalRoles(BrowserView):
    def __call__(self):
        self.cat = getToolByName(self.context, 'portal_catalog')
        self.logger = logging.getLogger("[AuditLocalRoles]")
        self.messages = []
        return self.getRoles()

    def localRolesMap(self, context):
        """ Effective local roles
        """

        rolemap = {}

        inherited_roles = self._inherited_roles(context)

        for login, roles, type, id in inherited_roles:
            if roles == ('Owner',):
                continue
            else:
                rolemap[id] = {
                    'details': [login, type],
                    'local_roles': [r for r in roles if r != 'Owner']
                }

        assigned_roles = context.acl_users._getLocalRolesForDisplay(context)

        for login, roles, type, id in assigned_roles:
            if roles == ('Owner',):
                continue
            elif rolemap.has_key(id):
                add = [r for r in roles if r != 'Owner']
                rolemap[id]['local_roles'] = list(
                    set(rolemap[id]['local_roles']).union(set(add))
                )
            else:
                rolemap[id] = {
                    'details': [login, type],
                    'local_roles': [r for r in roles if r != 'Owner']
                }

        return rolemap

    def _inherited(self, context):
        """Return True if local roles are inherited here. """

        if getattr(aq_base(context), '__ac_local_roles_block__', None):
            return False
        return True

    def _inherited_roles(self, context):
        """Returns a tuple with the acquired local roles."""

        if not self._inherited(context):
            return ()

        portal = getToolByName(context, 'portal_url').getPortalObject()

        result = []
        cont = True

        if portal != context:
            parent = aq_parent(context)
            while cont:
                if not getattr(parent, 'acl_users', False):
                    break
                userroles = parent.acl_users._getLocalRolesForDisplay(parent)
                for user, roles, role_type, name in userroles:
                    # Find user in result
                    found = 0
                    for user2, roles2, type2, name2 in result:
                        if user2 == user:
                            # Check which roles must be added to roles2
                            for role in roles:
                                if role not in roles2:
                                    roles2.append(role)
                            found = 1
                            break
                    if found == 0:
                        # Add it to result and make sure roles is a list so
                        # we may append and not overwrite the loop variable
                        result.append([user, list(roles), role_type, name])
                if parent == portal:
                    cont = False
                elif not self._inherited(parent):
                    # Role acquired check here
                    cont = False
                else:
                    parent = aq_parent(parent)

        # Tuplize all inner roles
        for pos in range(len(result)-1, -1, -1):
            result[pos][1] = tuple(result[pos][1])
            result[pos] = tuple(result[pos])

        return tuple(result)

    def getRoles(self):
        context_path = '/'.join(self.context.getPhysicalPath())

        brains = self.cat.queryCatalog({
            'path': context_path,
            'portal_type': "Folder",
            'Language': 'all',
            'show_inactive': True,
            'sort_on': "path"
        })

        no_brains = len(brains)
        self.messages.append("* no. of 'Folder' objects under context: " + str(no_brains))

        rolemaps = {}

        cnt = 0
        for brain in brains:
            cnt += 1

            self.logger.info("processing object %s/%s: %s",
                             str(cnt), str(no_brains), brain.getPath())
            ob = brain.getObject()

            rolemap = {}

            try:
                rolemap = self.localRolesMap(ob)
            except Exception, e:
                self.messages.append("* failed processing object '" +
                                     brain.getPath() + "' (" + str(e) + ")")
                self.logger.error("* failed processing object '%s' (%s)",
                                  brain.getPath(), e)
                continue

            if rolemap:
                for id in rolemap:
                    if id in rolemaps.keys():
                        rolemaps[id]['local_roles'].append((
                            brain.getPath(),
                            ob.absolute_url(),
                            rolemap[id]['local_roles']
                        ))
                    else:
                        rolemaps[id] = {
                            'id_details': rolemap[id]['details'],
                            'local_roles': [
                                (
                                    brain.getPath(),
                                    ob.absolute_url(),
                                    rolemap[id]['local_roles']
                                )
                            ]
                        }

        ids = set(rolemaps.keys())
        user_ids = set()
        group_ids = set()
        oth_ids = set()

        for id in ids:
            princ_type = rolemaps[id]['id_details'][1]
            if princ_type == 'user':
                user_ids.add(id)
            elif princ_type == 'group':
                group_ids.add(id)
            else:
                oth_ids.add(id)

        html = ''

        html += '<html>'
        html += '<head>'
        html += '<style>'
        html += 'p {margin: 0;}'
        html += 'table, th, td {text-align:left;' + \
                'border: 1px solid black; border-collapse: collapse;}'
        html += 'h2, h3 {display: inline-block; margin-bottom: 0;}'
        html += 'ul {margin: 0 auto;}'
        html += 'a#up {color: grey; text-decoration: none;}'
        html += 'span#uid {color: red;}'
        html += '</style></head>'
        html += '</head>'
        html += '<body>'        

        html += '<h1>Effective local roles of Plone principals under current context</h1>'

        for msg in self.messages:
            html += '<p>' + msg + '</p>'

        html += '<h2 id="toc">Quick links:</h2><br />'
        if user_ids:
            html += '<h3>User IDs:</h3>'
            html += '<ul>'
            for id in sorted(user_ids):
                html += '<li><a href="#' + id + '">' + id + '</a></li>'
            html += '</ul>'
        if group_ids:
            html += '<h3>Group IDs:</h3>'
            html += '<ul>'
            for id in sorted(group_ids):
                html += '<li><a href="#' + id + '">' + id + '</a></li>'
            html += '</ul>'
        if oth_ids:
            html += '<h3>Other IDs:</h3>'
            html += '<ul>'
            for id in sorted(oth_ids):
                html += '<li><a href="#' + id + '">' + id + '</a></li>'
            html += '</ul>'

        html += '<br />'

        for id in rolemaps:
            princ_type = rolemaps[id]['id_details'][1]

            html += '<h3 id="' + id + '">' + princ_type.capitalize() + \
                    ' ID: <span id="uid">' + id + '</span></h3>' + \
                    '<a id="up" href="#toc"> [up]</a>'
            html += '<table>'
            html += '<tr><th>Path</th><th>Local role(s)</th></tr>'
            for rowdata in rolemaps[id]['local_roles']:
                html += '<tr><td><a href="' + rowdata[1] + '">' + rowdata[0] + \
                        '</a></td><td>' + ', '.join(rowdata[2]) + '</td></tr>'
            html += '</table>'

        html += '</body>'
        html += '</html>'

        return html
