""" Controllers
"""
from Acquisition import aq_parent, aq_inner
from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.browser.ploneview import Plone
from Products.NavigationManager.browser.navigation import  getApplicationRoot
from Products.EEAPloneAdmin.browser.interfaces import IPloneAdmin, IObjectTitle
from plone.app.layout.globals.context import ContextState as BaseContextState
from plone.app.layout.globals.portal import PortalState as BasePortalState
from plone.memoize.view import memoize
from zope.component import adapts, getMultiAdapter, queryMultiAdapter
from zope.interface import implements, Interface

class ObjectTitle(object):
    """ Object title
    """
    implements(IObjectTitle)
    adapts(Interface)

    def __init__(self, context):
        self.context = context

    @property
    def title(self):
        """ Title
        """
        context = self.context
        putils = getToolByName(context, 'plone_utils')
        path = context.getPhysicalPath()
        title = parentTitle = putils.pretty_title_or_id(context, u''
                                                        ).decode('utf8')
        if len(path) > 3:
            obj = context
            if self.isDefaultPageInFolder():
                obj = aq_parent(obj)
            root = getApplicationRoot(context)
            if root is not context:
                while root is not aq_parent(obj) and  parentTitle == title:
                    obj = aq_parent(obj)
                    parentTitle = putils.pretty_title_or_id(obj).decode('utf8')
                if parentTitle != title and root is not obj:
                    title = '%s - %s' % (title.encode('utf8'),
                                         parentTitle.encode('utf8'))
        return title

    def isDefaultPageInFolder(self):
        """ Default page
        """
        context = self.context
        request = context.REQUEST
        container = aq_parent(aq_inner((context)))
        if not container:
            return False
        view = getMultiAdapter((container, request), name='default_page')
        return view.isDefaultPage(context)


class PloneAdmin(Plone):
    """ Plone admin
    """
    implements(IPloneAdmin)

    def toLocalizedTime(self, time, long_format = None,
                        time_only = None, translate=True):
        """ Remove translation of localized time """
        if translate:
            return Plone.toLocalizedTime(self, time=time, time_only=time_only,
                                         long_format=long_format)
        props = getToolByName(self.context, 'portal_properties').site_properties
        time = DateTime(time)
        if long_format:
            return time.strftime( props.localLongTimeFormat )
        return  time.strftime( props.localTimeFormat )

    @memoize
    def isCmsMode(self):
        """ CMS Mode """
        context = self.context
        portal_url = getToolByName(context, 'portal_url')
        portal = portal_url.getPortalObject()

        proptool = getToolByName(context, 'portal_properties')
        adminSkin = getattr(proptool.site_properties, 'admin_skin', None)
        admin = adminSkin and portal.getCurrentSkinName() == adminSkin
        #print "Admin: %s" % admin
        return admin

    def local_site(self):
        """ Local site
        """
        raise NotImplementedError(
            "This has been moved to @@plone_portal_state")

    #def is_empty(self):
        #""" Empty
        #"""
        #raise NotImplementedError(
            #"This has been moved to @@plone_context_state")

    def browser_title(self):
        """ Title
        """
        raise NotImplementedError(
            "This has been moved to @@plone_context_state")

    def _prepare_slots(self):
        """ Prepares a structure that makes it convenient to determine
            if we want to use-macro or render the path expression.
            The values for the dictionaries is a list of tuples
            that are path expressions and the second value is a
            1 for use-macro, 0 for render path expression.
        """
        # ZZZ: implement this for plone4, at this moment this method is
        # not called
        # tiberich: at this moment there's nothing in our zope
        # that will call this method.
        # I'm leaving this here as a reminder of what needs to be done:
        # make the columns portlet manager
        # also look for canonical objects when looking at left/right slots.

        raise NotImplementedError

        #context = self.context
        #slots={ 'left':[],
                #'right':[],
                #'document_actions':[] }

        ##canonical_left_slots = []
        ##canonical_right_slots = []
        ##canonical_document_action_slots = []

        #left_slots=getattr(context,'left_slots', [])
        #right_slots=getattr(context,'right_slots', [])
        #document_action_slots=getattr(context,'document_action_slots', [])
        ## if we use plone root slots we take the one from canonical
        ## they may be the same
        #if hasattr(aq_base(context), 'getCanonical'):
            #plone = self._data['portal']
            #canonical = context.getCanonical()
            #if  (hasattr(aq_parent(context), 'getCanonical') and
                 #aq_parent(canonical) is not
                 #aq_parent(context).getCanonical()):
                ## we only get seetings from canonical if they are in the same
                ## translated structure, i.e if a translated press release is
                ## moved from a theme centre to the newsrelease folder we take
                ## the canonical of parent of the translation
                ## We don't do this right away since there can be properties on
                ## the object it self so if we are in
                ## the same parallel structure
                ## we keep context canonical.
                #canonical = aq_parent(context).getCanonical()

            #if left_slots == getattr(plone, 'left_slots', []):
                #left_slots = getattr(canonical, 'left_slots', [])
            #if right_slots == getattr(plone, 'right_slots', []):
                #right_slots = getattr(canonical, 'right_slots', [])
            #if document_action_slots == getattr(
                #plone, 'document_action_slots', []):
                #document_action_slots = getattr(
                    #canonical, 'document_action_slots', [])

        ##check if the *_slots attributes are callable so that they can be
        ## overridden by methods or python scripts

        #if callable(left_slots):
            #left_slots=left_slots()

        #if callable(right_slots):
            #right_slots=right_slots()

        #if callable(document_action_slots):
            #document_action_slots=document_action_slots()

        #for slot in left_slots:
            #if not slot: continue
            #if slot.find('/macros/')!=-1:
                #slots['left'].append( (slot, 1) )
            #else:
                #slots['left'].append( (slot, 0) )

        #for slot in right_slots:
            #if not slot: continue
            #if slot.find('/macros/')!=-1:
                #slots['right'].append( (slot, 1) )
            #else:
                #slots['right'].append( (slot, 0) )

        #for slot in document_action_slots:
            #if not slot: continue
            #if slot.find('/macros/')!=-1:
                #slots['document_actions'].append( (slot, 1) )
            #else:
                #slots['document_actions'].append( (slot, 0) )

        #return slots


