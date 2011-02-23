from zope.interface import implements, Interface
from zope.component import adapts, getMultiAdapter, queryMultiAdapter

from Acquisition import aq_parent, aq_inner, aq_base
from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.browser.plone import Plone
from Products.CMFPlone.browser.navtree import getNavigationRoot
from Products.CMFPlone import utils
from Products.NavigationManager.browser.navigation import  getApplicationRoot
from interfaces import IPloneAdmin, IObjectTitle
from zope.publisher.interfaces.browser import IBrowserRequest

class ObjectTitle(object):
    
    implements(IObjectTitle)
    adapts(Interface)
    
    def __init__(self, context):
        self.context = context

    @property
    def title(self):
        context = self.context
        putils = getToolByName(context, 'plone_utils')
        path = context.getPhysicalPath()
        title = parentTitle = putils.pretty_title_or_id(context, u'').decode('utf8')
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
                    title = '%s - %s' % (title.encode('utf8'), parentTitle.encode('utf8'))
        return title

    def isDefaultPageInFolder(self):
        context = self.context
        request = context.REQUEST
        container = aq_parent(aq_inner((context)))
        if not container:
            return False
        view = getMultiAdapter((container, request), name='default_page')
        return view.isDefaultPage(context)

class PloneAdmin(Plone):

    implements(IPloneAdmin)
    
    def isCmsMode(self):
        """ """
        context = utils.context(self)
        portal_url = getToolByName(context, 'portal_url')
        portal = portal_url.getPortalObject()

        proptool = getToolByName(context, 'portal_properties')        
        adminSkin = getattr(proptool.site_properties,'admin_skin', None)
        admin = adminSkin and portal.getCurrentSkinName() == adminSkin
        print "Admin: %s" % admin
        return admin

    def toLocalizedTime(self, time, long_format=None, translate=True):
        """ Remove translation of localized time """
        if translate:
            return Plone.toLocalizedTime(self, time, long_format)
        props = getToolByName(utils.context(self), 'portal_properties').site_properties
        time = DateTime(time)
        if long_format:
            return time.strftime( props.localLongTimeFormat )
        return  time.strftime( props.localTimeFormat )

    def _initializeData(self, options=None):
        Plone._initializeData(self, options)
        context = utils.context(self)
        
        # first try with a multi adapter, if no luck try single adapter
        adapter = queryMultiAdapter((context, context.REQUEST), IObjectTitle)
        if adapter is None:
            adapter = IObjectTitle(context)
        self._data['browser_title'] = adapter.title

        self._data['local_site'] = self._data['portal_url']
        if self._data['language'] != 'en':
            root = getattr(self._data['portal'],'SITE', self._data['portal'])
            if hasattr(root, 'getTranslation') and root.getTranslation(self._data['language']) is not None:
                self._data['local_site'] = '%s/%s' % ( self._data['portal_url'], self._data['language'])

        for action in self._data['actions']['site_actions']:
            action['url'] = action['url'].replace('LOCAL_SITE',self._data['local_site'])


        is_empty = False
        if self._data.get('isAnon', False):
            catalog = getToolByName(context, 'portal_catalog')
            rid = catalog.getrid('/'.join(context.getPhysicalPath()))
            if rid:
                metadata = catalog.getMetadataForRID(rid)
                is_empty = metadata and metadata.get('is_empty', False)
                
        self._data['isEmpty'] = is_empty

        
    def _prepare_slots(self):
        """ Prepares a structure that makes it conveient to determine
            if we want to use-macro or render the path expression.
            The values for the dictioanries is a list of tuples
            that are path expressions and the second value is a
            1 for use-macro, 0 for render path expression.
        """
        context = utils.context(self)
        slots={ 'left':[],
                'right':[],
                'document_actions':[] }

        canonical_left_slots = []
        canonical_right_slots = []
        canonical_document_action_slots = []

        left_slots=getattr(context,'left_slots', [])
        right_slots=getattr(context,'right_slots', [])
        document_action_slots=getattr(context,'document_action_slots', [])
        # if we use plone root slots we take the ane fron canonical
        # they may be the same
        if hasattr(aq_base(context), 'getCanonical'):
            plone = self._data['portal']
            canonical = context.getCanonical()
            if  hasattr(aq_parent(context), 'getCanonical') and  aq_parent(canonical) is not aq_parent(context).getCanonical():
                # we only get seetings from canonical if they are in the same
                # translated structure, i.e if a translated press release is
                # moved from a theme centre to the newsrelease folder we take
                # the canonical of parent of the translation
                # We don't do this right away since there can be properties on
                # the object it self so if we are in the same parallel structure
                # we keep context canonical.
                canonical = aq_parent(context).getCanonical()
                
            if left_slots == getattr(plone, 'left_slots', []):
                left_slots = getattr(canonical, 'left_slots', [])
            if right_slots == getattr(plone, 'right_slots', []):
                right_slots = getattr(canonical, 'right_slots', [])
            if document_action_slots == getattr(plone, 'document_action_slots', []):
                document_action_slots = getattr(canonical, 'document_action_slots', [])
        
        #check if the *_slots attributes are callable so that they can be
        # overridden by methods or python scripts

        if callable(left_slots):
            left_slots=left_slots()

        if callable(right_slots):
            right_slots=right_slots()

        if callable(document_action_slots):
            document_action_slots=document_action_slots()

        for slot in left_slots:
            if not slot: continue
            if slot.find('/macros/')!=-1:
                slots['left'].append( (slot, 1) )
            else:
                slots['left'].append( (slot, 0) )

        for slot in right_slots:
            if not slot: continue
            if slot.find('/macros/')!=-1:
                slots['right'].append( (slot, 1) )
            else:
                slots['right'].append( (slot, 0) )

        for slot in document_action_slots:
            if not slot: continue
            if slot.find('/macros/')!=-1:
                slots['document_actions'].append( (slot, 1) )
            else:
                slots['document_actions'].append( (slot, 0) )

        return slots


            
