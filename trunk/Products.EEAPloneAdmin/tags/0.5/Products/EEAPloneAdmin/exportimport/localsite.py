import os
import re
import transaction
import codecs

from zope.interface import directlyProvides, directlyProvidedBy, alsoProvides
from zope.i18n import translate as realTranslate

from Acquisition import aq_parent, aq_inner, aq_base
from Globals import package_home, DevelopmentMode
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.browser.interfaces import INavigationRoot
from Products.Marshall.registry import getComponent
from Products.ZCatalog.ProgressHandler import ZLogHandler

from Products.EEAPloneAdmin.config import GLOBALS, EEA_LANGUAGES
from eea.translations import _ 
from eea.themecentre.interfaces import IThemeTagging, IThemeCentre, IThemeRelation

from valentine.gtranslate import translate as gtranslate

excludeFromNav = ('legal', 'quicklinks', 'address.html' )

# list of (path, portalType, translationText)
# translationText is None when we use the title of the object
translateFromSite = (('address.html', 'Document', None),
                     ('about-us/who/organisational-chart', 'Document', None),
                     ('about-us/who/staff-list', 'Document', 'EEA Staff list'),
                     ('legal', 'Folder', None),
                     ('legal/copyright', 'Folder', 'Copyright'),
                     ('legal/copyright/copyright-en', 'Document', None),                     
                     ('legal/disclaimer', 'Folder', None,),
                     ('legal/disclaimer/disclaimer-en', 'Document', None,),                     
                     ('legal/privacy', 'Folder', None),
                     ('legal/privacy/privacy-en', 'Document', None),                     
                     ('pressroom', 'Folder', 'Press Room'),
                     ('pressroom/newsreleases', 'Folder', 'News releases'),
                     ('pressroom/newsreleases/all-press-releases', 'RichTopic', 'News releases'),
                     ('quicklinks', 'Folder', None),
                     ('quicklinks/educational', 'Folder', 'Education'),                      
                     ('quicklinks/spotlight', 'Folder', None),                     
                     )

navigationRoot2NotPublish = ['eionet']


navigationMenues2Translate = { 'products' : ['reportsoverview', 'education', 'reports', 'more'],
                              'pressroom' : ['pressoverview', 'latestreports', 'highlights', 'pressreleases', 'presscontact'],
                              'abouteea' : [],
                              'contacts' : [],                               
                              }

structureNot2Translate = ['/www/SITE/about-us/jobs',
                          '/www/SITE/about-us/tenders',
                          '/www/SITE/sandbox',
                          '/www/SITE/forms',
                          '/www/SITE/themes/acidification',
                          '/www/SITE/themes/air_quality',
                          '/www/SITE/themes/information',
                          '/www/SITE/themes/management',
                          '/www/SITE/themes/nature',
                          '/www/SITE/themes/ozone',
                          '/www/SITE/themes/reporting', ]

untranslatedMessages = {}

def _useCorrectUrlForWhereWeAreRunningThis(context):
    url = context.absolute_url()
    ending = context.absolute_url(1)[4:]
    if 'localhost' in url:
        port = url.split(':')[2]
        port = port[:port.index('/')]
        url = 'http://dev1:%s/%s' % (port, ending)
    elif 'whiteshark' in url:
        url = 'http://www.webdev.eea.europa.eu/%s' % ending
    else:
        url = 'http://www.eea.europa.eu/' + ending

    return url

def getLanguages(context):
    plone = context.getSite()
    logger = context.getLogger('eea-localsite')
    # Use language codes in URL path for manual override
    lt = getToolByName(plone, 'portal_languages')
    defaultLang = lt.getDefaultLanguage()
    supportedLangs = DevelopmentMode and EEA_LANGUAGES or lt.getSupportedLanguages()
    if DevelopmentMode:
        logger.info("EEAPloneAdmin:local-sites: we are in DEBUG we only run for %s languages" % EEA_LANGUAGES)
    lt.manage_setLanguageSettings(defaultLang, supportedLangs, setPathN=True)
    logger.info("EEAPloneAdmin:local-sites: Enable 'Use language codes in URL path for manual override' in portal_languages")    
    siteLangView = plone.unrestrictedTraverse('@@translatedSitesLanguages')
    languages = [ (lang, foo) for lang, foo in siteLangView() if lang != 'en' ]
    return languages

