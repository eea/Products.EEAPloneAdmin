""" Audit local roles
"""
from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from Acquisition import aq_parent, aq_base
from plone import api
from DateTime import DateTime
from logging import getLogger
import csv

class AuditLocalRoles(BrowserView):
    """Local roles assigned under context"""

    def __init__(self, context, request):
        super(AuditLocalRoles, self).__init__(context, request)

        self.ALL_CTYPES_TXT = 'ALL TYPES'
        self.DISPLAY_TXT = 'Display report in browser'
        self.FILE_DOWNLOAD_TXT = 'Generate TSV file for download'
        self.FILE_PREFIX = 'audit_local_roles_'

        self.rolemaps = {}

        self.messages = []
        self.ctypes = []
        self.outypes = []

        self.brains = []
        self.db_effectiveroles = {}

    def __call__(self):

        req_submit = self.request.get('submit', None)
        req_ctypes = self.request.get('ctypes', None)
        req_outype = self.request.get('outype', None)

        cont = True

        if not req_submit:
            cont = False
            self.setCTypesForSelection()
            self.setOutputForSelection()
        else:
            if not req_ctypes:
                cont = False
                self.setCTypesForSelection()
                self.messages.append((
                    "err", "Please select content type(s)."
                ))
            else:
                if isinstance(req_ctypes, str):
                    req_ctypes = (req_ctypes,)
                else:
                    req_ctypes = tuple(req_ctypes)

                self.setCTypesForSelection(req_ctypes)

            if not req_outype:
                cont = False
                self.setOutputForSelection()
                self.messages.append((
                    "err", "Please select the type of output."
                ))
            else:
                self.setOutputForSelection(req_outype)

        if not cont:
            return self.index()

        self.p_cat = getToolByName(self.context, 'portal_catalog')
        self.acl_u = getToolByName(self.context, 'acl_users')
        self.logger = getLogger("[AuditLocalRoles]")

        self.portal = api.portal.get()
        self.url_prefix = \
            self.portal.absolute_url()[:-len(self.portal.absolute_url(1))-1]

        self.setBrains()

        if not self.brains:
            self.messages.append((
                "warn",
                "No objects of selected type(s) were found " +
                "under current context."
            ))
            return self.index()
        else:
            self.messages.append((
                "info",
                str(len(self.brains)) +
                " object(s) of selected type(s)" +
                " were found under current context."
            ))

        self.localzone = DateTime().timezone()

        self.computeRoleMaps()

        if req_outype == self.FILE_DOWNLOAD_TXT:
            self.setHeadersForFileDownloadTsv()

        return self.index()

    def getPortalSearchedTypes(self):
        """Returns a list with all the 'user searchable' content types"""

        sp = getToolByName(self.context, 'portal_properties').site_properties
        ctypes_ns = sp.getProperty('types_not_searched', ())

        pt = getToolByName(self.context, 'portal_types')
        ctypes = pt.listContentTypes()

        types = [t for t in ctypes if t not in ctypes_ns]

        return types

    def setCTypesForSelection(self, selected=()):
        """Sets up the 'ctypes' property as a list of all the content types
        available to the user for form selection, together with a flag which
        marks the user's selected content types. Default value is not present.
        """

        self.ctypes = [(self.ALL_CTYPES_TXT, self.ALL_CTYPES_TXT in selected)]

        types = self.getPortalSearchedTypes()

        self.ctypes += \
            [(t, t in selected and not self.ctypes[0][1]) for t in types]

    def getCTypesForSelection(self):
        """Getter fo 'ctypes' property. Called via view's template."""

        return self.ctypes

    def setOutputForSelection(self, selected=None):
        """Sets up the 'outypes' property as a list of the view's output types
        available to the user for form selection, together with a flag which
        marks the user's selected output type. Default value is present.
        """

        if not selected:
            selected = self.DISPLAY_TXT

        self.outypes = [
            (self.DISPLAY_TXT, self.DISPLAY_TXT == selected),
            (self.FILE_DOWNLOAD_TXT, self.FILE_DOWNLOAD_TXT == selected)
        ]

    def getOutputForSelection(self, selected=None):
        """Getter fo 'outype' property. Called via view's template."""

        return self.outypes

    def getMessages(self):
        """Getter fo 'messages' property. Called via view's template."""

        return self.messages

    def getUrlPrefix(self):
        """Getter fo 'url_prefix' property. Called via view's template."""

        return self.url_prefix

    def setBrains(self):
        """Sets up the 'brains' property, based on user's selection of
        content types
        """

        portal_types = []

        for ctype, selected in self.ctypes:
            if selected:
                if ctype == self.ALL_CTYPES_TXT:
                    portal_types = [t for t in self.getPortalSearchedTypes()]
                    break
                else:
                    portal_types.append(ctype)

        context_path = '/'.join(self.context.getPhysicalPath())

        self.brains = self.p_cat.queryCatalog({
            'path': context_path,
            'portal_type': portal_types,
            'Language': 'all',
            'show_inactive': True,
            'sort_on': "path"
        })

    def computeRoleMaps(self):
        """Looks for local roles within current context and stores relevant
        info in the 'rolemaps' dictionary
        """

        err_cnt = 0
        for brain in self.brains:
            rolemap = {}

            try:
                roles = self.getEffectiveRoles(brain.getPath())

                for _login, _roles, _type, _id in roles:
                    if _roles == ('Owner',):
                        continue
                    else:
                        if _type in rolemap.keys():
                            rolemap[_type].append(
                                (_id, tuple(r for r in _roles if r != 'Owner'))
                            )
                        else:
                            rolemap[_type] = [
                                (_id, tuple(r for r in _roles if r != 'Owner'))
                            ]

            except Exception, e:
                self.logger.error("Failed processing object '%s' (%s)",
                                  brain.getPath(), e)
                err_cnt += 1
                continue

            if rolemap:
                if brain.CreationDate != 'None':
                    br_created = brain.created.toZone(self.localzone).ISO()
                else:
                    br_created = None

                if brain.EffectiveDate != 'None':
                    br_effective = brain.effective.toZone(self.localzone).ISO()
                else:
                    br_effective = None

                if brain.ExpirationDate != 'None':
                    br_expires = brain.expires.toZone(self.localzone).ISO()
                else:
                    br_expires = None

                for _type in rolemap:
                    for _id, _roles in rolemap[_type]:
                        if _type in self.rolemaps.keys():
                            if _id in self.rolemaps[_type].keys():
                                self.rolemaps[_type][_id][1].append((
                                    _roles,
                                    brain.getPath(),
                                    brain.review_state,
                                    brain.portal_type,
                                    br_created,
                                    br_effective,
                                    br_expires
                                ))
                            else:
                                self.rolemaps[_type][_id] = (
                                    self.isUserInactive(_id, _type),
                                    [
                                        (
                                            _roles,
                                            brain.getPath(),
                                            brain.review_state,
                                            brain.portal_type,
                                            br_created,
                                            br_effective,
                                            br_expires
                                        )
                                    ]
                                )
                        else:
                            self.rolemaps[_type] = {
                                _id: (
                                    self.isUserInactive(_id, _type),
                                    [
                                        (
                                            _roles,
                                            brain.getPath(),
                                            brain.review_state,
                                            brain.portal_type,
                                            br_created,
                                            br_effective,
                                            br_expires
                                        )
                                    ]
                                )
                            }

        self.db_effectiveroles = {}

        if err_cnt:
            self.messages.append((
                "err",
                "Failed processing " +
                    str(err_cnt) + " objects. Review logs for details."
            ))

    def getEffectiveRoles(self, context_path):
        """Returns a tuple with the effective local roles at the given
        context path
        """

        if context_path in self.db_effectiveroles.keys():
            result = self.db_effectiveroles[context_path]
            return result

        context = api.content.get(path=context_path)

        a_roles = context.acl_users._getLocalRolesForDisplay(context)
        result = a_roles

        if not getattr(aq_base(context), '__ac_local_roles_block__', None) \
                and self.portal != context:

            parent = aq_parent(context)
            parent_path = '/'.join(parent.getPhysicalPath())

            if getattr(parent, 'acl_users', False):
                i_roles = self.getEffectiveRoles(parent_path)

                if not a_roles:
                    return i_roles

                result = []

                for i_login, i_roles, i_type, i_id in i_roles:
                    result.append([i_login, list(i_roles), i_type, i_id])

                for a_login, a_roles, a_type, a_id in a_roles:
                    found = 0
                    for _login, _roles, _type, _id in result:
                        if _id == a_id:
                            for a_role in a_roles:
                                if a_role not in _roles:
                                    _roles.append(a_role)
                            found = 1
                            break
                    if found == 0:
                        result.append([a_login, list(a_roles), a_type, a_id])

                for pos in range(len(result)-1, -1, -1):
                    result[pos][1] = tuple(result[pos][1])
                    result[pos] = tuple(result[pos])

        self.db_effectiveroles[context_path] = tuple(result)

        return result

    def isUserInactive(self, _id, _id_type):
        """Local roles information can point to users which do not exist
        anymore. Returns True if such a case is identified, otherwise False.
        """

        if _id_type == 'user' and not self.acl_u.getUserById(_id):
            return True
        return False

    def getPrincipalsForDisplay(self):
        """Based on the 'rolemaps' dictionary, returns a 'sorted' list
        containing details about users/groups which have local roles assigned
        Called via view's template.
        """

        result = []

        for _type in sorted(self.rolemaps.keys(), key=str.lower, reverse=True):
            s = []
            for _id in sorted(self.rolemaps[_type].keys(), key=str.lower):
                _inactive = self.rolemaps[_type][_id][0]
                s.append((_id, _inactive))
            result.append((_type, s))

        return result

    def getRoleMapForDisplay(self, _type, _id):
        """Based on the 'rolemaps' dictionary, for given user/group id,
        returns details about local roles and the associated content objects
        Called via view's template.
        """

        return self.rolemaps[_type][_id][1]

    def getRoleMapsForFileDownloadTsv(self, field_names=True):
        """Based on the 'rolemaps' dictionary, "prepares" the row-level data
        that will go into a TSV-formatted file; yields/returns row data
        in the form of tuple, not string
        """

        if field_names:
            yield (
                'AccessID',
                'isUserID',
                'userActive',
                'LocalRoles',
                'ObjectPath',
                'ObjectState',
                'ObjectType',
                'ObjectCreationDate',
                'ObjectEffectiveDate',
                'ObjectExpiryDate'
            )

        for _type in self.rolemaps:
            for _id in self.rolemaps[_type]:
                _inactive = self.rolemaps[_type][_id][0]
                for rowdata in self.rolemaps[_type][_id][1]:
                    yield (
                          _id,
                          'True' if _type == 'user' else 'False',
                          str(not _inactive),
                          ', '.join(rowdata[0]),
                          rowdata[1],
                          rowdata[2],
                          rowdata[3],
                          rowdata[4] or '',
                          rowdata[5] or '',
                          rowdata[6] or ''
                    )

    def setHeadersForFileDownloadTsv(self):
        """Base on the data generated by getRoleMapsForFileDownloadTsv(),
        sets up the response's header for TSV file download, if the user
        selected the output type as specified in the FILE_DOWNLOAD_TXT constant
        """

        contents = self.getRoleMapsForFileDownloadTsv()

        tstamp = DateTime().toZone(self.localzone).strftime('%Y%m%d_%I%M%S')

        self.request.response.setHeader(
            'Content-Type',
            'application/tsv'
        )
        self.request.response.setHeader(
            'Content-Disposition',
            'attachment; filename="' + self.FILE_PREFIX + tstamp + '.tsv"'
        )

        writer = csv.writer(self.request.response, delimiter='\t')
        writer.writerows(contents)
