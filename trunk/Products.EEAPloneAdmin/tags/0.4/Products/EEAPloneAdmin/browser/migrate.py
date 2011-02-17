import csv
import logging
from pprint import pformat
import urllib
from zope.interface import alsoProvides, directlyProvides, directlyProvidedBy
from eea.themecentre.interfaces import IThemeCentreSchema, IThemeRelation
from eea.themecentre.interfaces import IThemeTagging, IThemeCentre
from eea.themecentre.browser.themecentre import PromoteThemeCentre
from eea.themecentre.themecentre import createFaqSmartFolder, getThemeCentre
from eea.rdfrepository.interfaces import IFeed, IFeedContent
from eea.mediacentre.interfaces import IMediaType
from p4a.video.interfaces import IVideo
from Acquisition import aq_base
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.browser.interfaces import INavigationRoot
from Products.CMFPlone.utils import normalizeString
import socket
import feedparser
import urlparse
import os
url = 'http://themes.eea.europa.eu/migrate/%s?theme=%s'

# Some new theme ids are not same as old
themeIdMap = { 'coasts_seas' : 'coast_sea',
               'fisheries' : 'fishery',
               'human_health' : 'human',
               'natural_resources' : 'natural',
               'env_information' : 'information',
               'env_management' : 'management',
               'env_reporting' : 'reporting',
               'env_scenarios' : 'scenarios',
               'various' : 'other_issues' }

class FixExcludeFromNav(object):
    """ fix overwritten exclude_from_nav """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        context = self.context
        res = context.portal_catalog.searchResults(portal_type = 'Folder', id='multimedia', path = '/'.join(context.getPhysicalPath()))
        for folder in res:
            obj = folder.getObject()
            exclude_from_nav = getattr(aq_base(obj), 'exclude_from_nav', None)
            if exclude_from_nav and not callable(exclude_from_nav):
                del obj.exclude_from_nav
                obj.initializeLayers()

class MigrateWrongThemeIds(object):
    """ migrate wrong theme ids to old correct """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        context = self.context
        themeVocab = context.portal_vocabularies.themes
        themeIds = themeVocab.objectIds()

        for theme in themeIdMap.keys():
            res = context.portal_catalog.searchResults(getThemes=theme)
            for r in res:
                obj = r.getObject()
                try:
                    currentThemes = obj.getThemes()
                except:
                    continue
                if currentThemes == str(currentThemes):
                    currentThemes = [currentThemes,]
                newThemes = [ themeIdMap.get(r,r) for r in currentThemes ]
                obj.setThemes(newThemes)
                print '%s: %s -> %s' % (obj, currentThemes, newThemes)

        for t in themeIds:
            newT = themeIdMap.get(t,t)
            if newT != t:
                obj = themeVocab[t]
                obj.setId(newT)