def translate(msgid, target_language, output=False):
    translation = realTranslate(msgid, target_language=target_language)
    if translation == str(msgid):
        if msgid not in untranslatedMessages.get(target_language, {}).keys():
            if untranslatedMessages.get(target_language) is None:
                untranslatedMessages[target_language] = {}

            translation = untranslatedMessages.get(target_language).get(msgid)
            if translation is None:
                # we have run gtranslate so now we just keep it untranslated
                translation = str(msgid)

                # google translate doesn't have all languages
                if target_language not in ['tr','mt', 'hu']:
                    try:
                        translation = gtranslate(str(msgid), langpair="en|%s" % target_language)
                    except:
                        print "GTRANSLATE FAILED %s and msgid %s" % (target_language, msgid)

                untranslatedMessages.get(target_language)[msgid]  = translation
        translation = untranslatedMessages.get(target_language).get(msgid)            
    if type(translation) == type(''):
        return translation
    if type(translation) == type(u''):
        return translation.encode('utf8')
    # what do we have here?
    return str(translation)



def retagAllTranslations(context, languages):
    catalog = getToolByName(context, 'portal_catalog')
    langs = [ lang for lang, foo in languages
                       if lang != 'en' ]

    for b in catalog(object_provides='eea.themecentre.interfaces.IThemeTaggable',
                     Language='all'):
        
        if 'portal_factory' in b.getURL() or b.Language == 'en':
            continue
        obj = b.getObject()
        if b.getThemes == [] or b.getThemes == [None]:
            IThemeTagging(obj).tags = IThemeTagging(obj.getCanonical()).tags
        if IThemeCentre.providedBy(obj):
            IThemeRelation(obj).related = IThemeRelation(obj.getCanonical()).related
            print "%s : %s" % (obj.absolute_url(1), IThemeRelation(obj).related)
    
def setupTranslateSiteStructure(context):
    if context.readDataFile('eeaploneadmin_localsites.txt') is None:
        return

    plone = context.getSite()
    logger = context.getLogger('eea-localsite')

    languages = getLanguages(context)
    
    catalog = getToolByName(plone, 'portal_catalog')
    utils = getToolByName(plone, 'plone_utils')
    wf = getToolByName(plone, 'portal_workflow')
    folders = catalog(path = {'query': '/www/SITE',},
                      portal_type = ['Folder', 'ATFolder','RichTopic','Topic'],
                      Language='en'
                      )
    foldersByPath = {}
    
    for f in folders:
        url = f.getPath()
        for path in structureNot2Translate:
            if path in url:
                 break
        else:
            foldersByPath[url] = f
        
    folderPaths = foldersByPath.keys()
    folderPaths.sort()
    
    logger.info('PROGRESS: start: %s' % len(folderPaths))
    
    for lang, foo in languages:
        logger.info('PROGRESS: language %s' % lang)
        for path in folderPaths:
            f = foldersByPath[path]
            if 'portal_factory' in f.getURL():
                # we can have portal factory indexed objects which shouldn't be translated
                continue

            obj = f.getObject()

            translation = obj.getTranslation(lang)
            if translation is None:
                obj.addTranslation(lang)
                translation = obj.getTranslation(lang)
                transaction.savepoint()                
            
                originalState = wf.getInfoFor(obj, 'review_state')
                if originalState != wf.getInfoFor(translation, 'review_state'):
                    if originalState == 'published':
                        wf.doActionFor(translation, 'publish', comment='Initial publish by method setupLocalSite')
                    elif originalState == 'visible' and obj.portal_type != 'Folder':
                        wf.doActionFor(translation, 'submit', comment='Initial submit by method setupLocalSite')
                        wf.doActionFor(translation, 'show', comment='Initial show by method setupLocalSite')

                # we only translate title when creating translation
                # later we assume it's translated with imports and should
                # not be retranslated if the step is reimported
                title = _(obj.Title())
                translation.setTitle( translate(title, target_language=lang, output=True))

                # disable rename after creation
                translation.unmarkCreationFlag()
                
            # copy layout
            if obj.getProperty('layout') is not None:
                translation.setLayout(obj.getLayout())
            # copy interfaces of original
            directlyProvides(translation, directlyProvidedBy(obj))
            # disable translation of parent on next edit
            if hasattr(translation, '_lp_default_page'):
                delattr(translation, '_lp_default_page')
            # copy exclude from nav setting
            if hasattr(aq_base(obj), 'getExcludeFromNav'):
                try:
                    translation.setExcludeFromNav(obj.getExcludeFromNav())
                except:
                    logger.info("EEAPloneAdmin:local-sites: EXCLUDE-FROM-NAV-ERROR for %s" % obj.absolute_url())
            if obj.portal_type in ['Topic', 'RichTopic']:
                origCustFields = obj.getCustomViewFields()
                if list(origCustFields) != ['Title']:
                    #fields are already set use those
                    translation.setCustomViewFields(origCustFields)
                else:
                    # we only have default , we only need publish date
                    translation.setCustomViewFields(['EffectiveDate'])

            if utils.isDefaultPage(obj) and not utils.isDefaultPage(translation):
                parent = aq_parent(aq_inner(translation))
                parent.setDefaultPage(translation.getId())

            if obj.getProperty('navigationmanager_menuid') and translation.getProperty('navigationmanager_menuid') is None:
                translation.manage_addProperty('navigationmanager_menuid',
                                               obj.getProperty('navigationmanager_menuid'),
                                               'string')
                    
            translation.reindexObject()
        logger.info('PROGRESS: %s done' % lang)
        transaction.savepoint()        
    logger.info(" Structure translated")

