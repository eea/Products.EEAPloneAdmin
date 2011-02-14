import sys
import time
import codecs
import transaction
from zope.i18n import translate as realTranslate
from valentine.gtranslate import translate as gtranslate
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.browser.interfaces import INavigationRoot
from zope.interface import directlyProvides, directlyProvidedBy, alsoProvides
from zope.event import notify
from zope.app.event.objectevent import ObjectModifiedEvent
from Products.NavigationManager.sections import INavigationSectionPosition
from p4a.subtyper.interfaces import ISubtyper
from zope.component import getUtility
from zope.component import queryMultiAdapter
from eea.facetednavigation.interfaces import ICriteria
from eea.faceted.inheritance.interfaces import IHeritorAccessor
from Products.CMFCore.WorkflowCore import WorkflowException

# Logging
import logging
logger = logging.getLogger('EEAPloneAdmin.setupmethods')
info = logger.info
info_exception = logger.exception

def testTimeoutA(self):
    time.sleep(600)
    return 'done'

def bulkDeleteSpam(self):
    info('INFO: starting bulk delete spam')
    context = self
    request = self.REQUEST
    debug = request.get('debug', None)

    # Define context
    qevents_container = context.SITE.events.submitted
    qevents_container_ids = qevents_container.objectIds()

    # Indetify spam objects
    spam = []
    for ob_id in qevents_container_ids:
        count = ob_id.count('-')
        if count > 0:
            if count == 1 and ob_id[-2] == '-' and ob_id[-1].isdigit():
                spam.append(ob_id)
        else:
            spam.append(ob_id)

    # Delete spam
    trans_count = 0
    for ob_id in spam:
        trans_count += 1
        if debug:
            info('INFO: deleting %s' % ob_id)
        else:
            qevents_container.manage_delObjects([ob_id])
        if trans_count % 20 == 0:
            info('INFO: %s deleted spam' % str(trans_count))
            transaction.commit()

    info('INFO: Done bulk delete spam')

def bulkChangeState(self):
    """ Bulk change state of objects using multi-transactions """
    info('INFO: starting bulk state change')
    context = self
    request = self.REQUEST
    targets = []
    wftool = getToolByName(context, 'portal_workflow')

    #Get target objects
    cat = getToolByName(context, 'portal_catalog')
    query = {'path': '/www/SITE/soer/countries'}
    brains = cat(**query)
    targets = [brain.getObject() for brain in brains]

    #Change state of target objects
    debug = request.get('debug', None)
    done = 0
    for ob in targets:
        if debug:
        #Debug mode
            info('Target: %s' % ob.absolute_url())
        else:
        #Change state logic
            try:
                old_state = wftool.getInfoFor(ob, 'review_state')

                #Set Effective Date as today
                ob.setEffectiveDate(DateTime())

                if old_state == 'published':
                    pass
                elif old_state == 'visible':
                    wftool.doActionFor(ob, 'publish',
                                       comment='SOER2010 launch. Set by migration script.')
                elif old_state == 'webqa_pending':
                    wftool.doActionFor(ob, 'publish',
                                       comment='SOER2010 launch. Set by migration script.')
                elif old_state == 'new':
                    wftool.doActionFor(ob, 'publish',
                                       comment='SOER2010 launch. Set by migration script.')
                elif old_state == 'draft':
                    wftool.doActionFor(ob, 'publish',
                                       comment='SOER2010 launch. Set by migration script.')
                elif old_state == 'pending':
                    wftool.doActionFor(ob, 'publish',
                                       comment='SOER2010 launch. Set by migration script.')
                else:
                    info('ERROR: state not covered, %s' % ob.absolute_url())
                    info('ERROR: old state: %s' % old_state)

                cat.reindexObject(ob)
            except WorkflowException, err:
                info('ERROR: state not changed for %s' % ob.absolute_url())
                info_exception('Exception: %s ', err)

        if done % 2 == 0:
            # Commit subtransaction for every 2nd processed item
            transaction.commit()
            info('Subtransaction committed to zodb.')

    info('Done changing state.')