class MigrateTheme(object):
    """ Migrate theme info from themes.eea.europa.eu zope 2.6.4 """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        newThemeId = self.context.getId()
        themeId = themeIdMap.get(newThemeId, newThemeId)
        try:
            step = 0
            self._title(themeId)
            step += 1
            self._intro(themeId)
            step += 1
            self._relatedThemes(themeId)
            step += 1
            self._links(themeId)
            step += 1
            self._image(themeId)
            step += 1
            self._indicators(themeId)
        except:
            print themeId + ' failed on step %s' % step
        self.context.reindexObject()

    def _title(self, themeId):
        titleUrl = url % ('themeTitle', themeId)
        title = urllib.urlopen(titleUrl).read()
        title = title.replace('\n','')
        self.context.setTitle(title)

    def _image(self, themeId):
        getUrl = url % ('themeUrl', themeId)
        themeUrl  = urllib.urlopen(getUrl).read().strip()
        imageUrl = themeUrl + '/theme_image'
        imageData  = urllib.urlopen(imageUrl).read().strip()
        image = self.context.invokeFactory('Image', id='theme_image', title='%s - Theme image' % self.context.Title())
        obj = self.context[image]
        obj.setImage(imageData)
        obj.reindexObject()

    def _relatedThemes(self, themeId):
        relatedUrl = url % ('themeRelated', themeId)
        related = urllib.urlopen(relatedUrl).read().strip()
        related = related[1:-1].replace('\'','')
        related = [ theme.strip() for theme in related.split(',') ]
        theme = IThemeRelation(self.context)
        themeCentres = self.context.portal_catalog.searchResults(object_provides='eea.themecentre.interfaces.IThemeCentre')
        tcs = {}
        for tc in themeCentres:
            tcs[tc.getId] =  tc.getObject().UID()
        themeCentres = tcs

        # map old theme id to new
        related = [ themeIdMap.get(r, r) for r in related ]

        # XXX need to find UID for the related theme centres
        related = [ themeCentres.get(r) for r in related ]
        related = [ r for r in related
                      if r is not None ]
        theme.related = related

    def _intro(self, themeId):
        introUrl = url % ('themeIntro', themeId)
        introText = urllib.urlopen(introUrl).read().strip()
        intro = 'intro'
        if not hasattr(self.context, intro):
            intro = self.context.invokeFactory('Document', id=intro)
            obj = self.context[intro]
            obj.setTitle(self.context.Title() + ' introduction')
            obj.setText(introText, mimetype='text/html')
            obj.reindexObject()

    def _links(self, themeId):
        workflow = getToolByName(self.context, 'portal_workflow')
        linksUrl = url % ('themeLinks', themeId)
        links = urllib.urlopen(linksUrl).read().strip()
        links = links.split('\n')
        folder = self.context.links
        for link in links:
            link = link.split(';')
            if not link[0].strip():
                continue
            linkId = folder.invokeFactory('Link', id=link[0].strip())
            obj = folder[linkId]
            try:
                obj.setTitle(link[1].strip().decode('iso-8859-1'))
            except:
                obj.setTitle('link[2].strip()')
            obj.setRemoteUrl(link[2].strip())
            workflow.doActionFor(obj, 'publish')

    def _indicators(self, themeId):
        workflow = getToolByName(self.context, 'portal_workflow')
        indiUrl = url % ('themeIndicator', themeId)
        indiText = urllib.urlopen(indiUrl).read().strip()
        indicators = 'indicators'
        if not hasattr(self.context, indicators):
            indicators = self.context.invokeFactory('Document', id=indicators)
            obj = self.context[indicators]
            obj.setTitle('Indicators')
            obj.setText(indiText, mimetype='text/html')
            catalog = getToolByName(self.context, 'portal_catalog')
            indicatorRSS = catalog.searchResults( portal_type='RSSFeedRecipe', id='indicators_' +themeId)
            if len(indicatorRSS) > 0:
                obj.setRelatedItems(indicatorRSS[0].getObject().UID())
            workflow.doActionFor(obj, 'publish')
            obj.reindexObject()


class InitialThemeCentres(object):
    """ create inital theme structure """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        context = self.context
        workflow = getToolByName(self.context, 'portal_workflow')
        fixThemeIds = MigrateWrongThemeIds(context, self.request)
        fixThemeIds()

        themeids = context.portal_vocabularies.themes.objectIds()[1:]
        noThemes = int(self.request.get('noThemes',0))
        if noThemes > 0:
            themeids = themeids[:noThemes]
        toMigrate = self.request.get('migrate', False)
        for theme in themeids:
            if not hasattr(aq_base(context), theme):
                folder = context.invokeFactory('Folder', id=theme, title=theme)
                folder = context[folder]
                ptc = PromoteThemeCentre(folder, self.request)
                ptc()

                tc = IThemeCentreSchema(folder)
                tc.tags = theme

                workflow.doActionFor(folder, 'publish')

        if toMigrate:
            for theme in themeids:
                tc = context[theme]
                migrate = MigrateTheme(tc, self.request)
                migrate()

        if not hasattr(aq_base(context), 'right_slots'):
            slots = ['here/portlet_themes_related/macros/portlet',
                     'here/portlet_themes_rdf/macros/portlet']
            context.manage_addProperty('right_slots', slots, type='lines')

        if not hasattr(aq_base(context), 'left_slots'):
            slots = ['here/portlet_themes/macros/portlet', ]
            context.manage_addProperty('left_slots', slots, type='lines',),

        #if hasattr(aq_base(context), 'navigationmanager_menuid'):
        #    context.manage_addProperty('navigationmanager_menuid', 'themes', type='string')

        alsoProvides(context, INavigationRoot)
        context.layout = 'themes_view'
        return self.request.RESPONSE.redirect(context.absolute_url())

