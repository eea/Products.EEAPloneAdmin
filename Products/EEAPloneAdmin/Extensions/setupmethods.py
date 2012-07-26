""" Setup
"""
import sys
import time
import transaction
from zope.i18n import translate as realTranslate
from zope.component import queryAdapter
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.browser.interfaces import INavigationRoot
from zope.interface import alsoProvides
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent
from Products.NavigationManager.interfaces import INavigationSectionPosition
from p4a.subtyper.interfaces import ISubtyper
from zope.component import getUtility
from eea.faceted.inheritance.interfaces import IHeritorAccessor
from Products.CMFCore.WorkflowCore import WorkflowException
from DateTime import DateTime
from eea.dataservice.relations import IRelations

# Logging
import logging
logger = logging.getLogger('EEAPloneAdmin.setupmethods')
info = logger.info
info_exception = logger.exception


def migrateRelations(self, old_ob_path, new_ob_path):
    """ Migrate relations from one object to another
    """
    context = self
    old_ob = None
    new_ob = None
    info('INFO: starting relations migration for object %s' % (old_ob_path))
    cat = getToolByName(context, 'portal_catalog')
    
    query = {'path': {'query': old_ob_path, 'depth': 0}}
    brains = cat(**query)

    if len(brains)>0:
        old_ob = brains[0].getObject()
    
    query = {'path': {'query': new_ob_path, 'depth': 0}}
    brains = cat(**query)
    
    if len(brains)>0:
        new_ob = brains[0].getObject()
    
    # Move all the forward relations to the new_ob. 
    forwards = old_ob.getRelatedItems()
    info('INFO: forward relations for object: %s' % (forwards))
    
    if forwards:
    new_ob.setRelatedItems(forwards)
    old_ob.setRelatedItems([])
    info('INFO: copying forward relations to new object')
    
    # Take all back refs (objects that refer to old_ob)
    # and make them point to new_ob
    backs = []
    backs_topro = []    
    relations = queryAdapter(old_ob, IRelations)
    if relations:
        backs = relations.backReferences()
    #get also back references from other non standard relation field
        backs_topro = relations.backReferences(relatesTo='relatesToProducts')
    info('INFO: standard back refs: %s' % (backs))
    info('INFO: relatesToProducts back refs: %s' % (backs_topro))
    
    for ob in backs:
        related = ob.getRelatedItems()
        info('INFO: BEFORE updating standard relations on backrefs: %s' % (related))
        #remove reference to old_ob
        del related[related.index(old_ob)]
        related.append(new_ob)
        ob.setRelatedItems(related)
        info('INFO: AFTER updating standard relations on backrefs: %s' % (related))

    for ob in backs_topro:
        related = ob.getRelatedProducts()
        info('INFO: BEFORE updating relatedProducts on backrefs: %s' % (related))
        #remove reference to old_ob
        del related[related.index(old_ob)]
        related.append(new_ob)
        ob.setRelatedProducts(related)
        info('INFO: AFTER updating relatedProducts on backrefs: %s' % (related))
    

    info('INFO: finished migrating relations')


def testTimeoutA(self):
    """ Test
    """
    time.sleep(600)
    return 'done'

def updateMimeTypes(self, brains=None, extension=None, newmime=None, batchnr=20):
    """ Update mime types for file fields and their catalog index
    """
    if brains is None:
        brains = []
    info('INFO: starting mime types update')
    trans_count = 0
    totobs = len(brains)

    for myfile in brains:
        fileo = myfile.getObject()
        field = fileo.getField('file')
        if field:
            accessor = field.getAccessor(fileo)()
            if accessor != None:
                filename = accessor.filename
                if filename:
                    if extension and extension in filename:
                        trans_count += 1
                        if newmime:
                            accessor.content_type = newmime
                            info('INFO: updating mime type for %s %s' % (
                                                                  myfile.id,
                                                                  filename))
                            fileo.unindexObject()
                            fileo.reindexObject()
    if trans_count % batchnr == 0:
        info('INFO: processing %s of %s objects' % (str(trans_count),
                                                    str(totobs)))
        transaction.commit()

    info('INFO: completed mime types update')