def _fixNavigationUrls(portal_url, url, lang, site):
    template =  portal_url
    # if we have changed main urls to our dev we need to fix them back before running here
    # this is only need since we re-run the step on dev sites
    url = url.replace('http://dev1:8080/', 'http://www.eea.europa.eu/')
    url = url.replace('http://www.webdev.eea.europa.eu/', 'http://www.eea.europa.eu/')
    url = url.replace('http://dev1:19999/', 'http://www.eea.europa.eu/')    
    if lang != '':
        if portal_url.endswith('/'):
            portal_url = portal_url[:-1]
        template = '%s/%s/' % (portal_url,lang)

    menu_url = url.replace('http://www.eea.europa.eu/', template)
    menu_url = menu_url.replace('http://reports.eea.europa.eu/', template + 'reports')
    menu_url = menu_url.replace('http://reports.eea.europa.eu', template + 'reports')
    print "FIXED TRANSLATION url: %s" % menu_url
    return menu_url

def setupNavigationManager(context):
    if context.readDataFile('eeaploneadmin_localsites.txt') is None:
        return
    plone = context.getSite()
    logger = context.getLogger('eea-localsite')

    languages = getLanguages(context)

    navman = plone.portal_navigationmanager
    wf = getToolByName(plone, 'portal_workflow')

    if navman.getProperty('navigationmanager_fallback') is None:
        navman.manage_addProperty('navigationmanager_fallback',
                                  True,
                                  'boolean')
      

    site = getattr(plone, 'SITE')
    en = getattr(navman, 'default')
    navigationRoots = en.contentValues()
    en.setLanguage('en')
    portal_url = _useCorrectUrlForWhereWeAreRunningThis(plone)

    for lang, foo in languages:
        if not site.hasTranslation(lang):
            # a language that doesn't have local site
            continue
        translation = en.getTranslation(lang)
        if translation is None:
            en.addTranslation(lang)
            translation = en.getTranslation(lang)
            transaction.savepoint()
            wf.doActionFor(translation, 'publish', comment='Initial publish by method setupLocalSite')
            
        translation.unmarkCreationFlag()
        translation.setTitle( translate(_(en.Title()), target_language=lang) )

        homeUrl = _useCorrectUrlForWhereWeAreRunningThis(site.getTranslation(lang))
        translation.setUrl( _fixNavigationUrls(portal_url,homeUrl, '', site) )
        for root in navigationRoots:
            if root.Language() is None:
                root.setLanguage('en')
            translation = root.getTranslation(lang)
            if translation is None:
                root.addTranslation(lang)
                translation = root.getTranslation(lang)
                transaction.savepoint()
                if root.getId() not in navigationRoot2NotPublish:
                    wf.doActionFor(translation, 'publish', comment='Initial publish by method setupLocalSite')
                
            translation.unmarkCreationFlag()
            translation.setTitle( translate(_(root.Title()), target_language=lang))

            if root.getId() == 'eeahome':
                translation.setUrl( _fixNavigationUrls(portal_url, homeUrl, '', site) )
            else:
                translation.setUrl( _fixNavigationUrls(portal_url, root.getUrl(), lang, site) )
            translation.reindexObject()
            
            toTranslate = navigationMenues2Translate.get(root.getId(), None)
            for obj in root.contentValues():
                # if toTranslate is None then translate all otherwise what is in the list
                if toTranslate is None or obj.getId() in toTranslate:
                    translation = obj.getTranslation(lang)
                    if translation is None:
                        obj.addTranslation(lang)
                        translation = obj.getTranslation(lang)
                        wf.doActionFor(translation, 'publish', comment='Initial publish by method setupLocalSite')                            
                    translation.unmarkCreationFlag()
                    title = _(obj.Title())
                    translation.setTitle( translate(title, target_language=lang))
                    translation.setUrl( _fixNavigationUrls(portal_url, obj.getUrl(), lang, site) )
                    translation.reindexObject()

    # change main menu urls to the host we are using dev1 or webdev if we
    # are not on main site
    if 'www.eea.europa.eu' not in portal_url:
        for n in navigationRoots:
            n.setUrl( _fixNavigationUrls(portal_url, n.getUrl(), '', site) )
            for o in n.contentValues():
                o.setUrl( _fixNavigationUrls(portal_url, o.getUrl(), '', site) )
            
    logger.info("setupNavigationManager(): NavigationManager setup with local navigation")
    for lang, msgs in untranslatedMessages.items():
        pofile = codecs.open('/tmp/untranslated-navigation-%s.po' % lang, 'wb', encoding='utf8')
        for msgid, msgstr in msgs.items():
            pofile.writelines('msgid "%s"\nmsgstr "%s"\n\n' % (msgid, msgstr))

        pofile.close()