class RDF(object):
    """ Copies RDF/RSS feeds from themes.eea.europa.eu to
        RSSFeedRecipe objects in the current folder. """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        socket.setdefaulttimeout(15)
        workflow = getToolByName(self.context, 'portal_workflow')
        migrate_url = url % ('themeRDF', '')
        feeds = urllib.urlopen(migrate_url).readlines()

        for feed_line in feeds:
            id, title, feed_url = feed_line.strip().split('|')
            if id.startswith("reports_"):
                title = "Reports"
            elif not title:
                title = id

            if not hasattr(self.context, id):
                self.context.invokeFactory('RSSFeedRecipe', id=id, title=title)

            recipe = self.context[id]
            recipe.setEntriesWithDescription(0)
            recipe.setEntriesWithThumbnail(0)

            parsed = feedparser.parse(feed_url)
            if parsed['feed'].has_key('link'):
                recipe.setUrl(parsed['feed']['link'])

            recipe.setEntriesSize(10000)

            x = feed_url.find('theme=')
            if x > -1:
                theme = feed_url[x+6:].strip()
                taggable = IThemeTagging(recipe)
                taggable.tags = [theme]

            parsed_url = urlparse.urlparse(feed_url)
            if parsed_url[2] != '/schema.rdf' and parsed_url[2].endswith('.rdf'):
                if parsed_url[4]:
                    feed_url += '&image=yes'
                else:
                    feed_url += '?image=yes'
            recipe.setFeedURL(feed_url)

            if workflow.getInfoFor(recipe, 'review_state') != \
                    'published':
                workflow.doActionFor(recipe, 'publish')
            recipe.reindexObject()


        return str(len(feeds)) + ' RDF/RSS files were successfully migrated.'

class IndicatorRDFs(object):
    """ Create RSSFeedRecipes for indicator rss """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        context = self.context
        workflow = getToolByName(self.context, 'portal_workflow')
        url = 'http://themes.eea.europa.eu/indicators/bytheme.rss?theme_id=%s'
        themeids = context.portal_vocabularies.themes.objectIds()[1:]
        for theme in themeids:
            feedId = 'indicators_%s' % theme
            title = 'Indicators'
            feed_url = url % theme
            if not hasattr(self.context, feedId):
                self.context.invokeFactory('RSSFeedRecipe', id=feedId, title=title)
            recipe = self.context[feedId]
            recipe.setEntriesSize(10000)
            recipe.setFeedURL(feed_url)
            recipe.setEntriesWithDescription(0)
            recipe.setEntriesWithThumbnail(0)

            parsed = feedparser.parse(feed_url)
            if parsed['feed'].has_key('link'):
                recipe.setUrl(parsed['feed']['link'])

            taggable = IThemeTagging(recipe)
            taggable.tags = [theme]

            if workflow.getInfoFor(recipe, 'review_state') != \
                    'published':
                workflow.doActionFor(recipe, 'publish')
            recipe.reindexObject()

        return str(len(themeids)) + ' indicator fees migrated.'

class ThemeTaggable(object):
    """ Migrate theme tags to anootations. """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        catalog = getToolByName(self.context, 'portal_catalog')
        types = ('Highlight', 'Promotion', 'QuickEvent', 'PressRelease',
                'Speech')
        brains = catalog.searchResults(portal_type=types)

        for brain in brains:
            obj = brain.getObject()
            tagging = IThemeTagging(obj)
            themes = filter(None, obj.schema['themes'].get(obj))
            tagging.tags = themes