def bulkDelete(self, brains=None, batchnr=20, delete_versions=False):
    """ Delete many objects in batches (multi transactions). BE CAUTIUS.
    """
    if brains is None:
        brains = []
    info('INFO: starting bulk delete')
    request = self.REQUEST
    debug = request.get('debug', None)
    totobs = len(brains)
    deleted_count = 0

    # Delete loop
    trans_count = 0
    for brain in brains:
        trans_count += 1
        if debug:
            info('INFO: deleting %s' % brain)
        else:
            ob = brain.getObject()
            parent = ob.aq_parent
            #check if object has versions, if so do not delete it
            versions = ob.unrestrictedTraverse('@@getVersions')
            ver_nr = len(versions())
            if ((ver_nr < 2 or delete_versions) and
                 brain.review_state not in ['published', 'visible']):
                # only one version then delete, never delete published content
                info('INFO: deleting %s' % (ob.absolute_url()))
                parent.manage_delObjects([ob.id])
                deleted_count += 1
            else:
                info('INFO: Skip deleting: review state = %s  versions = %s' \
                    % (brain.review_state, str(ver_nr)))
        if trans_count % batchnr == 0:
            info('INFO: processing %s of %s objects' % (str(trans_count),
                                                        str(totobs)))
            transaction.commit()

    info('INFO: Done bulk delete of %s of total %s requested' % (
                               str(deleted_count), str(totobs)))

def bulkDeleteSpam(self):
    """ Cleanup spam
    """
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
    #wf = getToolByName(context, 'portal_workflow')

    all_brains = cat.searchResults({'show_inactive':True,
        'language':'ALL',
        'object_provides':'eea.indicators.content.interfaces.ISpecification'})

    done = 0
    try:
        for brain in all_brains:
            done += 1
            content = brain.getObject()
            content.reindexObject()
            msg = "(%d / %d) reindexed indicator: %s" % (done, len(
                all_brains), "/".join(content.getPhysicalPath()))
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
    """ Setter
    """
    context = self
    cat = getToolByName(context, 'portal_catalog')
    wf = getToolByName(context, 'portal_workflow')

   # Example:
   #    >>> fid = portal.invokeFactory('Folder', 'heritor')
   #    >>> heritor = portal._getOb(fid)
   #    >>> subtyper.change_type(heritor,
   #    ...     'eea.faceted.inheritance.FolderFacetedHeritor')
   #
   #  Connect heritor with ancestor
   #
   #    >>> request = heritor.REQUEST
   #    >>> IHeritorAccessor(heritor).ancestor = '/plone/ancestor'
   #    >>> IHeritorAccessor(heritor).ancestor
   #    '/plone/ancestor'

    pubs = cat.searchResults({'id':'indicators', 'path': '/www/SITE/themes/'})
    subtyper = getUtility(ISubtyper)
    printed = "Indicators sections for new IMSv3\n"

    for indf in pubs:
        indfo = indf.getObject()
        printed = printed + indfo.absolute_url() + '\n'
        subtyper.change_type(indfo,
                             'eea.faceted.inheritance.FolderFacetedHeritor')
        IHeritorAccessor(indfo
                         ).ancestor = '/www/SITE/themes/indicators-ancestor'
        try:
            wf.doActionFor(indfo, 'publish',
                        comment='done by setupmethods for new indicators ims.')
        except Exception:
            printed = printed + 'no possible to publish\n'
        indfo.reindexObject()

    #oldpages=cat.searchResults({'id':'indicators-old','meta_type':'Folder',
    #                            'path': '/www/SITE/themes/'})
    #for indf in oldpages[:10]:
    #    indfo=indf.getObject()
    #    printed = printed + indfo.absolute_url() + '\n'
        #wf.doActionFor(indfo,
        # 'hide',comment='done by setupmethods for new indicators ims.')
        #indfo.reindexObject()

    return printed

def createIndicatorSections(self):
    """ Create sections
    """
    context = self
    cat = getToolByName(context, 'portal_catalog')
    wf = getToolByName(context, 'portal_workflow')

    pubs = cat.searchResults({
        'object_provides' : 'eea.themecentre.interfaces.IThemeCentre',
        'path': '/www/SITE/themes/'
    })

    printed = "Indicators sections for new IMSv3"

    #image preview for indicators
    img_preview = context.manage_copyObjects(["img_preview"])

    for theme in pubs:
        themeItem = theme.getObject()
        printed = printed + themeItem.absolute_url()
        themeId = theme.id
        printed = printed + 'fixing a few things in %s' % themeId
        if hasattr(themeItem, 'indicators'):
            try:
                printed = printed + '\nfixing indicators\n'
                #rename old indicators page
                themeItem.manage_renameObject('indicators', 'indicators-old')
                oldindpage = themeItem.manage_cutObjects(["indicators-old"])
                oldpage = themeItem['indicators-old']
                #create new indicator section
                #create folder and preview image in it
                themeItem.invokeFactory('Folder', id='indicators')
                indf = themeItem['indicators']
                #indf.setLayout('dc_view')
                indf.setTitle('Indicators')
                # copy old intro text in rich topic area
                #indf.setRichContent(oldpage.getText())
                INavigationSectionPosition(indf
                                           ).section = 'data-center-services'
                indf.unmarkCreationFlag()
                indf.manage_pasteObjects(img_preview)
                indf.manage_pasteObjects(oldindpage)
                oldpage = indf['indicators-old']
                oldpage.setTitle('Indicators - old')
            except Exception:
                printed = printed + "ERROR on theme: " + themeId

            #publish
            # Make sure it's published
            try:
                wf.doActionFor(indf, 'publish',
                        comment='done by setupmethods for new indicators ims.')
            except Exception, err:
                logger.info(err)
            #reindex
            indf.reindexObject()


            #retract old page
            # Make sure it's published
            try:
                wf.doActionFor(oldpage, 'hide',
                        comment='done by setupmethods for new indicators ims.')
            except Exception, err:
                logger.info(err)
            #reindex
            oldpage.reindexObject()

        else:
            printed = printed + 'no indicators page found\n'

        #printed 'reindexing'
        #themeItem.reindexObject();

    return printed