def setupLocalSites(context):

    if context.readDataFile('eeaploneadmin_localsites.txt') is None:
        return

    plone = context.getSite()
    logger = context.getLogger('eea-localsite')

    qi = getToolByName(plone, 'portal_quickinstaller')
    if not qi.isProductInstalled('RedirectionTool'):
        logger.info("EEAPloneAdmin:local-sites: RedirectionTool needs to be installed")
        return
        
    sendWorkflowEmails = plone.getProperty('send_workflow_emails')
    if sendWorkflowEmails is None:
        plone.manage_addProperty('send_workflow_emails', False, 'boolean')
        sendWorkflowEmails = True
    else:
        plone.manage_changeProperties(send_workflow_emails=False)
        
    languages = getLanguages(context)
    logger.info("EEAPloneAdmin:local-sites: setup local sites")    
    wf = getToolByName(plone, 'portal_workflow')
    utils = getToolByName(plone, 'plone_utils')

    local = getattr(plone, 'SITE')
    
    en = local
    title = _(u'European Environment Agency')

    if not hasattr(en, 'introduction'):
        en.invokeFactory('Document', id='introduction', title='Introduction')
    enIntro = en['introduction']

    if not hasattr(en, 'reports'):
        en.invokeFactory('Folder', id='reports', title='Reports')
        enReportsFolder = en['reports']
        enReportsFolder.invokeFactory('Document', id='reports', title='Reports')
        enReportsFolder.setDefaultPage('reports')
        enReportsFolder.invokeFactory('RSSFeedRecipe', id='reports-rss', title='Reports')
    enReportsFolder = en['reports']
    enReports = enReportsFolder['reports']
    enReportsRss = enReportsFolder['reports-rss']

    for lang, foo  in languages:
      alreadyDone = []
        
      if not DevelopmentMode and hasattr(plone, lang):
          # if we are in production we don't want to change already migrated local sites
          logger.info("Skipping language %s" % lang)
          continue
      
      translation = en.getTranslation(lang)
      if translation is None:
          en.addTranslation(lang)
          transaction.savepoint()
          translation = en.getTranslation(lang)
          translation.setId(lang)
          translation.unmarkCreationFlag()
          wf.doActionFor(translation, 'publish', comment='Initial publish by method setupLocalSite')
          alsoProvides(translation, INavigationRoot)
          logger.info("added localsite %s" % lang)

      if translation.getProperty('navigationmanager_site') is None:
          translation.manage_addProperty('navigationmanager_site',
                                         'default-%s' % lang,
                                         'string')

      translation.setLayout('frontpage_view')
      translation.setTitle( translate( title, target_language=lang))

      for path,portalType, msgId in translateFromSite:
          paths = path.split('/')
          obj = en
          for p in paths:
              obj = getattr(obj, p, None)
              if obj is None:
                  logger.info("EEAPloneAdmin:local-sites: WARNING No existing object %s" % path)
                  continue
              if obj in alreadyDone:
                  continue
              
              doc = obj.getTranslation(lang)
              if doc is None:
                  obj.addTranslation(lang)
                  doc = obj.getTranslation(lang)
                  doc.unmarkCreationFlag()
                  originalState = wf.getInfoFor(obj, 'review_state')
                  if originalState == 'published':
                      wf.doActionFor(doc, 'publish', comment='Initial publish by method setupLocalSite')
                  elif originalState == 'visible' and portalType != 'Folder':
                      wf.doActionFor(doc, 'submit', comment='Initial submit by method setupLocalSite')
                      wf.doActionFor(doc, 'show', comment='Initial show by method setupLocalSite')

                  doc.setTitle( translate( _(msgId or obj.Title()), target_language=lang))
                      
              if obj.getId() in excludeFromNav:
                  doc.setExcludeFromNav(True)

              if utils.isDefaultPage(obj):
                  parent = aq_parent(aq_inner(doc))
                  parent.setDefaultPage(doc.getId())

              if obj.getProperty('layout') is not None:
                  doc.setLayout(obj.getLayout())

              doc.reindexObject()
              alreadyDone.append(obj)
              transaction.savepoint()

      
      if not hasattr(translation, 'introduction'):
          xliffMarshaller = getComponent('atxliff')
          TITLE = re.compile("""&lt;tr&gt; \r\n          &lt;td width="100%" colspan="3" valign="top" class="TeaserBoxHeaderEEA30sec" align="center"&gt; \r\n            &lt;p class="head0w"&gt;(.*)&lt;/p&gt;\r\n          &lt;/td&gt;\r\n        &lt;/tr&gt;\r\n        """)
          TITLE_TO_REMOVE = re.compile("""&lt;tr&gt; \r\n          &lt;td width="100%" colspan="3" valign="top" class="TeaserBoxHeaderEEA30sec" align="center"&gt; \r\n            &lt;p class="head0w"&gt;.*&lt;/p&gt;\r\n          &lt;/td&gt;\r\n        &lt;/tr&gt;\r\n        """)
          try:
              filename = os.path.join(package_home(GLOBALS), 'exportimport', 'local-sites', 'introduction-%s.xlf' % lang)
              xliff = open(filename, 'r').read()
              newTitle = TITLE.findall(xliff)
              xliff = TITLE_TO_REMOVE.sub('', xliff)
              # set path to the english introduction
              xliff = xliff.replace('original="/index_html"', 'original="%s"' % '/'.join( enIntro.getPhysicalPath()))
              # in plone the body field is called text
              xliff = xliff.replace('id="body"', 'id="text"')
              # fix xhtml 
              xliff = xliff.replace('&lt;br/&gt;', '&lt;br /&gt;')
              # fix broke resolveuid
              # about-us/governance/intro - List of Management Board Members
              xliff = xliff.replace('resolveuid/3374ee862f322175658ae0109cfa4d8d', 'resolveuid/883275041407e0cfea1bdfe9961f2252')
              # about-us/governance/intro - List of Scientific Committee members
              xliff = xliff.replace('resolveuid/c48511d8d406547c9a6ce84ee94dc781', 'resolveuid/7957a7529ed5df88caa7ad40ee9859f2')
              xliffMarshaller.demarshall(enIntro, xliff, useTidy=True, keepHTML=False)
              intro = enIntro.getTranslation(lang)
              intro.unmarkCreationFlag()
              if len(newTitle) == 2:
                  intro.setTitle(newTitle[1])
              else:
                  logger.info("EEAPloneAdmin:local-sites title not changed for %s" % filename)
                  
          except:
              logger.info("EEAPloneAdmin:local-sites ERROR failed to load %s" % filename)                  


      if not hasattr(translation, 'reports'):
          rssTemplate = 'http://reports.eea.europa.eu/reports_local.rdf?select=public&image=yes&replang=%s'
          rssTitle = _(u'Reports')

          # reports folder
          enReportsFolder.addTranslation(lang)
          rfolder = enReportsFolder.getTranslation(lang)
          rfolder.unmarkCreationFlag()
          rfolder.setTitle( translate( rssTitle, target_language=lang))
          rfolder.manage_addProperty('navigationmanager_menuid',
                                         'products',
                                         'string')
          
          enReports.addTranslation(lang)
          doc = enReports.getTranslation(lang)
          doc.unmarkCreationFlag()
          doc.setTitle( translate( rssTitle, target_language=lang))
          rfolder.setDefaultPage('reports')

          enReportsRss.addTranslation(lang)
          rss = enReportsRss.getTranslation(lang)
          rss.unmarkCreationFlag()
          rss.setTitle( translate( rssTitle, target_language=lang))
          rss.setUrl('/%s/reports' % lang)
          rss.setFeedURL(rssTemplate % lang)
          rss.setLanguage(lang)
          rss.setEntriesSize(10000)
          rss.setEntriesWithDescription(0)
          transaction.savepoint()
          try:
              rss.reindexObject()
          except:
              logger.info("EEAPloneAdmin:local-sites ERROR feed %s" % rss.getFeedURL())
              print "EEAPloneAdmin:local-sites ERROR feed %s" % rss.getFeedURL()
              
          doc.setRelatedItems(rss.UID())
          wf.doActionFor(doc, 'publish', comment='Initial publish by method setupLocalSite')
          
    setupTranslateSiteStructure(context)
    setupNavigationManager(context)
    setupLocalRDFRepositories(context)
    themecentreFix(context)
    importTranslations(context)
    setupRetagAllTranslations(context)
    fixPromotion(context)
    fixLangIndependentFields(context)

    catalog = getToolByName(plone, 'portal_catalog')
    # catalog.manage_catalogReindex redirects so we do it here
    pgthreshold = catalog._getProgressThreshold()
    handler = (pgthreshold > 0) and ZLogHandler(pgthreshold) or None
    catalog.refreshCatalog(clear=1, pghandler=handler)
    
    plone.manage_changeProperties(send_workflow_emails=sendWorkflowEmails)
    logger.info("LOCAL-SITES are up online")
    