class UpdateSmartFoldersAndTitles(object):
    """ Change all event topics to have end instead of start in criteria. """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        catalog = getToolByName(self.context, 'portal_catalog')

        # change criteria on event topic
        query = { 'portal_type': 'Topic',
                  'id': 'events_topic' }
        brains = catalog.searchResults(query)
        for brain in brains:
            topic = brain.getObject()
            topic.setTitle('Upcoming events')
            topic.reindexObject()

            if 'crit__start_ATFriendlyDateCriteria' in topic.objectIds():
                topic.deleteCriterion('crit__start_ATFriendlyDateCriteria')

            if 'crit__end_ATFriendlyDateCriteria' not in topic.objectIds():
                date_crit = topic.addCriterion('end', 'ATFriendlyDateCriteria')
                date_crit.setValue(0)
                date_crit.setDateRange('+')
                date_crit.setOperation('more')

            if 'crit__created_ATSortCriterion' in topic.objectIds():
                topic.deleteCriterion('crit__created_ATSortCriterion')
                topic.addCriterion('start', 'ATSortCriterion')

            # add custom fields to the events and highlight folders, links don't
            # need any as they shouldn't show anything in "detail"
            topic.setCustomViewFields(['start', 'end', 'location'])

        # add custom field on all highligh topic
        query = { 'portal_type': 'Topic',
                  'id': 'highlights_topic' }
        brains = catalog.searchResults(query)
        for brain in brains:
            topic = brain.getObject()
            topic.setCustomViewFields(['EffectiveDate'])

        # remove custom field on all link topics
        query = { 'portal_type': 'Topic',
                  'id': 'links_topic' }
        brains = catalog.searchResults(query)
        for brain in brains:
            topic = brain.getObject()
            topic.setTitle('External links')
            topic.reindexObject()
            topic.setCustomViewFields([])

        # rename titles on folders in themecentre
        query = { 'object_provides': 'eea.themecentre.interfaces.IThemeCentre' }
        brains = catalog.searchResults(query)
        for brain in brains:
            themecentre = brain.getObject()

            events_folder = getattr(themecentre, 'events')
            if events_folder:
                events_folder.setTitle('Upcoming events')
                events_folder.reindexObject()
            links_folder = getattr(themecentre, 'links')
            if links_folder:
                links_folder.setTitle('External links')
                links_folder.reindexObject()

            faqs_folder = getattr(themecentre, 'faq')
            if faqs_folder:
                if not getattr(faqs_folder, 'faqs_topic', None):
                    theme_id = IThemeCentreSchema(themecentre).tags
                    createFaqSmartFolder(faqs_folder, theme_id)

        # themecentre portlet smart folders should not rename themselves
        query = { 'portal_type': 'Topic',
                  'path': '/'.join(self.context.getPhysicalPath()) }
        brains = catalog.searchResults(query)
        for brain in brains:
            topic = brain.getObject()
            topic._at_rename_after_creation = False

        return 'success'

class FeedMarkerInterface(object):
    """ Changes all IFeed marker interfaces to be IFeedContent markers. """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        catalog = getToolByName(self.context, 'portal_catalog')
        query = { 'portal_type': 'RSSFeedRecipe' }
        brains = catalog.searchResults(query)
        for brain in brains:
            feed = brain.getObject()
            directlyProvides(feed, directlyProvidedBy(feed)-IFeed)
            directlyProvides(feed, directlyProvidedBy(feed), IFeedContent)
            feed.reindexObject()
        return 'success'

class PromotionThemes(object):
    """ Old promotions might have themes as strings instead of lists. """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        catalog = getToolByName(self.context, 'portal_catalog')
        query = { 'portal_type': 'Promotion' }
        brains = catalog.searchResults(query)
        not_migrated = ''
        for brain in brains:
            obj = brain.getObject()
            if obj.schema['themes'].get(obj) == 'default':
                if IThemeTagging(obj).tags == ['d', 'e', 'f', 'a',
                                               'u', 'l', 't']:
                    IThemeTagging(obj).tags = ['default']
                else:
                    not_migrated += brain.getURL() + '\n'

        if not_migrated:
            return 'Some objects were not migrated\n' + not_migrated
        else:
            return 'success'

class ThemeLayoutAndDefaultPage(object):
    """ Removes the layout property on all themecentres and instead adds the
        default_page property with 'intro'. The intro document gets a layout
        property instead. """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        query = {'object_provides': 'eea.themecentre.interfaces.IThemeCentre'}
        brains = self.context.portal_catalog.searchResults(query)
        for brain in brains:
            themecentre = brain.getObject()
            tc_base = aq_base(themecentre)
            intro = getattr(themecentre, 'intro', None)
            tc_layout = getattr(tc_base, 'layout', None)
            if intro:
                if tc_layout:
                    tc_base.__delattr__('layout')
                if not themecentre.hasProperty('default_page'):
                    themecentre.manage_addProperty('default_page', 'intro', 'string')
                if not intro.hasProperty('layout'):
                    intro.manage_addProperty('layout', 'themecentre_view', 'string')
                themecentre._p_changed = True
        return str(len(brains)) + ' themecentres migrated'