def createRODListing(self):
    """ ROD
    """
    context = self
    cat = getToolByName(context, 'portal_catalog')
    wf = getToolByName(context, 'portal_workflow')

    pubs = cat.searchResults({
        'object_provides' : 'eea.themecentre.interfaces.IThemeCentre',
        'path': '/www/SITE/themes/'
    })

    printed = "Rod listing"

    for theme in pubs:
        themeItem = theme.getObject()
        themeId = theme.id
        if not hasattr(themeItem, 'reporting-obligations'):
            printed = (printed + '\n adding reporting obligations page to ' +
                       themeId)
            themeItem.invokeFactory('Document', id='reporting-obligations')
            rod = themeItem['reporting-obligations']
            rod.setLayout('rod_listing')
            rod.setTitle('Countries reporting obligations')
            INavigationSectionPosition(rod).section = 'data-center-services'
            rod.unmarkCreationFlag()
            # Make sure it's published
            try:
                wf.doActionFor(rod, 'publish',
                        comment='published by script for data centres setup.')
            except Exception, err:
                logger.info(err)
            rod.reindexObject()
        else:
            printed = printed + '\n rod listing exists for ' + themeId

    return printed

def createDCPage(self):
    """ create dc page for non-Datacentre sites """
    context = self
    cat = getToolByName(context, 'portal_catalog')
    wf = getToolByName(context, 'portal_workflow')

    pubs = cat.searchResults({
        'object_provides' : 'eea.themecentre.interfaces.IThemeCentre',
        'path': '/www/SITE/themes/'
    })

    printed = "create dc page for not dc sites"

    for theme in pubs:
        themeItem = theme.getObject()
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
                wf.doActionFor(dc, 'publish',
                        comment='published by script for data centres setup.')
            except Exception, err:
                logger.info(err)
            dc.reindexObject()
        else:
            printed = printed + '\n dc listing exists for ' + themeId

    return printed

def unmarkCreationFlagForBrains(self, brains=None):
    """ unmark creation flag for given catalog brains """
    info('INFO: starting unmark creation flag')
    tot = len(brains)
    i = 0
    for b in brains:
        i += 1
    info('INFO: processing %s of %s' % (str(i), str(tot)))
        try:
            o = b.getObject()
            if o.checkCreationFlag():
                msg = 'INFO: Unmarking creation flag for %s - %s' % (
                    o.getId(), o.absolute_url())
                o.unmarkCreationFlag()
                info(msg)
            else:
                msg = 'Already marked for %s - %s' % (
                    o.getId(), o.absolute_url())
                info(msg)
        except WorkflowException, err:
                info('ERROR: unmarking flag for %s' % o.absolute_url())
                info_exception('Exception: %s ', err)

    info('INFO: DONE unmark creation flag')

def interactiveMapsPromotions(self):
    """find interactive maps via promotions """
    context = self
    cat = getToolByName(context, 'portal_catalog')
    #wf = getToolByName(context, 'portal_workflow')

    pubs = cat.searchResults({ 'portal_type' : 'Promotion'})

    printed = "Promotions:"

    for pub in pubs:
        pubo = pub.getObject()
        printed = printed + pub.review_state + ' ' + pubo.absolute_url() + '\n'
        if INavigationSectionPosition(pubo).section:
            printed = (printed + 'Sections: ' +
                       INavigationSectionPosition(pubo).section + '\n')
        printed = printed + '************************************************\n'

    return printed