def setupRetagAllTranslations(context):
    if context.readDataFile('eeaploneadmin_localsites.txt') is None:
        return

    plone = context.getSite()
    logger = context.getLogger('eea-localsite')

    languages = getLanguages(context)
    retagAllTranslations(plone, languages)
    logger.info("setupRetagAllTranslations():  Translations re tagged")
    
def setupLocalRDFRepositories(context):

    if context.readDataFile('eeaploneadmin_localsites.txt') is None:
        return

    plone = context.getSite()
    logger = context.getLogger('eea-localsite')
    wf = getToolByName(plone, 'portal_workflow')
    
    enRDFRepo = plone.SITE.themes['rdf-repository']
    siteLangView = plone.unrestrictedTraverse('@@translatedSitesLanguages')
    languages = getLanguages(context)


    
    for id, ob in enRDFRepo.objectItems():
        if 'reports_' in id:
            theme = IThemeTagging(ob).tags[0]
            rssTemplate = 'http://reports.eea.europa.eu/reports_local.rdf?select=public&image=yes&replang=%s&theme=%s'
            rssTitle = _(u'Reports')
            newRss = oldRss = 0
            for lang, foo in languages:
                translation = ob.getTranslation(lang)
                if translation is None:
                    ob.addTranslation(lang)
                    translation = ob.getTranslation(lang)
                    transaction.savepoint()
                    newRss += 1
                else:
                    oldRss += 1
                    
                IThemeTagging(translation).tags = IThemeTagging(ob).tags
                translation.unmarkCreationFlag()
                translation.setTitle( translate( rssTitle, target_language=lang))
                translation.setUrl('/%s/themes/%s/reports' % (lang, theme))
                rssUrl = rssTemplate % (lang, theme)
                translation.setFeedURL(rssUrl)
                translation.setLanguage(lang)
                translation.setEntriesSize(10000)
                translation.setEntriesWithDescription(0)
                translation.updateFeed()
                if wf.getInfoFor(translation, 'review_state') != 'published':
                    wf.doActionFor(translation, 'publish', comment='Initial publish by method setupLocalRDFRepositories')
            logger.info("setupLocalRDFRepositories(): configured %s new and %s old RSSFeedRecipe for theme:%s" % (newRss, oldRss, theme))