def printCheckInterval(self):
    """ Get/set python check interval """
    request = self.REQUEST
    interval = request.get('interval', None)

    if interval:
        return sys.setcheckinterval(int(interval))
    else:
        return sys.getcheckinterval()

def bulkReindexObjects(self, brains):
    """ Bulk reindex objects using multi-transactions """
    info('INFO: Start reindexing')
    done = 0
    for brain in brains:
        try:
    	    done += 1
    	    info('INFO: reindexing %s', brain.getId)
    	    obj = brain.getObject()
    	    obj.reindexObject()
    	    if done % 10 == 0:
    		transaction.commit()
    		info('INFO: Subtransaction committed to zodb')
	except Exception, err:
    	    info('ERROR: error during reindexing')
    	    info_exception('Exception: %s ', err)
    info('INFO: Done reindexing')

def reindexAllIndicators(self):
    """ Incremental commit and indexing of indicators """
    context = self
    cat = getToolByName(context, 'portal_catalog')
    wf = getToolByName(context, 'portal_workflow')

    all_brains = cat.searchResults({'show_inactive':True,
                                    'language':'ALL',
                                    'object_provides':'eea.indicators.content.interfaces.ISpecification'})

    done = 0
    try:
        for brain in all_brains:
            done += 1
            content = brain.getObject()
            content.reindexObject()
            msg = "(%d / %d) reindexed indicator: %s" % (done, len(all_brains), "/".join(content.getPhysicalPath()))
            info(msg)
            for asses in content.objectValues('Assessment'):
                asses.reindexObject()
                msg = "Reindexed assessment"
                info(msg)
            if done % 10 == 0:
                # Commit subtransaction for every 10th processed item
                transaction.commit()
                info('Subtransaction committed to zodb.')
    except Exception, err:
        info('ERROR: error during reindexing of an indicator')
        info_exception('Exception: %s ', err)
    info('Done reindexing.')

def setIndicatorsFacets(self):
    context = self
    cat = getToolByName(context, 'portal_catalog')
    wf = getToolByName(context, 'portal_workflow')

   # Example:
   #    >>> fid = portal.invokeFactory('Folder', 'heritor')
   #    >>> heritor = portal._getOb(fid)
   #    >>> subtyper.change_type(heritor, 'eea.faceted.inheritance.FolderFacetedHeritor')
   #
   #  Connect heritor with ancestor
   #
   #    >>> request = heritor.REQUEST
   #    >>> IHeritorAccessor(heritor).ancestor = '/plone/ancestor'
   #    >>> IHeritorAccessor(heritor).ancestor
   #    '/plone/ancestor'

    pubs=cat.searchResults({'id':'indicators', 'path': '/www/SITE/themes/'})
    subtyper = getUtility(ISubtyper)
    printed = "Indicators sections for new IMSv3\n"

    for indf in pubs:
        indfo=indf.getObject()
        printed = printed + indfo.absolute_url() + '\n'
        subtyper.change_type(indfo, 'eea.faceted.inheritance.FolderFacetedHeritor')
        IHeritorAccessor(indfo).ancestor = '/www/SITE/themes/indicators-ancestor'
        try:
            wf.doActionFor(indfo, 'publish',comment='done by setupmethods for new indicators ims.')
        except:
            printed = printed + 'no possible to publish\n'
        indfo.reindexObject()

    #oldpages=cat.searchResults({'id':'indicators-old','meta_type':'Folder','path': '/www/SITE/themes/'})
    #for indf in oldpages[:10]:
    #    indfo=indf.getObject()
    #    printed = printed + indfo.absolute_url() + '\n'
        #wf.doActionFor(indfo, 'hide',comment='done by setupmethods for new indicators ims.')
        #indfo.reindexObject()

    return printed