class GenericThemeToDefault(object):
    """ Migrates theme tags ['G','e','n','e','r','i','c'] or ['D', 'e', 'f', 'a', 'u', 'l', 't'] to ['default']. """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        catalog = getToolByName(self.context, 'portal_catalog')
        query1 = { 'getThemes': 'G' }
        query2 = { 'getThemes': 'D' }
        query3 = { 'getThemes': 'g' }
        query4 = { 'getThemes': 'd' }
        queries = [query1,query2,query3,query4]
        output=''
        for query in queries:
           brains = catalog.searchResults(query)
           for brain in brains:
               if brain.getThemes == ['G', 'e', 'n', 'e', 'r', 'i', 'c'] or brain.getThemes == ['g', 'e', 'n', 'e', 'r', 'i', 'c'] or brain.getThemes == ['D', 'e', 'f', 'a', 'u', 'l', 't'] or brain.getThemes == ['d', 'e', 'f', 'a', 'u', 'l', 't']:
                  obj = brain.getObject()
                  themes = IThemeTagging(obj)
                  output=output+'NOTOK: '+obj.id+': '+'brain.getThemes[0]: '+ brain.getThemes[0] + ' themes.tags[0]: '+ (len(themes.tags) > 0 and themes.tags[0] or '') + ' URL: ' + obj.absolute_url() +'\r'
                  themes.tags = ['default']
                  obj.reindexObject()
               else:
                  output=output+'OK: '+brain.id+': '+'brain.getThemes[0]: '+ brain.getThemes[0] + 'URL:'+ brain.getURL() +'\r'
        return 'themes are migrated, RESULT:\r' + output

class EntriesWithThumbnail(object):
    """ Changes 'entries with thumbnail' to 10000 on all rss feed recipes
        in the rdf repository. """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        repository = self.context
        catalog = getToolByName(self.context, 'portal_catalog')
        query = {'portal_type': 'RSSFeedRecipe',
                 'path': repository.getPhysicalPath() }
        brains = catalog.searchResults(query)
        for brain in brains:
            recipe = brain.getObject()
            recipe.setEntriesWithThumbnail(10000)
        return '%d rss recipes were migrated' % len(brains)

class ChangeDefaultPageToProperty(object):
    """ Changes default_page to being a property so it's visible in ZMI """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        query = {'object_provides': 'eea.themecentre.interfaces.IThemeCentre'}
        brains = self.context.portal_catalog.searchResults(query)
        for brain in brains:
            themecentre = brain.getObject()
            links = getattr(themecentre, 'links', None)
            news = getattr(themecentre, 'news', None)
            events = getattr(themecentre, 'events', None)

            for folder in filter(None, (links, news, events)):
                base = aq_base(folder)
                attr = getattr(base, 'default_page', None)
                has_property = base.hasProperty('default_page')
                # if object has a default_page attribute that is not a property
                if attr is not None and not has_property:
                    del base.default_page
                    base.manage_addProperty('default_page', attr, 'string')
        return "successfully migrated properties"

class EnsureAllObjectsHaveTags(object):
    """ Adds themecentre tag to all its objects if they don't have it
        already. """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        themesdir = self.context
        portal_catalog = getToolByName(self.context, 'portal_catalog')

        count = 0
        path = '/'.join(themesdir.getPhysicalPath())
        brains = portal_catalog.searchResults(path=path)
        for brain in brains:
            if not brain.getThemes:
                obj = brain.getObject()
                themeCentre = getThemeCentre(obj)
                if themeCentre:
                    themes = IThemeTagging(obj, None)
                    if themes:
                        themeCentreThemes = IThemeCentreSchema(themeCentre)
                        themes.tags = [themeCentreThemes.tags]
                        count += 1

        return str(count)  + " objects were tagged"

class ChangeMediaTypesDefault(object):
    """ Changes the media type on file's don't have any media type set.
        If media type not set, the type 'other' is set on the file. """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        catalog = getToolByName(self.context, 'portal_catalog')
        brains = catalog.searchResults(object_provides='p4a.video.interfaces.IVideoEnhanced')
        for brain in brains:
            file = brain.getObject()
            media = IMediaType(file)
            if not media.types:
                media.types = ['other']
            file.reindexObject()

        return "migration successful"

class AddRichTextDescriptionToVideos(object):
    """ Adds an empty string to the rich_description field on all
        IVideoEnhanced objects. As this is a new field it's None
        and the edit page fails with a traceback. """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        catalog = getToolByName(self.context, 'portal_catalog')
        brains = catalog.searchResults(object_provides='p4a.video.interfaces.IVideoEnhanced')
        for brain in brains:
            file = brain.getObject()
            video = IVideo(file)
            video.rich_description = u''
            video.urls = ()

        return str(len(brains)) + " videos where migrated."


