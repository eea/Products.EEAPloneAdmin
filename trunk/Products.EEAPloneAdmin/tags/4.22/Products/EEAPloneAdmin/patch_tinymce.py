""" Patch TinyMCE
"""
from Acquisition import aq_base
from Products.Archetypes.interfaces import IBaseObject

# needed by patched_getConfiguration
from Products.CMFCore.utils import getToolByName
from zope.i18n import translate
from Products.TinyMCE import TMCEMessageFactory as _
from types import StringTypes
from plone.app.layout.globals.portal import RIGHT_TO_LEFT
from zope.app.component.hooks import getSite
from Products.CMFCore.interfaces._content import IFolderish
from Acquisition import aq_inner
from Acquisition import aq_parent
import json

# needed by patched_getListing
from zope.component import getUtility
from plone.i18n.normalizer.interfaces import IIDNormalizer

def patched_getContentType(self, object=None, fieldname=None):
    """Original code here. Notice that it doesn't treat properly the
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


def patched_getConfiguration(self, context=None, field=None, request=None):
    """ Patched configuration to set NavigationRoot to www/SITE since
        we have many folders that implement INavigationRoot
    """
    results = {}

    # Get widget attributes
    widget = getattr(field, 'widget', None)
    filter_buttons = getattr(widget, 'filter_buttons', None)
    allow_buttons = getattr(widget, 'allow_buttons', None)
    redefine_parastyles = getattr(widget, 'redefine_parastyles', None)
    parastyles = getattr(widget, 'parastyles', None)
    rooted = getattr(widget, 'rooted', False)
    toolbar_width = getattr(widget, 'toolbar_width', self.toolbar_width)

    # Get safe html transform
    safe_html = getattr(getToolByName(self, 'portal_transforms'), 'safe_html')

    # Get kupu library tool filter
    # Settings are stored on safe_html transform in Plone 4 and
    # on kupu tool in Plone 3.
    kupu_library_tool = getToolByName(self, 'kupu_library_tool', None)

    # Remove to be stripped attributes
    try:
        style_whitelist = safe_html.get_parameter_value('style_whitelist')
    except (KeyError, AttributeError):
        if kupu_library_tool is not None:
            style_whitelist = kupu_library_tool.getStyleWhitelist()
        else:
            style_whitelist = []
    results['valid_inline_styles'] = style_whitelist

    # Replacing some hardcoded translations
    labels = {}
    labels['label_styles'] = translate(_('(remove style)'), context=request)
    labels['label_paragraph'] = translate(_('Normal paragraph'),
                                                            context=request)
    labels['label_plain_cell'] = translate(_('Plain cell'), context=request)
    labels['label_style_ldots'] = translate(_('Style...'), context=request)
    labels['label_text'] = translate(_('Text'), context=request)
    labels['label_tables'] = translate(_('Tables'), context=request)
    labels['label_selection'] = translate(_('Selection'), context=request)
    labels['label_lists'] = translate(_('Lists'), context=request)
    labels['label_print'] = translate(_('Print'), context=request)
    labels['label_no_items'] = translate(_('No items in this folder'),
                                                            context=request)
    labels['label_no_anchors'] = translate(_('No anchors in this page'),
                                                            context=request)
    results['labels'] = labels

    # Add styles to results
    results['styles'] = []
    results['table_styles'] = []
    if not redefine_parastyles:
        if isinstance(self.tablestyles, StringTypes):
            for tablestyle in self.tablestyles.split('\n'):
                if not tablestyle:
                    # empty line
                    continue
                tablestylefields = tablestyle.split('|')
                tablestyletitle = tablestylefields[0]
                tablestyleid = tablestylefields[1]
                if tablestyleid == 'plain':
                    # Do not duplicate the default style hardcoded in the
                    # table.htm.pt
                    continue
                if request is not None:
                    tablestyletitle = translate(_(tablestylefields[0]),
                                                        context=request)
                results['styles'].append(tablestyletitle + '|table|' +
                                                            tablestyleid)
                results['table_styles'].append(tablestyletitle + '=' +
                                                            tablestyleid)
        if isinstance(self.styles, StringTypes):
            styles = []
            for style in self.styles.split('\n'):
                if not style:
                    # empty line
                    continue
                stylefields = style.split('|')
                styletitle = stylefields[0]
                if request is not None:
                    styletitle = translate(_(stylefields[0]), context=request)
                merge = styletitle + '|' + '|'.join(stylefields[1:])
                styles.append(merge)
            results['styles'].extend(styles)

    if parastyles is not None:
        results['styles'].extend(parastyles)

    # Get buttons from control panel
    results['buttons'] = self.getEnabledButtons(context=context)

    # Filter buttons
    if allow_buttons is not None:
        allow_buttons = self.translateButtonsFromKupu(context=context,
                                                        buttons=allow_buttons)
        results['buttons'] = filter(lambda x: x in results['buttons'],
                                                                allow_buttons)
    if filter_buttons is not None:
        filter_buttons = self.translateButtonsFromKupu(context=context,
                                                       buttons=filter_buttons)
        results['buttons'] = filter(lambda x: x not in filter_buttons,
                                                           results['buttons'])

    # Get valid html elements
    results['valid_elements'] = self.getValidElements()

    # Set toolbar_location
    if self.toolbar_external:
        results['toolbar_location'] = 'external'
    else:
        results['toolbar_location'] = 'top'

    if self.autoresize:
        results['path_location'] = 'none'
        results['resizing_use_cookie'] = False
        results['resizing'] = False
        results['autoresize'] = True
    else:
        results['path_location'] = 'bottom'
        results['resizing_use_cookie'] = True
        if self.resizing:
            results['resizing'] = True
        else:
            results['resizing'] = False
        results['autoresize'] = False

    if '%' in self.editor_width:
        results['resize_horizontal'] = False
    else:
        results['resize_horizontal'] = True

    try:
        results['editor_width'] = int(self.editor_width)
    except (TypeError, ValueError):
        results['editor_width'] = 600

    try:
        results['editor_height'] = int(self.editor_height)
    except (TypeError, ValueError):
        results['editor_height'] = 400

    try:
        results['toolbar_width'] = int(toolbar_width)
    except (TypeError, ValueError):
        results['toolbar_width'] = 440

    if self.directionality == 'auto':
        language = context.Language()
        if not language:
            portal_properties = getToolByName(context, "portal_properties")
            site_properties = portal_properties.site_properties
            language = site_properties.getProperty('default_language',
                                                   None)
        directionality = (language[:2] in RIGHT_TO_LEFT) and 'rtl' or 'ltr'
    else:
        directionality = self.directionality
    results['directionality'] = directionality

    if self.contextmenu:
        results['contextmenu'] = True
    else:
        results['contextmenu'] = False

    portal = getSite()
    results['portal_url'] = aq_inner(portal).absolute_url()
    # plone4 commented line
    # nav_root = getNavigationRootObject(context, portal)
    nav_root = portal.restrictedTraverse('SITE')
    results['navigation_root_url'] = nav_root.absolute_url()

    if self.content_css and self.content_css.strip() != "":
        results['content_css'] = self.content_css
    else:
        results['content_css'] = '/'.join([
            results['portal_url'],
            self.getId(),
            "@@tinymce-getstyle"])

    if self.link_using_uids:
        results['link_using_uids'] = True
    else:
        results['link_using_uids'] = False

    if self.allow_captioned_images:
        results['allow_captioned_images'] = True
    else:
        results['allow_captioned_images'] = False

    if self.rooted or rooted:
        results['rooted'] = True
    else:
        results['rooted'] = False

    results['customplugins'] = []
    if self.customplugins is not None:
        results['customplugins'].extend(self.customplugins.split('\n'))

    results['entity_encoding'] = self.entity_encoding

    props = getToolByName(self, 'portal_properties')
    livesearch = props.site_properties.getProperty('enable_livesearch', False)
    if livesearch:
        results['livesearch'] = True
    else:
        results['livesearch'] = False

    AVAILABLE_LANGUAGES = set(
    'sq ar hy az eu be bn nb bs br bg ca ch zh hr cs da dv nl en et fi fr gl '
    'ka de el gu he hi hu is id ia it ja ko lv lt lb mk ms ml mn se no nn fa '
    'pl pt ps ro ru sc sr ii si sk sl es sv ta tt te th tr tw uk ur cy vi zu'
                                                                    .split())

    if 'LANGUAGE' in context.REQUEST:
        results['language'] = context.REQUEST.LANGUAGE[:2]
        if results['language'] not in AVAILABLE_LANGUAGES:
            results['language'] = "en"
    else:
        results['language'] = "en"

    try:
        results['document_url'] = context.absolute_url()
        parent = aq_parent(aq_inner(context))
        if getattr(aq_base(context), 'checkCreationFlag', None) and \
                                                  context.checkCreationFlag():
            parent = aq_parent(aq_parent(parent))
            results['parent'] = parent.absolute_url() + "/"
        else:
            if IFolderish.providedBy(context):
                results['parent'] = context.absolute_url() + "/"
            else:
                results['parent'] = parent.absolute_url() + "/"
    except AttributeError:
        results['parent'] = results['portal_url'] + "/"
        results['document_url'] = results['portal_url']

    # Get Library options
    results['libraries_spellchecker_choice'] = \
                                    self.libraries_spellchecker_choice

    # init vars specific for "After the Deadline" spellchecker
    mtool = getToolByName(portal, 'portal_membership')
    member = mtool.getAuthenticatedMember()
    # None when Anonymous User
    results['atd_rpc_id'] = 'Products.TinyMCE-' + (member.getId() or '')
    results['atd_rpc_url'] = "%s/@@" % portal.absolute_url()
    results['atd_show_types'] = self.libraries_atd_show_types.strip() \
                                                    .replace('\n', ',')
    results['atd_ignore_strings'] = self.libraries_atd_ignore_strings \
                                            .strip().replace('\n', ',')

    return json.dumps(results)



def patched_getBreadcrumbs(self, path=None):
    """Get breadcrumbs with navigation root set to www/SITE"""
    result = []

    #plone4 root_url = getNavigationRoot(self.context)
    root_url = "/www/SITE/"
    root = aq_inner(self.context.restrictedTraverse(root_url))
    root_url = root.absolute_url()

    if path is not None:
        root_abs_url = root.absolute_url()
        path = path.replace(root_abs_url, '', 1)
        path = path.strip('/')
        root = aq_inner(root.restrictedTraverse(path))

    relative = aq_inner(self.context) \
            .getPhysicalPath()[len(root.getPhysicalPath()):]
    if path is None:
        # Add siteroot
        result.append({'title': root.title_or_id(),
                                'url': '/'.join(root.getPhysicalPath())})

    for i in range(len(relative)):
        now = relative[:i + 1]
        obj = aq_inner(root.restrictedTraverse(now))

        if IFolderish.providedBy(obj):
            if not now[-1] == 'talkback':
                result.append({'title': obj.title_or_id(),
                                  'url': root_url + '/' + '/'.join(now)})
    return result


def patched_getListing(self, filter_portal_types, rooted,
                                    document_base_url, upload_type=None):
    """Returns the actual listing"""
    catalog_results = []
    results = {}

    object = aq_inner(self.context)
    portal_catalog = getToolByName(object, 'portal_catalog')
    normalizer = getUtility(IIDNormalizer)

    # check if object is a folderish object, if not, get it's parent.
    if not IFolderish.providedBy(object):
        object = aq_parent(object)

    #plone4 if INavigationRoot.providedBy(object) or 
    #(rooted == "True" and document_base_url[:-1] == object.absolute_url()):
    if (rooted == "True" and document_base_url[:-1] == object.absolute_url()):
        results['parent_url'] = ''
    else:
        results['parent_url'] = aq_parent(object).absolute_url()

    if rooted == "True":
        results['path'] = self.getBreadcrumbs(results['parent_url'])
    else:
        # get all items from siteroot to context (title and url)
        results['path'] = self.getBreadcrumbs()

    # get all portal types and get information from brains
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
    path = '/'.join(object.getPhysicalPath())
    if object.portal_type == 'Topic':
        for brain in object.queryCatalog(sort_on='getObjPositionInParent'):
            cat_results(brain)
    else:
        for brain in portal_catalog(portal_type=filter_portal_types,
                                    sort_on='getObjPositionInParent',
                                    path={'query': path, 'depth': 1}):
            cat_results(brain)

    # add catalog_ressults
    results['items'] = catalog_results

    # decide whether to show the upload new button
    results['upload_allowed'] = False
    if upload_type:
        portal_types = getToolByName(object, 'portal_types')
        fti = getattr(portal_types, upload_type, None)
        if fti is not None:
            results['upload_allowed'] = fti.isConstructionAllowed(object)

    # return results in JSON format
    return json.dumps(results)


def patched_getSearchResults(self, filter_portal_types, searchtext):
    """Returns the actual search result"""

    catalog_results = []
    results = {}

    results['parent_url'] = ''
    results['path'] = []
    if searchtext:
        # plone4 it was search by SearchableText instead of title which gave
        # thousands of searches just vaguely related to the keywords
        for brain in self.context.portal_catalog.searchResults({'Title': '%s*'
            % searchtext, 'portal_type': filter_portal_types, 'sort_on':
            'sortable_title', 'path': '/'.join(
                                            self.context.getPhysicalPath())}):
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