def createIndicatorSections(self):
    context = self
    cat = getToolByName(context, 'portal_catalog')
    wf = getToolByName(context, 'portal_workflow')

    pubs=cat.searchResults({ 'object_provides' : 'eea.themecentre.interfaces.IThemeCentre','path': '/www/SITE/themes/' })

    printed = "Indicators sections for new IMSv3"

    #image preview for indicators
    img_preview = context.manage_copyObjects(["img_preview"])

    for theme in pubs:
        themeItem=theme.getObject()
        printed = printed + themeItem.absolute_url()
        themeId = theme.id
        printed = printed + 'fixing a few things in %s' % themeId
        if hasattr(themeItem, 'indicators'):
            try:
                printed = printed + '\nfixing indicators\n'
                #rename old indicators page
                themeItem.manage_renameObject('indicators','indicators-old')
                oldindpage=themeItem.manage_cutObjects(["indicators-old"])
                oldpage = themeItem['indicators-old']
                #create new indicator section
                #create folder and preview image in it
                themeItem.invokeFactory('Folder', id='indicators')
                indf = themeItem['indicators']
                #indf.setLayout('dc_view')
                indf.setTitle('Indicators')
                # copy old intro text in rich topic area
                #indf.setRichContent(oldpage.getText())
                INavigationSectionPosition(indf).section = 'data-center-services'
                indf.unmarkCreationFlag()
                indf.manage_pasteObjects(img_preview)
                indf.manage_pasteObjects(oldindpage)
                oldpage = indf['indicators-old']
                oldpage.setTitle('Indicators - old')
            except:
                printed = printed + "ERROR on theme: " + themeId

            #publish
            # Make sure it's published
            try:
                wf.doActionFor(indf, 'publish',comment='done by setupmethods for new indicators ims.')
            except:
                pass
            #reindex
            indf.reindexObject()


            #retract old page
            # Make sure it's published
            try:
                wf.doActionFor(oldpage, 'hide',comment='done by setupmethods for new indicators ims.')
            except:
                pass
            #reindex
            oldpage.reindexObject()

        else:
            printed = printed + 'no indicators page found\n'

        #printed 'reindexing'
        #themeItem.reindexObject();

    return printed

def createRODListing(self):
    context = self
    cat = getToolByName(context, 'portal_catalog')
    wf = getToolByName(context, 'portal_workflow')

    pubs=cat.searchResults({ 'object_provides' : 'eea.themecentre.interfaces.IThemeCentre','path': '/www/SITE/themes/' })

    printed = "Rod listing"

    for theme in pubs:
        themeItem=theme.getObject()
        themeId = theme.id
        if not hasattr(themeItem, 'reporting-obligations'):
            printed = printed + '\n adding reporting obligations page to ' + themeId
            themeItem.invokeFactory('Document', id='reporting-obligations')
            rod = themeItem['reporting-obligations']
            rod.setLayout('rod_listing')
            rod.setTitle('Countries reporting obligations')
            INavigationSectionPosition(rod).section = 'data-center-services'
            rod.unmarkCreationFlag()
            # Make sure it's published
            try:
                wf.doActionFor(rod, 'publish',comment='published by script for data centres setup.')
            except:
                pass
            rod.reindexObject()
        else:
            printed = printed + '\n rod listing exists for ' + themeId

    return printed

def createDCPage(self):
    """ create dc page for non-Datacentre sites """
    context = self
    cat = getToolByName(context, 'portal_catalog')
    wf = getToolByName(context, 'portal_workflow')

    pubs=cat.searchResults({ 'object_provides' : 'eea.themecentre.interfaces.IThemeCentre','path': '/www/SITE/themes/' })

    printed = "create dc page for not dc sites"

    for theme in pubs:
        themeItem=theme.getObject()
        themeId = theme.id
        if not hasattr(themeItem, 'dc'):
            printed = printed + '\n adding dc page to ' + themeId
            themeItem.invokeFactory('Document', id='dc')
            dc = themeItem['dc']
            dc.setLayout('dc_view')
            dc.setTitle('Data services overview')
            INavigationSectionPosition(dc).section = 'data-center-services'
            dc.unmarkCreationFlag()
            # Make sure it's published
            try:
                wf.doActionFor(dc, 'publish',comment='published by script for data centres setup.')
            except:
                pass
            dc.reindexObject()
        else:
            printed = printed + '\n dc listing exists for ' + themeId

    return printed