def sendModifiedForObjects(self):
    """ Send modified
    """
    context = self
    cat = getToolByName(context, 'portal_catalog')
    pubs = cat.searchResults({ 'id' : 'dm' })
    printed = ""
    for pub in pubs:
        pubo = pub.getObject()
        printed = printed + pub.id + "\n modified"
        pubo.reindexIsEmptyForSite(pubo, query={
            'path' : '/'.join(pubo.getPhysicalPath()),
            'Language' : 'all'
        })
        notify(ObjectModifiedEvent(pubo))
    return printed

def hideMapsDataFolders(self):
    """ Hide maps
    """
    context = self
    cat = getToolByName(context, 'portal_catalog')
    wf = getToolByName(context, 'portal_workflow')
    pubs = cat.searchResults({ 'id' : 'maps-and-graphs' ,
                             'path': '/www/SITE/themes/'})
    printed = "STARTED"
    for pub in pubs:
        pubo = pub.getObject()
        printed = printed + pub.id + "\n modified"
        try:
            wf.doActionFor(pubo, 'showPublicDraft',
            comment='Data centre setup. Hiding old structure. done by method.')
        except Exception:
            printed = printed + '/'.join(
                pubo.getPhysicalPath()) + "\n exception"
        notify(ObjectModifiedEvent(pubo))
    return printed

def setNavContext(self):
    """moving the data centric object under data centre section. """
    context = self
    cat = getToolByName(context, 'portal_catalog')
    pubs = cat.searchResults({ 'id' : 'datasets' , 'path': '/www/SITE/themes/'})
    printed = "STARTED"
    for pub in pubs:
        pubo = pub.getObject()
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
    pubs = cat.searchResults({ 'navSection' : 'quicklinks' })
    printed = "STARTED\n"
    for pub in pubs:
        pubo = pub.getObject()
        printed = printed + pub.id + "\n modified \n"
        printed = printed + '/'.join(pubo.getPhysicalPath()) + "\n"
        #notify(ObjectModifiedEvent(pubo))
        navContext = INavigationSectionPosition(pubo)
        #navContext.section = 'data-center-services'
        #notify(ObjectModifiedEvent(pubo))
        printed = printed + '  SECTION: ' + navContext.section + "\n"
    return printed

def setupPublicationsFolder(self):
    """ Setup publications
    """
    context = self
    printed = ""
    lt = getToolByName(context, 'portal_languages')
    wf = getToolByName(context, 'portal_workflow')

    #defaultLang = lt.getDefaultLanguage()
    supportedLangs = lt.getSupportedLanguages()

    printed = printed + context.id + "\n"

    for lang in supportedLangs:
        en = context
        translation = en.getTranslation(lang)
        printed = printed + "\n" + lang
        if translation is None:
            en.addTranslation(lang)
            printed = printed + "\n" + lang + " added missing translation"
            translation = en.getTranslation(lang)
            translation.unmarkCreationFlag()
            wf.doActionFor(translation, 'publish',
            comment='Initial auto publish by method for new publication system')
            printed = printed + "\n published"
            #alsoProvides(translation, INavigationRoot)

        translation.setLayout('folder_summary_search_view')
        printed = printed + "\n setting layout with search"
        #translation.setTitle( translate( title, target_language=lang))
        #printed=printed+"\n translate title"

    return printed

def setupPublicationsFolderRoot(self):
    """ Setup publications root
    """
    context = self
    printed = ""
    lt = getToolByName(context, 'portal_languages')
    #wf = getToolByName(context, 'portal_workflow')

    #defaultLang = lt.getDefaultLanguage()
    supportedLangs = lt.getSupportedLanguages()

    printed = printed + context.id + "\n"

    for lang in supportedLangs:
        en = context
        translation = en.getTranslation(lang)
        printed = printed + "\n" + lang
        if translation is not None:
            translation.setDefaultPage('latest')
            #alsoProvides(translation, INavigationRoot)
            printed = printed + "\n default page set to latest rich topic"
        else:
            printed = printed + "\n" + lang + " not translated"
    return printed

untranslatedMessages = {}

def translate(msgid, target_language, output=False):
    """ Translate
    """
    translation = realTranslate(msgid, target_language=target_language)
    if translation == str(msgid):
        if msgid not in untranslatedMessages.get(target_language, {}).keys():
            untranslatedMessages.setdefault(target_language, {})
            untranslatedMessages[target_language].setDefault(msgid, str(msgid))
        translation = untranslatedMessages.get(target_language).get(msgid)
    if type(translation) == type(''):
        return translation
    if type(translation) == type(u''):
        return translation.encode('utf8')
    # what do we have here?
    return str(translation)