def fixPromotion(context):
    """ Fix link for glossary promotion so it goes to local. """
    
    if context.readDataFile('eeaploneadmin_localsites.txt') is None:
        return

    plone = context.getSite()
    logger = context.getLogger('eea-localsite')
    wf = getToolByName(plone, 'portal_workflow')
    
    siteLangView = plone.unrestrictedTraverse('@@translatedSitesLanguages')
    languages = getLanguages(context)
    qlinks = plone.SITE.quicklinks

    for lang, foo in languages:
        promotion = qlinks.educational['glossary-learn-about-environmental-terms']
        translation = promotion.getTranslation(lang)
        if translation is not None:
            translation.setUrl('http://glossary.%s.eea.europa.eu/' % lang)
            translation.reindexObject()

    for obj in qlinks.educational.objectValues():
        for lang, foo in languages:
            translation = obj.getTranslation(lang)
            if translation is not None:
                if wf.getInfoFor(translation, 'review_state') != 'published' and wf.getInfoFor(obj, 'review_state') == 'published':
                    wf.doActionFor(translation, 'publish', comment='Initial publish by method localsite.fixPromotion')
                

toTranslatefromG = { 'Animations' : 'Animations',
                     'Images' : 'Images',
                     'Interactive Maps' : 'Interactive Maps',
                     'Interviews' : 'Interviews',
                     'Presentations' : 'Presentations',
                     'Videos' : 'Videos',
                     'Other' : 'Other',
                     'Menu' : 'Menu',
                     }

