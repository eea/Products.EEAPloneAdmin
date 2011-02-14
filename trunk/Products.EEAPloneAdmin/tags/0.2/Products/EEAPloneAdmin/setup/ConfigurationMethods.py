import transaction
from Acquisition import aq_base
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.permissions import AddPortalMember
from Products.CMFPlone.migrations.migration_util import safeEditProperty

from zLOG import INFO
from Products.CMFPlone.setup.SetupBase import SetupWidget
from Products.EEAPloneAdmin.config import *
from eea.themecentre.interfaces import IThemeTagging, IThemeCentreSchema
from Products.NavigationManager.catalog import reindexTree

def migrateReportsRSS2Topics(self, portal):
    themes = portal.portal_catalog( {'object_provides' : 'eea.themecentre.interfaces.IThemeCentre',
				     'Language' : 'en',
				     'path' : '/www/SITE/themes' })
    languages = portal.portal_languages.getSupportedLanguages()
    wf = getToolByName(portal, 'portal_workflow')
    rt = getToolByName(portal, 'portal_redirection')
    def _redirectUrl(theme, obj):
        redirectUrl = '/%s/reports' % theme.absolute_url(1)
        if redirectUrl.startswith('/www/SITE'):
            redirectUrl = redirectUrl[9:]
        elif redirectUrl.startswith('/www'):
            redirectUrl = redirectUrl[4:]
        print redirectUrl
        rt.addRedirect(redirectUrl, obj)
        
    def _createTopic(theme, lang):
	translation = theme.getTranslation(lang)
	if translation is not None and hasattr(aq_base(theme),'publications'):
            title = portal.SITE.publications.getTranslation(lang).Title()
	    translation.manage_delObjects(ids=['reports'])
            localrdfrepo = rdfrepo.getTranslation(lang)
            if localrdfrepo:
                localrdfrepo.manage_delObjects(ids=['reports_%s' % theme.getId()])
                                               
            theme.publications.addTranslation(lang)
	    topicId = 'publications_topic'
	    theme.publications[topicId].addTranslation(lang)
	    folder = translation.publications
            _redirectUrl(translation, folder)
	    # disable rename after creation
	    folder.unmarkCreationFlag()
            topic = folder[topicId]
            topic.unmarkCreationFlag()
		
	    folder.setTitle(title)
	    topic.setTitle(title)
            topic.setLayout('folder_summary_view')
            topic.setCustomViewFields(['effective'])
	    folder.setDefaultPage(topicId)
	    wf.doActionFor(folder, 'publish', comment='Initial publish by method migrateReportsRSS2Topics')
	    wf.doActionFor(topic, 'publish', comment='Initial publish by method migrateReportsRSS2Topics')
            reindexTree(topic)

	if translation is not None:
            title = portal.SITE.articles.getTranslation(lang).Title()
            theme.articles.addTranslation(lang)
	    topicId = 'articles_topic'
	    theme.articles[topicId].addTranslation(lang)
	    folder = translation.articles
	    # disable rename after creation
	    folder.unmarkCreationFlag()
            topic = folder[topicId]
            topic.unmarkCreationFlag()
		
	    folder.setTitle(title)
	    topic.setTitle(title)
            topic.setLayout('folder_summary_view')
            topic.setCustomViewFields(['effective'])            
	    folder.setDefaultPage(topicId)
	    wf.doActionFor(folder, 'publish', comment='Initial publish by method migrateReportsRSS2Topics')
	    wf.doActionFor(topic, 'publish', comment='Initial publish by method migrateReportsRSS2Topics')
            reindexTree(topic)
            
    rdfrepo = portal.SITE.themes['rdf-repository']

    portal.SITE.themes.manage_changeProperties(send_workflow_emails=False)
    sendWorkflowEmails = portal.getProperty('send_workflow_emails')
    if sendWorkflowEmails is None:
        portal.manage_addProperty('send_workflow_emails', False, 'boolean')
    else:
        portal.manage_changeProperties(send_workflow_emails=False)

    for b in themes:
	theme = b.getObject()
	title = portal.SITE.publications.Title()
	theme.manage_delObjects(ids=['reports'])
        rdfrepo.manage_delObjects(ids=['reports_%s' % theme.getId()])
	theme.invokeFactory('Folder', id='publications', title=title)
	folder = theme.publications
        _redirectUrl(theme, folder)
	folder.setLanguage('en')
	wf.doActionFor(folder, 'publish', comment='Initial publish by method migrateReportsRSS2Topics')
	topicId = folder.invokeFactory('RichTopic', id='publications_topic', title=title)
	folder.setDefaultPage(topicId)
        topic = folder[topicId]
        topic.setLayout('folder_summary_view')
        topic.setLanguage('en')
        crit = topic.addCriterion('object_provides', 'ATSelectionCriterion')
        crit.setValue('eea.reports.interfaces.IReportContainerEnhanced')
        crit = topic.addCriterion('review_state', 'ATSelectionCriterion')
        crit.setValue('published')
        crit = topic.addCriterion('getThemes', 'ATSelectionCriterion')
        themes = IThemeCentreSchema(theme).tags
        crit.setValue(themes)
        topic.addCriterion('effective', 'ATSortCriterion')
        topic.setCustomViewFields(['effective'])
	wf.doActionFor(folder[topicId], 'publish', comment='Initial publish by method migrateReportsRSS2Topics')
        reindexTree(topic)
        
        # Articles
	title = portal.SITE.articles.Title()
	theme.invokeFactory('Folder', id='articles', title=title)
	folder = theme.articles
	folder.setLanguage('en')
	wf.doActionFor(folder, 'publish', comment='Initial publish by method migrateReportsRSS2Topics')
	topicId = folder.invokeFactory('RichTopic', id='articles_topic', title=title)
	folder.setDefaultPage(topicId)
        topic = folder[topicId]
        topic.setLayout('folder_summary_view')
        topic.setLanguage('en')
        crit = topic.addCriterion('Type', 'ATSelectionCriterion')
        crit.setValue('Article')
        crit = topic.addCriterion('review_state', 'ATSelectionCriterion')
        crit.setValue('published')
        crit = topic.addCriterion('getThemes', 'ATSelectionCriterion')
        themes = IThemeCentreSchema(theme).tags
        crit.setValue(themes)
        topic.addCriterion('effective', 'ATSortCriterion')
        topic.setCustomViewFields(['effective'])
	wf.doActionFor(folder[topicId], 'publish', comment='Initial publish by method migrateReportsRSS2Topics')
        reindexTree(topic)
        
        for lang in languages:
            if lang != 'en':
                _createTopic(theme, lang)
        transaction.savepoint()        

    # remove left report rss feeds from none existing theme centres
    reportRSS = [ feed for feed in rdfrepo.objectIds() if feed.startswith('report')]
    rdfrepo.manage_delObjects(ids=reportRSS)
    # remove reports directory in each site since it's redirected to publications
    site = portal.SITE
    site.manage_delObjects(ids=['reports'])
    for lang in languages:
        local = rdfrepo.getTranslation(lang)
        if local:
            reportRSS = [ feed for feed in local.objectIds() if feed.startswith('report')]
            local.manage_delObjects(ids=reportRSS)
        local = site.getTranslation(lang)
        if local and hasattr(aq_base(local),'reports'):
            local.manage_delObjects(ids=['reports'])
            
    if not portal.getProperty('manually_added_portlets'):
	portal.manage_addProperty('manually_added_portlets',
				['publications_topic', 'articles_topic'],
				  'lines')

    portal.SITE.themes.manage_changeProperties(send_workflow_emails=True)
    portal.manage_changeProperties(send_workflow_emails=sendWorkflowEmails)


