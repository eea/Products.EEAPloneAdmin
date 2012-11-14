""" Patch TinyMCE
"""
from Acquisition import aq_base
from Products.Archetypes.interfaces import IBaseObject
from Products.CMFCore.utils import getToolByName
from plone.app.layout.navigation.interfaces import INavigationRoot
from Products.CMFCore.interfaces._content import IFolderish
from Acquisition import aq_inner
from Acquisition import aq_parent
import json
from zope.component import getUtility
from plone.i18n.normalizer.interfaces import IIDNormalizer

def patched_getContentType(self, object=None, fieldname=None):
    """ Original code here. Notice that it doesn't treat properly the
    case that fieldname is None

    def getContentType(self, object=None, fieldname=None):
        context = aq_base(object)
        if IBaseObject.providedBy(context):
            # support Archetypes fields
            if fieldname is None:
                field = context.getPrimaryField()
            else:
                field = context.getField(
                    fieldname) or getattr(context, fieldname, None)
            if field and hasattr(aq_base(field), 'getContentType'):
                return field.getContentType(context)
        elif '.widgets.' in fieldname:
            # support plone.app.textfield RichTextValues
            fieldname = fieldname.split('.widgets.')[-1]
            field = getattr(context, fieldname, None)
            mimetype = getattr(field, 'mimeType', None)
            if mimetype is not None:
                return mimetype
        return 'text/html'
    """

    context = aq_base(object)
    if IBaseObject.providedBy(context):
        # support Archetypes fields
        if fieldname is None:
            field = context.getPrimaryField()
        else:
            field = context.getField(fieldname) or getattr(
                context, fieldname, None)
        if field and hasattr(aq_base(field), 'getContentType'):
            return field.getContentType(context)
    elif fieldname == None:
        return 'text/html'
    elif '.widgets.' in fieldname:
        # support plone.app.textfield RichTextValues
        fieldname = fieldname.split('.widgets.')[-1]
        field = getattr(context, fieldname, None)
        mimetype = getattr(field, 'mimeType', None)
        if mimetype is not None:
            return mimetype
    return 'text/html'


def patched_getListing(self, filter_portal_types, rooted,
                                    document_base_url, upload_type=None):
    """ Returns the actual listing
    """
    catalog_results = []
    results = {}

    obj = aq_inner(self.context)
    normalizer = getUtility(IIDNormalizer)

    # check if object is a folderish object, if not, get it's parent.
    if not IFolderish.providedBy(obj):
        obj = aq_parent(obj)

    if INavigationRoot.providedBy(object) or (rooted == "True" and 
                            document_base_url[:-1] == object.absolute_url()):
        results['parent_url'] = ''
    else:
        results['parent_url'] = aq_parent(obj).absolute_url()

    if rooted == "True":
        results['path'] = self.getBreadcrumbs(results['parent_url'])
    else:
        # get all items from siteroot to context (title and url)
        results['path'] = self.getBreadcrumbs()

    # start patch -> get all portal types and get information from brains
    # plone4 added ability to click topics and get the query results
    def cat_results(brain):
        """ utility function to avoid repetition of code
        """
        return  catalog_results.append({
                'id': brain.getId,
                'uid': brain.UID or None,  # Maybe Missing.Value
                'url': brain.getURL(),
                'portal_type': brain.portal_type,
                'normalized_type': normalizer.normalize(brain.portal_type),
                'title': brain.Title == "" and brain.id or brain.Title,
                'icon': brain.getIcon,
                'is_folderish': brain.is_folderish
                })
        
    base_obj = aq_base(obj)
    if hasattr(base_obj, 'queryCatalog'):
        for brain in obj.queryCatalog(sort_on='getObjPositionInParent'):
            cat_results(brain)
    else:
        for brain in self.context.getFolderContents({'portal_type':
                    filter_portal_types, 'sort_on': 'getObjPositionInParent'}):
            cat_results(brain)
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
    return json.dumps(results)

def patched_getSearchResults(self, filter_portal_types, searchtext):
    """ Returns the actual search result
    """
    catalog_results = []
    results = {}

    results['parent_url'] = ''
    results['path'] = []
    if searchtext:
        # plone4 it was search by SearchableText instead of title which gave
        # thousands of searches just vaguely related to the keywords
        folder_path = '/'.join(self.context.getPhysicalPath())
        res = self.context.portal_catalog.searchResults(
                Title='%s*' % searchtext, portal_type=filter_portal_types,
                Language=self.context.Language(), path={'query': folder_path})
        for brain in res:
            catalog_results.append({
                'id': brain.getId,
                'uid': brain.UID,
                'url': brain.getURL(),
                'portal_type': brain.portal_type,
                'title': brain.Title == "" and brain.id or brain.Title,
                'icon': brain.getIcon,
                'is_folderish': brain.is_folderish
                })

    # add catalog_results
    results['items'] = catalog_results

    # never allow upload from search results page
    results['upload_allowed'] = False

    # return results in JSON format
    return json.dumps(results)