def interactiveMapsPromotions(self):
    """find interactive maps via promotions """
    context = self
    cat = getToolByName(context, 'portal_catalog')
    wf = getToolByName(context, 'portal_workflow')

    pubs=cat.searchResults({ 'portal_type' : 'Promotion'})

    printed = "Promotions:"

    for pub in pubs:
        pubo=pub.getObject()
        printed = printed + pub.review_state + ' ' + pubo.absolute_url() + '\n'
        if INavigationSectionPosition(pubo).section:
            printed = printed +'Sections: ' + INavigationSectionPosition(pubo).section + '\n'
        printed = printed + '**************************************************\n'

    return printed

def sendModifiedForObjects(self):
    context = self
    cat = getToolByName(context, 'portal_catalog')
    pubs=cat.searchResults({ 'id' : 'dm' })
    printed=""
    for pub in pubs:
        pubo=pub.getObject()
        printed = printed + pub.id + "\n modified"
        pubo.reindexIsEmptyForSite(pubo, query={'path' : '/'.join(pubo.getPhysicalPath()),
                                                'Language' : 'all' })
        notify(ObjectModifiedEvent(pubo))
    return printed

def hideMapsDataFolders(self):
    context = self
    cat = getToolByName(context, 'portal_catalog')
    wf = getToolByName(context, 'portal_workflow')
    pubs=cat.searchResults({ 'id' : 'maps-and-graphs' ,'path': '/www/SITE/themes/'})
    printed="STARTED"
    for pub in pubs:
        pubo=pub.getObject()
        printed = printed + pub.id + "\n modified"
        try:
            wf.doActionFor(pubo, 'showPublicDraft', comment='Data centre setup. Hiding old structure. done by method.')
        except:
            printed = printed + '/'.join(pubo.getPhysicalPath()) + "\n exception"
        notify(ObjectModifiedEvent(pubo))
    return printed

def setNavContext(self):
    """moving the data centric object under data centre section. """
    context = self
    cat = getToolByName(context, 'portal_catalog')
    pubs=cat.searchResults({ 'id' : 'datasets' ,'path': '/www/SITE/themes/'})
    printed="STARTED"
    for pub in pubs:
        pubo=pub.getObject()
        printed = printed + pub.id + "\n modified"
        printed = printed + '/'.join(pubo.getPhysicalPath()) + "\n"
        notify(ObjectModifiedEvent(pubo))
        navContext = INavigationSectionPosition(pubo)
        navContext.section = 'data-center-services'
        notify(ObjectModifiedEvent(pubo))
        printed = printed + '  SECTION: ' + navContext.section
    return printed

def setNavContextForLiveMaps(self):
    """moving the live maps objects under data centre section. """
    context = self
    cat = getToolByName(context, 'portal_catalog')
    pubs=cat.searchResults({ 'navSection' : 'quicklinks' })
    printed="STARTED\n"
    for pub in pubs:
        pubo=pub.getObject()
        printed = printed + pub.id + "\n modified \n"
        printed = printed + '/'.join(pubo.getPhysicalPath()) + "\n"
        #notify(ObjectModifiedEvent(pubo))
        navContext = INavigationSectionPosition(pubo)
        #navContext.section = 'data-center-services'
        #notify(ObjectModifiedEvent(pubo))
        printed = printed + '  SECTION: ' + navContext.section  + "\n"
    return printed