def getTranslationsFromGoogle(context):
    if context.readDataFile('eeaploneadmin_localsites.txt') is None:
        return

    plone = context.getSite()
    logger = context.getLogger('eea-localsite')
    wf = getToolByName(plone, 'portal_workflow')
    
    siteLangView = plone.unrestrictedTraverse('@@translatedSitesLanguages')
    languages = getLanguages(context)

    for lang, foo in languages:
        pofile = codecs.open('/tmp/gtranslated-%s.po' % lang, 'wb', encoding='utf8')
        for msgid, msgstr in toTranslatefromG.items():
            try:
                pofile.writelines('\nmsgid "%s"\nmsgstr "%s"\n\n' % (msgid,  gtranslate(msgstr, langpair="en|%s" % lang)))
            except:
                logger.info("FAILED for lang %s msgstr %s" % (lang, msgstr))
        pofile.close()
    #run this later
    # cd eea.translations/eea/translations/i18n
    # ls /tmp/gtranslated-* | awk -F- '{split($2, b, "."); print "cat /tmp/gtranslated-"b[1]".po >> "b[1]"/LC_MESSAGES/eea.translations.po" ;}' | /bin/sh
    # ls | awk '{ print "pocompile "$1"/LC_MESSAGES/eea.translations.po "$1"/LC_MESSAGES/eea.translations.mo" ;}' | /bin/sh


navigationItems2RemoveFromTranslatedMenues = ['chemicals', 'coasts-and-seas', 'fisheries', 'industry']
themecentres2MovePressIn = ['regions',]

def themecentreFix(context):
    if context.readDataFile('eeaploneadmin_localsites.txt') is None:
        return

    plone = context.getSite()
    logger = context.getLogger('eea-localsite')
    wf = getToolByName(plone, 'portal_workflow')
    catalog = getToolByName(plone, 'portal_catalog')    
    siteLangView = plone.unrestrictedTraverse('@@translatedSitesLanguages')
    languages = getLanguages(context)

    navman = plone.portal_navigationmanager.default

    for lang, foo in languages:
        local = getattr(plone, lang, None)
        if local is None:
            continue
        highlights = local['highlights']
        pressReleases = local['pressroom']['newsreleases']
        
        for f in local.themes.objectValues():
            default = f.getCanonical().getDefaultPage()
            if default is not None and hasattr(f, default):
                intro = f[default]
                f.setDefaultPage(intro.getId())
                intro.setLayout('themecentre_view')
            else:
                logger.info('No intro page for %s' % f.absolute_url())
            if f.getId() in themecentres2MovePressIn:
                # find all highlights and pressreleases in this theme centre and move theme
                # out since the themecentre is unpublished
                press = catalog(path='/'.join(f.getPhysicalPath()),
                                portal_type=['Highlight','PressRelease'],
                                Language='all' )
                
                for b in press:
                    obj = b.getObject()
                    parent = aq_parent(obj)
                    cut = parent.manage_cutObjects(ids=[b.getId,])
                    if b.portal_type == 'Highlight':
                        highlights.manage_pasteObjects(cut)
                    elif b.portal_type == 'PressRelease':
                        pressReleases.manage_pasteObjects(cut)
                        
            if not hasattr(aq_base(f), 'reports') and hasattr(aq_base(f.getCanonical()), 'reports'):
                reportRSS =  getattr(local.themes['rdf-repository'], 'reports_%s' % f.getId(), None)
                if reportRSS is not None:
                    reportsEN = f.getCanonical()['reports']
                    reportsEN.addTranslation(lang)
                    doc = reportsEN.getTranslation(lang)
                    transaction.savepoint()
                    doc.setTitle( translate(_('Reports'), target_language=lang))
                    doc.setRelatedItems(reportRSS.UID())
                    if wf.getInfoFor(reportsEN, 'review_state') == 'published':
                        wf.doActionFor(doc, 'publish', comment='Unpublish on local site migration')
                    
        if navman.hasTranslation(lang):
            try:
                themes = navman.getTranslation(lang)['themes']
                logger.info('Removing themes in %s' % themes.absolute_url())
                themes.manage_delObjects(ids=navigationItems2RemoveFromTranslatedMenues)
            except:
                logger.info('FAILED Removing menu themes %s' % lang)                