def setupLanguageSettings(self, portal):
        portal.portal_languages.manage_setLanguageSettings('en', EEA_LANGUAGES)

def setupControlledMarshall(self, portal):
    from Products.Marshall import ControlledMarshaller
    from Products.Marshall.predicates import add_predicate
    from Products.Marshall.config import TOOL_ID as marshall_id
    from Products.ATContentTypes.content import *

    marshall = getToolByName(portal, marshall_id, None)
    if marshall:
        document.ATDocument.schema.registerLayer('marshall',
                                                 ControlledMarshaller())
        newsitem.ATNewsItem.schema.registerLayer('marshall',
                                             ControlledMarshaller())
        add_predicate(marshall, id='doc',
                      title='.doc extension',
                      predicate='default',
                      expression="python: filename and filename.endswith('.doc')",
                      component_name='primary_field')
        add_predicate(marshall, id='txt',
                      title='.txt extension',
                      predicate='default',
                      expression="python: filename and filename.endswith('.txt')",
                      component_name='rfc822')
        add_predicate(marshall, id='default',
                      title='default',
                      predicate='default',
                      expression='',
                      component_name='primary_field')
        
def configureContentTypes(self, portal):
    pt = getToolByName(portal, 'portal_types')
    typeInfo = { 'Folder' : { 'allowed_content_types' : ('Ad', 'Highlight', 'RDFEvent', 'Event', 'Document', 'Folder', 'RSSFeedRecipe', 'Promotion'),
                              'filter_content_types' : True},
                 'Plone Site' : { 'allowed_content_types' : ('Folder'),
                                  'filter_content_types' : True } }
    for t,info  in typeInfo.items():
        tInfo = pt.getTypeInfo(t)
        tInfo.allowed_content_types = info['allowed_content_types']
        tInfo.filter_content_types = info['filter_content_types']        

