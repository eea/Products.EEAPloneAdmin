""" Patch TinyMCE
"""
import json
from Products.CMFCore.utils import getToolByName
from Products.CMFEditions.utilities import maybeSaveVersion
from Products.CMFCore.interfaces._content import IFolderish
from plone.app.layout.navigation.interfaces import INavigationRoot
from plone.i18n.normalizer.interfaces import IIDNormalizer
from Acquisition import aq_inner
from Acquisition import aq_parent
from Acquisition import ImplicitAcquisitionWrapper
from zope.component import getUtility


def patched_getListing(self, filter_portal_types, rooted, document_base_url,
                       upload_type=None, image_types=None):
    """Returns the actual listing"""
    catalog_results = []
    results = {}
    # code written in Products.TinyMCE which isn't actually used
    #image_types = image_types or []

    obj = aq_inner(self.context)
    portal_catalog = getToolByName(obj, 'portal_catalog')
    normalizer = getUtility(IIDNormalizer)

    # check if object is a folderish object, if not, get it's parent.
    if not IFolderish.providedBy(obj):
        obj = aq_parent(obj)

    if INavigationRoot.providedBy(obj) or (rooted == "True" and
                                document_base_url[:-1] == obj.absolute_url()):
        results['parent_url'] = ''
    else:
        results['parent_url'] = aq_parent(obj).absolute_url()

    if rooted == "True":
        results['path'] = self.getBreadcrumbs(results['parent_url'])
    else:
        # get all items from siteroot to context (title and url)
        results['path'] = self.getBreadcrumbs()

    plone_layout = self.context.restrictedTraverse('@@plone_layout', None)
    if plone_layout is None:
        # Plone 3
        plone_view = self.context.restrictedTraverse('@@plone')
        getIcon = lambda brain: plone_view.getIcon(brain).html_tag()
    else:
        # Plone >= 4
        getIcon = lambda brain: plone_layout.getIcon(brain)()

    # get all portal types and get information from brains

    # start patch -> get all portal types and get information from brains
    # plone4 added ability to click topics and get the query results
    if not isinstance(obj.queryCatalog, ImplicitAcquisitionWrapper):
        brains = obj.queryCatalog()
    else:
        path = '/'.join(obj.getPhysicalPath())
        query = self.listing_base_query.copy()
        query.update({'portal_type': filter_portal_types,
                      'sort_on': 'getObjPositionInParent',
                      'path': {'query': path, 'depth': 1}})
        brains = portal_catalog(**query)
    for brain in brains:
        description = u''
        if isinstance(brain.Description, unicode):
            description = brain.Description
        else:
            description = unicode(brain.Description, 'utf-8', 'ignore')
        catalog_results.append({
            'id': brain.getId,
            'uid': brain.UID or None,  # Maybe Missing.Value
            'url': brain.getURL(),
            'portal_type': brain.portal_type,
            'normalized_type': normalizer.normalize(brain.portal_type),
            'title': brain.Title == "" and brain.id or brain.Title,
            'icon': getIcon(brain),
            'description': description,
            'is_folderish': brain.is_folderish,
            })
    ## end patch


    # add catalog_ressults
    results['items'] = catalog_results

    # decide whether to show the upload new button
    results['upload_allowed'] = False
    if upload_type:
        portal_types = getToolByName(obj, 'portal_types')
        fti = getattr(portal_types, upload_type, None)
        if fti is not None:
            results['upload_allowed'] = fti.isConstructionAllowed(obj)

    # return results in JSON format
    self.context.REQUEST.response.setHeader("Content-type", "application/json")
    return json.dumps(results)

def patched_getSearchResults(self, filter_portal_types, searchtext):
    """Returns the actual search result"""
    if '*' not in searchtext:
        searchtext += '*'

    catalog_results = []
    results = {
        'parent_url': '',
        'path': [],
    }

    #folder_path = '/'.join(self.context.getPhysicalPath())
    # #14922 do a site wide search from now on instead of being bounded
    # by navigation root and context language
    folder_path = '/www'
    query = {
        'portal_type': filter_portal_types,
        'sort_on': 'sortable_title',
        'path': folder_path,
        'Title': searchtext,
        'Language': 'all',
    }
    if searchtext:
        plone_layout = self.context.restrictedTraverse('@@plone_layout',
                                                       None)
        if plone_layout is None:
            # Plone 3
            plone_view = self.context.restrictedTraverse('@@plone')
            getIcon = lambda brain: plone_view.getIcon(brain).html_tag()
        else:
            # Plone >= 4
            getIcon = lambda brain: plone_layout.getIcon(brain)()

        brains = self.context.portal_catalog.searchResults(**query)
        for brain in brains:
            catalog_results.append({
                'id': brain.getId,
                'uid': brain.UID,
                'url': brain.getURL(),
                'portal_type': brain.portal_type,
                'title': brain.Title == "" and brain.id or brain.Title,
                'icon': getIcon(brain),
                'description': brain.Description,
                'is_folderish': brain.is_folderish,
                })

    # add catalog_results
    results['items'] = catalog_results

    # never allow upload from search results page
    results['upload_allowed'] = False

    # return results in JSON format
    self.context.REQUEST.response.setHeader("Content-type",
                                            "application/json")
    return json.dumps(results)


def patched_getStyles(self, styles, labels):
    """ See ITinyMCE interface
    """
    h = {"Tables": [], "Lists":[]}
    styletype = ""
    titles = []
    for i in styles[4:]:
        e = i.split('|')
        while len(e) <= 2:
            e.append("")
        if not e[1]:
            styletype = e[0]
            titles.append(styletype)
            h[styletype] = ['{ title: "' + styletype +
                            '"' + ', tag: "", className: "-", type: "'
                            + styletype + '"' + ' }']
            continue
        el = e[1].lower()
        if el in ('table', 'tr', 'td', 'th'):
            styletype = "Tables"
        elif el in ('ol', 'li', 'dt', 'dd', 'dl'):
            styletype = "Lists"
        if not styletype:
            continue
        h[styletype].append('{ title: "' + e[0] + '", tag: "' + e[1] +
                            '", className: "' + e[2] + '", type: "' +
                            styletype + '" }')

    a = []
    # add styles in the order they were added
    for title in titles:
        a.extend(h[title])
    return '[' + ','.join(a) + ']'



def patched_save(self, text, fieldname):
    """18221 call SaveVersion when using tinyMCE save plugin"""
    self.context.getField(fieldname).set(self.context, text,
                                         mimetype='text/html')
    # patch
    maybeSaveVersion(self.context, comment="TinyMCE save triggered revision",
                     force=False)

    return "saved"


def patched_getConfiguration(self, context=None, field=None, request=None):
    """ #117294 show path bar and add mini-header to body class """
    results = self._old_getConfiguration(context, field, request)
    results['theme_advanced_path'] = True
    if context.restrictedTraverse('@@miniheader_content_types')():
        results['body_class'] += ' mini-header'
    return results