def importTranslations(context):
    if context.readDataFile('eeaploneadmin_localsites.txt') is None:
        return

    plone = context.getSite()
    logger = context.getLogger('eea-localsite')
    wf = getToolByName(plone, 'portal_workflow')
    xliffMarshaller = getComponent('atxliff')
    
    siteLangView = plone.unrestrictedTraverse('@@translatedSitesLanguages')
    languages = getLanguages(context)

    for lang, foo in languages:
        filename = os.path.join(package_home(GLOBALS), 'exportimport', 'local-sites', 'EEA-2008-0037-00-00-EN%s.xlf' % lang.upper())
        xliff = open(filename, 'r').read()
        # solves #1968, we may change this to regex to be sure we only change links we want to
        xliff = xliff.replace('http://glossary.eea.europa.eu/results', 'http://glossary.%s.eea.europa.eu/'% lang)
        xliff = xliff.replace('http://www.eea.europa.eu/quicklinks/educational', '/%s/quicklinks/educational'% lang)
        xliff = xliff.replace('http://www.eea.europa.eu/themes', '/%s/themes'% lang)
        xliff = xliff.replace('<a href="../../organisation/organigram.html"', '<a href="resolveuid/103d4eb4c235fc7e8c60cb799af3cdbd"')
        xliff = xliff.replace('<a href="../../organisation/staff.html"', '<a href="resolveuid/256c65bd4fd03cbad2b114885ebe1f60"')
        xliff = xliff.replace('<a href="../organisation/staff.html"', '<a href="resolveuid/256c65bd4fd03cbad2b114885ebe1f60"')        
        REPORTS_URL = re.compile("""<target>\s*http://reports.eea.europa.eu/\s*</target>""")
        xliff = REPORTS_URL.sub('<target>/%s/reports</target>' % lang, xliff)
        xliffMarshaller.demarshall(plone.SITE, xliff, useTidy=True, keepHTML=True,
                                   sync_workflow=True, validatetranslations=True,
                                   dump2po='xliff-%s.po' % lang)
        logger.info("Imported %s" % filename)
    logger.info("Translations Imported.")

def reindexIsEmptyIndex(context):
    """ reindex is_empty for all topics and folders. """

    if context.readDataFile('eeaploneadmin_localsites.txt') is None:
        return

def fixLangIndependentFields(context):
    """ copy language independent fields for PressRelease/Highlights and
    Promotions since there are some that didn't get the value correct. """
    if context.readDataFile('eeaploneadmin_localsites.txt') is None:
        return

    plone = context.getSite()
    logger = context.getLogger('eea-localsite')
    catalog = getToolByName(plone, 'portal_catalog')

    for b in catalog( portal_type=['PressRelease', 'Highlight', 'Promotion'],
                      Language='en'):
        canonical = b.getObject().getCanonical()
        schema = canonical.Schema()
        independent_fields = schema.filterFields(languageIndependent=True)

        for lang, t in canonical.getTranslations().items():
            translation = t[0]
            for field in independent_fields:
                accessor = field.getEditAccessor(canonical)
                if not accessor:
                    accessor = field.getAccessor(canonical)
                data = accessor()
                translation_mutator = getattr(translation, field.translation_mutator)
                translation_mutator(data)
            translation.reindexObject()
    logger.info("Copied language independent fields for PressRelease,Highlight, Promotion ")

    