def setupDefaultLeftRightSlots(self, portal):
    """ sets up the slots on objectmanagers """
    left_slots=( 'here/portlet_navigation/macros/portlet')
    right_slots=()
    safeEditProperty(portal, 'left_slots', left_slots, 'lines')
    safeEditProperty(portal, 'right_slots', right_slots, 'lines')
    safeEditProperty(portal.Members, 'right_slots', (), 'lines')

def setDateProperties(self, portal):
    prop_tool = portal.portal_properties
    prop = prop_tool.site_properties
    prop.localTimeFormat = '%d %b %Y'
    prop.localLongTimeFormat = '%d %b %Y %H:%M'    

def setNavigationProperties(self, portal):
    prop_tool = portal.portal_properties
    n_prop = prop_tool.navtree_properties
    typesNotToList = [ 'ExternalHighlight','Highlight', 'FlashFile', 'News Item', 'RDFEvent', 'Event' ]
    for typ in n_prop.metaTypesNotToList:
        typesNotToList.append(typ)
    n_prop.metaTypesNotToList = typesNotToList
    n_prop.wf_states_to_show = ['published']
    n_prop.enable_wf_state_filtering = True

def setupDefaultRSSFeeds(self, portal):
    """ create default RSS feed recipes in folder /rss/
        rssfeeds =  ( (Title, URL, noOfEntries, noWithDescription, noWithThumbnail ) ) """

    rssfeeds = ( ('Reports', 'http://reports.eea.europa.eu/',
		             'http://reports.eea.europa.eu/reports.rdf?image=yes',2,1,1),
                 ('Briefings', 'http://reports.eea.eu.int/index_table?sort=Serial#Briefing',
		               'http://reports.eea.europa.eu/reports.rdf?select=public&image=yes&include_series=Briefing',2,1,1),
                 ('Technical reports', 'http://reports.eea.europa.eu/index_table?sort=Serial#Technical report',
		                       'http://reports.eea.europa.eu/reports.rdf?select=experts&image=yes',2,1,1),
		 ('Indicators', 'http://themes.eea.eu.int/all_indicators_box',
		                'http://themes.eea.europa.eu/indicators/indicators.rss', 2, 1, 0),
		 ('Maps and graphs', 'http://dataservice.eea.eu.int/atlas/',
		                     'http://dataconnector.eea.europa.eu/xmldataservice/xml/rss_news/MapsGrapsNews_Top10.xml', 1,1,0),
                 ('Data sets', 'http://dataservice.eea.eu.int/dataservice/',
		               'http://dataconnector.eea.europa.eu/xmldataservice/xml/rss_news/DatasetNews_Top10.xml',1,1,0),
                 ('National SOE reports', 'http://countries.eea.eu.int/SERIS',
		                     'http://countries.eea.europa.eu/SERIS/rss?version=1.0', 1,0,0) )
    rssFolder = getattr(portal, 'rss', None)
    if rssFolder is None:
        portal.invokeFactory('Folder', id='rss', title='RSS feeds')
        rssFolder = getattr(portal, 'rss', None)

    oldRss = rssFolder.contentValues('RSSFeedRecipe')
    oldUrls = [ old.getFeedURL() for old in oldRss ]
    print oldUrls
    workflow = portal.portal_workflow
    for title, homeUrl, rssUrl, noOfEntries, noWithDesc, noWithThumb  in rssfeeds:
        if rssUrl not in oldUrls:
            id = rssFolder.invokeFactory('RSSFeedRecipe', id=title.lower().replace(' ','-'), title=title,
				    url = homeUrl,
                                    feedURL = rssUrl,
                                    entriesSize = noOfEntries,
                                    entriesWithDescription = noWithDesc,
                                    entriesWithThumbnail = noWithThumb )
            rss = getattr(rssFolder, id)
            workflow.doActionFor(rss, 'publish')
            