def translateObject(self, templateview, navigationroot=False):
    """ Translate object
    """
    context = self
    #request = context.REQUEST
    #printed=""
    mytitle = context.title
    print mytitle
    lt = getToolByName(context, 'portal_languages')
    wf = getToolByName(context, 'portal_workflow')

    #defaultLang = lt.getDefaultLanguage()
    supportedLangs = lt.getSupportedLanguages()

    print context.id + "\n"

    for lang in supportedLangs:
        en = context
        translation = en.getTranslation(lang)
        print "\n processing language: " + lang
        if translation is None:
            en.addTranslation(lang)
            print "\n" + lang + " added missing translation"
            translation = en.getTranslation(lang)
            translation.unmarkCreationFlag()
            wf.doActionFor(translation, 'publish',
                       comment='Initial auto publish by translateObject method')
            print "\n published"

        if navigationroot:
            alsoProvides(translation, INavigationRoot)
            print "\n INavigationRoot assigned"
        translation.setLayout(templateview)
        print "\n setting layout to: " + templateview
        transtitle = translate(mytitle, target_language=lang)
        translation.setTitle(transtitle)
        print "\n translate title to: " + transtitle

    return "object translated operation completed: " + str(untranslatedMessages)

def getTranslationsFromGoogle(self, toTranslatefromG):
    """ Translate from google
    """
    return []

def importSubscribers(self):
    """ Import subscribers
    """
    info('INFO: Starting import of subscribers')
    portal = self.portal_url.getPortalObject()
    backup = portal['SITE']['sandbox']['testnewsletter']['subscribers']
    target = portal['SITE']['subscription'][
        'eea_main_subscription']['subscribers']

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
    """ Set active subscribers
    """
    info('INFO: Starting import of subscribers')
    portal = self.portal_url.getPortalObject()
    backup = portal['SITE']['sandbox']['testnewsletter']['subscribers']
    target = portal['SITE']['subscription'][
        'eea_main_subscription']['subscribers']

    all_emails = []
    duplicate_email_ids = []

    i = 0
    for subscriber in backup.objectValues():
        sid = subscriber.id
        s = target.get(sid)
        if not s:
            info('INFO: original id %s is not found in new folder', sid)
            continue

        s.active = subscriber.active
        s.email = subscriber.email
        s.format = subscriber.format
        s.bounces = []
        s._p_changed = True
        info("INFO: set %s to %s (using %s)" % (
            s.id, s.active, subscriber.active))

        if (s.email in all_emails):
            duplicate_email_ids.append(s.id)
        else:
            all_emails.append(s.email)

        if (i % 10) == 0:
            transaction.commit()
        i += 1

    info("INFO: the following ids are duplicated emails, should be erased %s",
         duplicate_email_ids)
    transaction.commit()
    info('INFO: Done reset subscribers active status')
    return str(duplicate_email_ids)


def sendMistakeEmail(self):
    """ Send email
    """
    return
    import email as emailutils

    portal = self.portal_url.getPortalObject()
    mailhost = portal.MailHost
    subscribers = portal['SITE']['subscription'][
        'eea_main_subscription']['subscribers']
    #theme = portal['SITE']['subscription']['eea_main_subscription']

    subject = "Apologies - Your EEA newsletter subscription remains intact"
    body = """Dear subscriber,

This morning, you might have been informed that you had been automatically
removed from our newsletter service. The email was sent by mistake.
You will receive EEA notifications in the future without having to
resubscribe to our service.

We apologise for any inconvenience it may have caused.

The EEA webteam
"""
    emails = [s.email for s in subscribers.objectValues() if s.active]
    errors = []

    count = len(emails)

    for i, email in enumerate(emails):
        mailMsg = emailutils.Message.Message()
        mailMsg["To"] = email
        mailMsg["From"] = "EEA Notification Service <no-reply@eea.europa.eu>"
        mailMsg["Subject"] = subject
        mailMsg["Date"] = emailutils.Utils.formatdate(localtime=1)
        mailMsg["Message-ID"] = emailutils.Utils.make_msgid()
        mailMsg["Mime-version"] = "1.0"
        mailMsg["Content-type"] = "text/plain"
        mailMsg.set_payload(body)
        mailMsg.epilogue = "\n" # To ensure that message ends with newline

        try:
            #ZZZ: is
            #theme.sendmail("no-reply@eea.europa.eu",
            #[("", email)], mailMsg, subject = subject)
            mailhost.send(messageText=body, mto=email,
                          mfrom="no-reply@eea.europa.eu", subject=subject)
            info("INFO: sent email to %s, %s of %s" % (email, i, count))
        except Exception, e:
            info("Got exception %s for %s" % (e, email))
            errors.append(email)


    return str(errors)