class ContextState(BaseContextState):
    """Additions to default @@plone_context_state"""

    #@memoize
    #def is_empty(self):
        #""" Empty
        #"""
        #portal_state = getMultiAdapter((self.context, self.request),
                                        #name="plone_portal_state")
        ## NOTE: this used to be globalized with p2.5 method,
        ## this in no longer possible
        #context = self.context
        #is_empty = False
        #if portal_state.anonymous():
            #catalog = getToolByName(context, 'portal_catalog')
            #rid = catalog.getrid('/'.join(context.getPhysicalPath()))
            #if rid:
                #metadata = catalog.getMetadataForRID(rid)
                #is_empty = metadata and metadata.get('is_empty', False)

        #return is_empty

    @memoize
    def browser_title(self):
        """ Title
        """
        # NOTE: this used to be globalized with p2.5 method,
        # this in no longer possible

        context = self.context

        # first try with a multi adapter, if no luck try single adapter
        adapter = queryMultiAdapter((context, context.REQUEST), IObjectTitle)
        if adapter is None:
            adapter = IObjectTitle(context)
        return adapter.title


class PortalState(BasePortalState):
    """Additions to default @@plone_portal_state"""

    @memoize
    def local_site(self):
        """ Local site
        """
        # NOTE: this used to be globalized with p2.5 method,
        # this in no longer possible
        # ZZZ: BAD STYLE: this method used to have side effects,
        # by changing site actions urls
        portal = self.portal()
        language = self.language()
        portal_url = self.portal_url()

        local_site = portal_url
        if language != 'en':
            root = getattr(portal, 'SITE', portal)
            if (hasattr(root, 'getTranslation') and
                root.getTranslation(language) is not None):
                local_site = '%s/%s' % (portal_url, language)

        #ZZZ: implement this for plone4
        #for action in self._data['actions']['site_actions']:
            #action['url'] = action['url'].replace('LOCAL_SITE',
                                                      #self._data['local_site'])

        return local_site