def configureContentCache(cacheTool):
    """ add our content types for caching """
    rules = cacheTool.getRules()

    id = 'eed-content-types'
    if id not in rules.objectIds():
        rules.invokeFactory(id=id, type_name='ContentCacheRule')
        rule = getattr(rules, id)
        rule.setTitle('EEA Content')
        rule.setDescription('Rule for views of eea content types.  Anonymous users are served content object views from the proxy cache.  These views are purged when content objects change.  Authenticated users are served pages from memory.  Member ID is used in the ETag because content is personalized; the time of the last catalog change is included so that the navigation tree stays up to date.')
        rule.setContentTypes(['Highlight', 'PressRelease', 'FlashFile'])
        rule.setDefaultView(True)
        rule.setTemplates([])
        rule.setCacheStop(['portal_status_message'])
        rule.setLastModifiedExpression('python:object.modified()')
        rule.setHeaderSetIdAnon('cache-in-memory')
        rule.setHeaderSetIdAuth('cache-with-etag')
        rule.setEtagComponents(['member','catalog_modified','language','gzip','skin'])
        rule.setEtagRequestValues(['month','year','orig_query'])
        rule.setEtagTimeout(3600)
        rule.setPurgeExpression('python:object.getImageAndFilePurgeUrls()')
        rule.reindexObject()

def configureCache(self, portal):
    cacheTool = getToolByName(portal, 'portal_cache_settings', None)
    if cacheTool:
        cacheTool.setCacheConfig('squid_behind_apache')

        squidUrls = ['http://127.0.0.1:3128/']
        domains = [ 'http://www.eea.europa.eu:80', 'http://eea.europa.eu:80' ]
        for url in cacheTool.getSquidURLs():
            if url not in squidUrls:
                squidUrls.append(url)
        cacheTool.setSquidURLs(squidUrls)

        for d in cacheTool.getDomains():
            if d not in domains:
                domains.append(url)
        cacheTool.setDomains(domains)

        configureContentCache(cacheTool)

        
def disableAnonymousJoin(self, portal):
    portal.manage_permission(AddPortalMember,
                             ('Manager',), acquire=0)