def setupPublicationsFolder(self):
    context=self
    printed=""
    lt = getToolByName(context, 'portal_languages')
    wf = getToolByName(context, 'portal_workflow')

    defaultLang = lt.getDefaultLanguage()
    supportedLangs = lt.getSupportedLanguages()

    printed=printed+context.id+"\n"

    for lang in supportedLangs:
        en=context
        translation = en.getTranslation(lang)
        printed=printed+"\n"+lang
        if translation is None:
            en.addTranslation(lang)
            printed=printed+"\n"+lang+" added missing translation"
            translation = en.getTranslation(lang)
            translation.unmarkCreationFlag()
            wf.doActionFor(translation, 'publish', comment='Initial auto publish by method for new publication system')
            printed=printed+"\n published"
            #alsoProvides(translation, INavigationRoot)

        translation.setLayout('folder_summary_search_view')
        printed=printed+"\n setting layout with search"
        #translation.setTitle( translate( title, target_language=lang))
        #printed=printed+"\n translate title"

    return printed

def setupPublicationsFolderRoot(self):
    context=self
    printed=""
    lt = getToolByName(context, 'portal_languages')
    wf = getToolByName(context, 'portal_workflow')

    defaultLang = lt.getDefaultLanguage()
    supportedLangs = lt.getSupportedLanguages()

    printed=printed+context.id+"\n"

    for lang in supportedLangs:
        en=context
        translation = en.getTranslation(lang)
        printed=printed+"\n"+lang
        if translation is not None:
            translation.setDefaultPage('latest')
            #alsoProvides(translation, INavigationRoot)
            printed=printed+"\n default page set to latest rich topic"
        else:
            printed=printed+"\n"+lang+" not translated"
    return printed

untranslatedMessages = {}

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

def translateObject(self,templateview, navigationroot=False):
    context=self
    request = context.REQUEST
    printed=""
    mytitle=context.title
    print mytitle
    lt = getToolByName(context, 'portal_languages')
    wf = getToolByName(context, 'portal_workflow')

    defaultLang = lt.getDefaultLanguage()
    supportedLangs = lt.getSupportedLanguages()

    print context.id+"\n"

    for lang in supportedLangs:
        en=context
        translation = en.getTranslation(lang)
        print "\n processing language: "+lang
        if translation is None:
            en.addTranslation(lang)
            print "\n"+lang+" added missing translation"
            translation = en.getTranslation(lang)
            translation.unmarkCreationFlag()
            wf.doActionFor(translation, 'publish', comment='Initial auto publish by translateObject method')
            print "\n published"

        if navigationroot:
            alsoProvides(translation, INavigationRoot)
            print "\n INavigationRoot assigned"
        translation.setLayout(templateview)
        print "\n setting layout to: " + templateview
        transtitle = translate( mytitle, target_language=lang)
        translation.setTitle( transtitle)
        print "\n translate title to: " + transtitle

    return "object translated operation completed: " +  str(untranslatedMessages)

def getTranslationsFromGoogle(self, toTranslatefromG):
    context = self
    lt = getToolByName(context, 'portal_languages')
    wf = getToolByName(context, 'portal_workflow')
    translationslist = []
    defaultLang = lt.getDefaultLanguage()
    languages = lt.getSupportedLanguages()

    for lang in languages:
        pofile = codecs.open('/tmp/gtranslated-%s.po' % lang, 'wb', encoding='utf8')
        for msgid, msgstr in toTranslatefromG.items():
            try:
                translated = gtranslate(msgstr, langpair="en|%s" % lang)
                pofile.writelines('\nmsgid "%s"\nmsgstr "%s"\n\n' % (msgid,  translated ))
                translationslist.append((msgid, lang ,translated))
            except:
                translationslist.append(("FAILED for lang %s msgstr %s" % (lang, msgstr)))
        pofile.close()
    return translationslist
    # run this later
    # cd eea.translations/eea/translations/i18n
    # ls /tmp/gtranslated-* | awk -F- '{split($2, b, "."); print "cat /tmp/gtranslated-"b[1]".po >> "b[1]"/LC_MESSAGES/eea.translations.po" ;}' | /bin/sh
    # ls | awk '{ print "pocompile "$1"/LC_MESSAGES/eea.translations.po "$1"/LC_MESSAGES/eea.translations.mo" ;}' | /bin/sh