class AddFolderAsLocallyAllowedTypeInLinks(object):
    """ Add the 'Folder' type as a locally addable type to all 'External link' folders in themecentres. """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        catalog = getToolByName(self.context, 'portal_catalog')
        brains = catalog.searchResults(object_provides=IThemeCentre.__identifier__)
        objs = [b.getObject() for b in brains]
        for obj in objs:
            linkfolder = None
            if 'links' in obj.objectIds():
                linkfolder = obj.links
            elif 'external-links' in obj.objectIds():
                linkfolder = obj['external-links']

            if linkfolder is not None:
                local = linkfolder.getLocallyAllowedTypes()
                immediate = linkfolder.getImmediatelyAddableTypes()
                if 'Folder' not in local:
                    linkfolder.setLocallyAllowedTypes(local + ('Folder',))
                if 'Folder' not in immediate:
                    linkfolder.setImmediatelyAddableTypes(immediate + ('Folder',))

        return 'successfully run'

class AddPressReleaseToHighlightsTopic(object):
    """ Adds PressRelease to the highlight topic's search criteria. """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        catalog = getToolByName(self.context, 'portal_catalog')
        brains = catalog.searchResults(object_provides=IThemeCentre.__identifier__,
                                       Language='all')
        themecentres = [b.getObject() for b in brains]
        successful = 0

        for themecentre in themecentres:
            highlights_folder = getattr(themecentre, 'highlights', None)
            if highlights_folder is None:
                continue

            topic = getattr(highlights_folder, 'highlights_topic', None)
            if topic is not None:
                crit = topic.getCriterion('Type_ATPortalTypeCriterion')
                value = crit.Value()
                if not 'Press Release' in value:
                    crit.setValue(value + ('Press Release',))
                successful += 1

        return '%d highlight smart folders were modified' % successful


class ChangeMultimediaLayout(object):
    """ Changes layout to mediacentre_view in the global multimedia folder """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        portal_url = getToolByName(self.context, 'portal_url')
        portal = portal_url.getPortalObject()
        default_page = getattr(portal.SITE.multimedia, 'default_page', None)
        if default_page:
            multimedia = getattr(portal.SITE.multimedia, default_page)
            multimedia.manage_changeProperties(layout = 'mediacentre_view')
            return "layout property of %s is changed to %s." % \
                    (multimedia.absolute_url(), 'mediacentre_view')
        else:
            return "default_page property of multimedia not found, " \
                   "no migration done"

class MakeThemeMultimediaLayoutAProperty(object):
    """ Multimedia folders in themecentres have a layout property that's
        not visible in ZMI. Add it as a real property. """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        catalog = getToolByName(self.context, 'portal_catalog')
        themeCentres = catalog.searchResults(object_provides=IThemeCentre.__identifier__)
        props = 0
        for tc in themeCentres:
            multimedia = getattr(aq_base(tc.getObject()), 'multimedia', None)
            if multimedia is not None:
                multimedia = aq_base(multimedia)
                layout = getattr(multimedia, 'layout', None)
                if not multimedia.hasProperty('layout'):
                    del multimedia.layout
                    multimedia.manage_addProperty('layout', layout, 'string')
                    props += 1
        return '%d layout properties are fixed' % props