def disableMailForgottenPassword(self, portal):
    portal.manage_permission('Mail forgotten password',
                             ('Manager',), acquire=0)


def setupLDAPUserFolder(self, portal):
    """ Basic LDAP initialization inside gruf's user source. 
        Code from GRUF3/tests. """
        
    from Products.EEAPloneAdmin.ldap_config import eionet
            
    dg = eionet.get
    # User source replacement
    portal.acl_users.replaceUserSource("Users",
        "manage_addProduct/LDAPUserFolder/manage_addLDAPUserFolder"
        )
    # Edit LDAPUF 'cause objectClass cannot be set otherwise :(
    lduf = portal.acl_users.Users.acl_users
    lduf.manage_edit(
        title = dg('title'),
        login_attr = dg('login_attr'),
        uid_attr = dg('uid_attr'),
        users_base = dg('users_base'),
        users_scope = dg('users_scope'),
        roles= dg('roles'),
        obj_classes = 'top,inetOrgPerson',
        groups_base = dg('groups_base'),
        groups_scope = dg('groups_scope'),
        binduid = dg('binduid'),
        bindpwd = dg('bindpwd'),
        binduid_usage = dg('binduid_usage'),
        rdn_attr = dg('rdn_attr'),
        local_groups = dg('local_groups'),
        encryption = dg('encryption'),
        read_only=dg('read_only'),
        )

    lduf.manage_addServer( host=dg('server')
                        , port=dg('port')
                        , use_ssl=dg('use_ssl')
                        , conn_timeout=dg('conn_timeout')
                        , op_timeout=dg('op_timeout'))
    


def setupMemcachedRamCache(self, portal):
    """ Replace RAMCaches with MemcachedManager """

    ramCaches = ['RAMCache', 'Cache_NavigationManager', 'CacheSetup_ResourceRegistryCache',
		 'Cache_searches','Cache_subscribers']

    for id, ram in portal.objectItems('RAM Cache Manager'):
        if id in ramCaches:
	    settings = ram.getSettings()
	    settings['servers'] = ('127.0.0.1:11211',)
	    title = ram.Title
	    portal.manage_delObjects(ids=[id])
	    factory = portal.manage_addProduct['MemcachedManager']
	    factory.manage_addMemcachedManager(id=id)
	    portal[id].manage_editProps(title, settings)
	    
	    
	
	
functions = {
    'disableMailForgottenPassword' : disableMailForgottenPassword,
    'setDateProperties' : setDateProperties,
    'configureContentTypes' : configureContentTypes,
    'setupDefaultLeftRightSlots':setupDefaultLeftRightSlots,
    'setupDefaultRSSFeeds' : setupDefaultRSSFeeds,
    'configureCache' : configureCache,
    'disableAnonymousJoin': disableAnonymousJoin,
    'setupLDAPUserFolder':setupLDAPUserFolder,
    'setNavigationProperties':setNavigationProperties,
    'setupControlledMarshall':setupControlledMarshall,
    'setupLanguageSettings':setupLanguageSettings,
    'setupMemcachedRamCache':setupMemcachedRamCache,
    'migrateReportsRSS2Topics' : migrateReportsRSS2Topics,
    }

class EEAGeneralSetup(SetupWidget):
    type = 'EEA Plone Admin and General Setup'

    description = """This applies a function to the site. These functions are some of the basic
set up features of a site. The chances are you will not want to apply these again. <b>Please note</b>
these functions do not have a uninstall function."""

    functions = functions

    def setup(self):
        pass

    def delItems(self, fns):
        out = []
        out.append(('Currently there is no way to remove a function', INFO))
        return out

    def addItems(self, fns):
        out = []
        for fn in fns:
            self.functions[fn](self, self.portal)
            out.append(('Function %s has been applied' % fn, INFO))
        return out

    def installed(self):
        return []

    def available(self):
        """ Go get the functions """
        return self.functions.keys()