def importSubscribers(self):
    import transaction

    info('INFO: Starting import of subscribers')
    portal = self.portal_url.getPortalObject()
    backup = portal['SITE']['sandbox']['testnewsletter']['subscribers']
    target = portal['SITE']['subscription']['eea_main_subscription']['subscribers']
    
    unprocessed_ids = []

    i = 0
    ids = target.objectIds()
    for subscriber in backup.objectValues():
        if subscriber.id in ids:
            info("INFO: Skipping %s %s", subscriber.email, subscriber.id)
            unprocessed_ids.append(subscriber.id)
            continue

        target.invokeFactory('Subscriber', subscriber.id)
        info('INFO: %s adding %s', str(i), subscriber.email)
        s = target[subscriber.id]
        s.email = subscriber.email
        s.format = subscriber.format
        s.active = subscriber.active
        s.bounces = []

        if (i % 10) == 0:
            transaction.commit()
        i += 1

    info('INFO: Done import subscribers')
    return str(unprocessed_ids)

def setActiveSubscribers(self):
    import transaction

    info('INFO: Starting import of subscribers')
    portal = self.portal_url.getPortalObject()
    backup = portal['SITE']['sandbox']['testnewsletter']['subscribers']
    target = portal['SITE']['subscription']['eea_main_subscription']['subscribers']
    
    all_emails = []
    duplicate_email_ids = []

    i = 0
    for subscriber in backup.objectValues():
        id = subscriber.id
        s = target.get(id)
        if not s:
            info('INFO: original id %s is not found in new folder', id)
            continue

        s.active = subscriber.active
        s.email = subscriber.email
        s.format = subscriber.format
        s.bounces = []
        s._p_changed = True
        info("INFO: set %s to %s (using %s)" % (s.id, s.active, subscriber.active))

        if (s.email in all_emails):
            duplicate_email_ids.append(s.id)
        else:
            all_emails.append(s.email)

        if (i % 10) == 0:
            transaction.commit()
        i += 1

    info("INFO: the following ids are duplicated emails, should be erased %s", duplicate_email_ids)
    transaction.commit()
    info('INFO: Done reset subscribers active status')
    return str(duplicate_email_ids)


def sendMistakeEmail(self):
    import email as emailutils

    portal = self.portal_url.getPortalObject()
    mailhost = portal.MailHost
    subscribers = portal['SITE']['subscription']['eea_main_subscription']['subscribers']
    theme = portal['SITE']['subscription']['eea_main_subscription']

    subject = "Apologies - Your EEA newsletter subscription remains intact"
    body = """Dear subscriber,

This morning, you might have been informed that you had been automatically removed from our newsletter service. The email was sent by mistake. You will receive EEA notifications in the future without having to resubscribe to our service.

We apologise for any inconvenience it may have caused.

The EEA webteam
"""
    emails = [s.email for s in subscribers.objectValues() if s.active]
    errors = []

    count = len(emails)

    for i, email in enumerate(emails):
        mailMsg=emailutils.Message.Message()
        mailMsg["To"]=email
        mailMsg["From"]="EEA Notification Service <no-reply@eea.europa.eu>"
        mailMsg["Subject"]=subject
        mailMsg["Date"]=emailutils.Utils.formatdate(localtime=1)
        mailMsg["Message-ID"]=emailutils.Utils.make_msgid()
        mailMsg["Mime-version"]="1.0"
        mailMsg["Content-type"]="text/plain"
        mailMsg.set_payload(body)
        mailMsg.epilogue="\n" # To ensure that message ends with newline

        try:
            #TODO: is 
            #theme.sendmail("no-reply@eea.europa.eu", [("", email)], mailMsg, subject = subject)
            mailhost.send(messageText=body, mto=email, mfrom="no-reply@eea.europa.eu", subject=subject)
            info("INFO: sent email to %s, %s of %s" % (email, i, count))
        except Exception, e:
            info("Got exception %s for %s" % (e, email))
            errors.append(email)


    return str(errors)