class ImportEcoTipsTranslationsFromCSV(object):
    """ Import translations form EcoTip objects from the
        EEAWEBSITE_ECOTIP_Migration.csv file """

    def __init__(self, context, request):
        self.context = context.getCanonical()
        self.request = request
        self.safe = True
        self.publish = False
        self.reindex = False
        self.languages = []
        self.logger = logging.getLogger('EEAPloneAdmin.migrate.importEcoTips')
        self.errors = []
        self.tips = {}
        self.imported = {}

    def _return(self):
        msg = "You called this script with this parameters:"
        msg += "\n\tsafe=%s" % self.safe
        msg += "\n\tpublish=%s" % self.publish
        msg += "\n\treindex=%s" % self.reindex
        msg += "\n\tlanguage=%s" % ', '.join(self.languages)
        msg += "\n\n"

        if self.safe:
            msg += "Translations NOT imported with %s warning(s). " % len(self.errors)
            msg += "To import ignoring warnings set safe param to False"
        else:
            msg += "Translations imported with %s error(s)" % len(self.errors)

        msg += "\n\n"

        return msg + '\n'.join(self.errors)

    def _raise(self, msg):
        if self.safe:
            self.logger.warn(msg)
        else:
            self.logger.error(msg)
        self.errors.append(msg)

    def _prepare_tips(self):
        """ Get green tips titles
        """
        tips = self.context.objectValues('ATDocument')
        for tip in tips:
            key = tip.title_or_id().strip()
            value = tip.getId()
            self.tips[key] = value

    def _import(self):
        filename = os.path.join(os.path.dirname(__file__), 'EEAWEBSITE_ECOTIP_Migration.csv')
        reader = csv.reader(open(filename, 'r'), delimiter='\t', quotechar='"')
        header = reader.next()
        for index, row in enumerate(reader):
            if len(row) < 5:
                self._raise("Invalid row(%d) in csv file." % (index + 2))

            lang     = row[0].strip().lower()
            en_title = row[1].strip()
            tr_title = row[2].strip()
            tr_desc  = row[4].strip()
            key = self.tips.get(en_title, None)
            if not key:
                self._raise("I can not find this title in my green tips. Language: %s, Title: %s" % (lang, en_title))
                continue

            self._add_translation(key, lang, tr_title, tr_desc)

        for lang in self.languages:
            tra = self.context.getTranslation(lang)
            self._reindex(tra)
            self._publish(tra)

        for title, tip in self.tips.items():
            langs = self.imported.get(tip, [])
            junk = [lang for lang in self.languages if lang not in langs]
            if junk:
                junk.sort()
                self._raise('No translations found for %s(%s), \n\tlanguages:\t%s' % (tip, title, ', '.join(junk)))

    def _add_translation(self, key, lang, title, description):
        """ Add trannslation
        """
        if lang not in self.languages:
            return

        translation = lang in self.imported.get(key, [])
        if translation:
            self._raise('Duplicated translation in csv file: %s language: %s' % (
                key, lang))
            return

        self.imported.setdefault(key, [])
        self.imported[key].append(lang)

        tip = self.context._getOb(key)
        translation = tip.getTranslation(lang)
        if translation:
            self._raise("Already imported. I'll override it: %s, %s" % (lang, key))

        if self.safe:
            return

        if not translation:
            self.logger.info('Add translation lang: %s for %s', lang, key)
            tip.addTranslation(lang)
            translation = tip.getTranslation(lang)

        translation.getField('title').getMutator(translation)(title)
        translation.getField('description').getMutator(translation)(description)

        self._publish(translation)
        self._reindex(translation)

    def _publish(self, translation):
        if self.safe:
            return
        if not self.publish:
            return

        wftool = getToolByName(self.context, 'portal_workflow')
        state = wftool.getInfoFor(translation, 'review_state', '(Unknown)')
        if state == 'published':
            return
        try:
            wftool.doActionFor(translation, 'publish',
                               comment='Auto published by migration script.')
        except Exception, err:
            self._raise('Could not publish %s, state: %s, error: %s' % (
                translation.absolute_url(1), state, err))
        else:
            self.logger.info('Published translation %s', translation.absolute_url())

    def _reindex(self, translation):
        if self.safe:
            return
        if not self.reindex:
            return

        ctool = getToolByName(self.context, 'portal_catalog')
        ctool.reindexObject(translation)
        self.logger.info('Reindexed translation %s',  translation.absolute_url())

    def __call__(self, safe=True, publish=True, reindex=True, language='all'):
        if not self.context.getId() == 'green-tips':
            return "Ops, you can run this migration script only in green-tips context"

        self.safe = safe in [True, 1, 'True', '1', 'yes', 'on']
        self.publish = publish in [True, 1, 'True', '1', 'yes', 'on']
        self.reindex = reindex in [True, 1, 'True', '1', 'yes', 'on']
        if language == 'all':
            language = []
        if isinstance(language, str):
            language = [language,]
        self.languages = language or self.context.getTranslations().keys()
        if 'en' in self.languages:
            self.languages.remove('en')
        self._prepare_tips()

        self._import()
        return self._return()

class MigrateDatesInCallForTendersAndInterests(object):
    """ #1787 required us to set value on the expiration and effective fields.
        This copies the dates open -> effective and close -> expire. """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        catalog = getToolByName(self.context, 'portal_catalog')
        for b in catalog({'portal_type' : ['CallForTender', 'CallForInterest']}):
            obj = b.getObject()
            obj.setCloseDate(obj.getCloseDate())
            obj.setOpenDate(obj.getOpenDate())

