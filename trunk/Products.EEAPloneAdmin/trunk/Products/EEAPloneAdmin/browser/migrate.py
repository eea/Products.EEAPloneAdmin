""" Migrate
"""
from Acquisition import aq_base
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from eea.mediacentre.interfaces import IMediaType
from eea.promotion.interfaces import IPromotion, IPromoted
from eea.themecentre.browser.themecentre import PromoteThemeCentre
from eea.themecentre.interfaces import IThemeCentreSchema, IThemeRelation
from eea.themecentre.interfaces import IThemeTagging, IThemeCentre
from eea.themecentre.themecentre import createFaqSmartFolder, getThemeCentre
from p4a.video.interfaces import IVideo
from plone.app.blob.browser.migration import BlobMigrationView
from plone.app.blob.migrations import ATFileToBlobMigrator, getMigrationWalker
from plone.app.blob.migrations import migrate
from plone.app.layout.navigation.interfaces import INavigationRoot
from zope.interface import alsoProvides
from eea.mediacentre.interfaces import IVideo as MIVideo
from Products.EEAContentTypes.content.interfaces import IFlashAnimation
import csv
import logging
import os
import urllib
import transaction
import json
from cStringIO import StringIO
from zope.interface import directlyProvides, directlyProvidedBy, noLongerProvides
from eea.dataservice.interfaces import IEEAFigureMap, IEEAFigureGraph
from plone.i18n.locales.interfaces import ICountryAvailability
from zope.component import queryUtility

from Products.EEAPloneAdmin.browser.migration_helper_data import \
    countryDicts, countryGroups



logger = logging.getLogger("Products.EEAPloneAdmin")

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
    """ Fix overwritten exclude_from_nav
    """
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        context = self.context
        res = context.portal_catalog.searchResults(
            portal_type='Folder',
            id='multimedia',
            path='/'.join(context.getPhysicalPath()))
        for folder in res:
            obj = folder.getObject()
            exclude_from_nav = getattr(aq_base(obj), 'exclude_from_nav', None)
            if exclude_from_nav and not callable(exclude_from_nav):
                del obj.exclude_from_nav
                obj.initializeLayers()

class MigrateWrongThemeIds(object):
    """ Migrate wrong theme ids to old correct
    """
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
                except Exception:
                    continue
                if currentThemes == str(currentThemes):
                    currentThemes = [currentThemes, ]
                newThemes = [ themeIdMap.get(r, r) for r in currentThemes ]
                obj.setThemes(newThemes)
                print '%s: %s -> %s' % (obj, currentThemes, newThemes)

        for t in themeIds:
            newT = themeIdMap.get(t, t)
            if newT != t:
                obj = themeVocab[t]
                obj.setId(newT)

class MigrateTheme(object):
    """ Migrate theme info from themes.eea.europa.eu zope 2.6.4
    """
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
        except Exception:
            print themeId + ' failed on step %s' % step
        self.context.reindexObject()

    def _title(self, themeId):
        """ Title
        """
        titleUrl = url % ('themeTitle', themeId)
        title = urllib.urlopen(titleUrl).read()
        title = title.replace('\n', '')
        self.context.setTitle(title)

    def _image(self, themeId):
        """ Image
        """
        getUrl = url % ('themeUrl', themeId)
        themeUrl = urllib.urlopen(getUrl).read().strip()
        imageUrl = themeUrl + '/theme_image'
        imageData = urllib.urlopen(imageUrl).read().strip()
        image = self.context.invokeFactory('Image',
                                           id = 'theme_image',
                                           title = '%s - Theme image' %
                                                       self.context.Title())
        obj = self.context[image]
        obj.setImage(imageData)
        obj.reindexObject()

    def _relatedThemes(self, themeId):
        """ Related themes
        """
        relatedUrl = url % ('themeRelated', themeId)
        related = urllib.urlopen(relatedUrl).read().strip()
        related = related[1:-1].replace('\'', '')
        related = [ theme.strip() for theme in related.split(',') ]
        theme = IThemeRelation(self.context)
        themeCentres = self.context.portal_catalog.searchResults(
            object_provides='eea.themecentre.interfaces.IThemeCentre')
        tcs = {}
        for tc in themeCentres:
            tcs[tc.getId] = tc.getObject().UID()
        themeCentres = tcs

        # map old theme id to new
        related = [ themeIdMap.get(r, r) for r in related ]

        # ZZZ need to find UID for the related theme centres
        related = [ themeCentres.get(rel) for rel in related ]
        related = [ rl for rl in related if rl is not None ]
        theme.related = related

    def _intro(self, themeId):
        """ Intro
        """
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
        """ Links
        """
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
            except Exception:
                obj.setTitle('link[2].strip()')
            obj.setRemoteUrl(link[2].strip())
            workflow.doActionFor(obj, 'publish')

    def _indicators(self, themeId):
        """ Indicators
        """
        workflow = getToolByName(self.context, 'portal_workflow')
        indiUrl = url % ('themeIndicator', themeId)
        indiText = urllib.urlopen(indiUrl).read().strip()
        indicators = 'indicators'
        if not hasattr(self.context, indicators):
            indicators = self.context.invokeFactory('Document', id=indicators)
            obj = self.context[indicators]
            obj.setTitle('Indicators')
            obj.setText(indiText, mimetype='text/html')
            workflow.doActionFor(obj, 'publish')
            obj.reindexObject()

class InitialThemeCentres(object):
    """ Create inital theme structure
    """
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        context = self.context
        workflow = getToolByName(self.context, 'portal_workflow')
        fixThemeIds = MigrateWrongThemeIds(context, self.request)
        fixThemeIds()

        themeids = context.portal_vocabularies.themes.objectIds()[1:]
        noThemes = int(self.request.get('noThemes', 0))
        if noThemes > 0:
            themeids = themeids[:noThemes]
        toMigrate = self.request.get('migrate', False)
        for theme in themeids:
            if not hasattr(aq_base(context), theme):
                folder = context.invokeFactory('Folder',
                                               id=theme,
                                               title=theme)
                folder = context[folder]
                ptc = PromoteThemeCentre(folder, self.request)
                ptc()

                tc = IThemeCentreSchema(folder)
                tc.tags = theme

                workflow.doActionFor(folder, 'publish')

        if toMigrate:
            for theme in themeids:
                tc = context[theme]
                _migrate = MigrateTheme(tc, self.request)
                _migrate()

        if not hasattr(aq_base(context), 'right_slots'):
            slots = ['here/portlet_themes_related/macros/portlet',
                     'here/portlet_themes_rdf/macros/portlet']
            context.manage_addProperty('right_slots', slots, type='lines')

        if not hasattr(aq_base(context), 'left_slots'):
            slots = ['here/portlet_themes/macros/portlet', ]
            context.manage_addProperty('left_slots', slots, type='lines',)#,

        #if hasattr(aq_base(context), 'navigationmanager_menuid'):
        #    context.manage_addProperty('navigationmanager_menuid',
                                        #'themes',
                                        #type='string')

        alsoProvides(context, INavigationRoot)
        context.layout = 'themes_view'
        return self.request.RESPONSE.redirect(context.absolute_url())

class ThemeTaggable(object):
    """ Migrate theme tags to anootations
    """
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
            themes = [x for x in obj.schema['themes'].get(obj) if x is not None]
            tagging.tags = themes

class UpdateSmartFoldersAndTitles(object):
    """ Change all event topics to have end instead of start in criteria
    """
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
                date_crit = topic.addCriterion('end',
                                               'ATFriendlyDateCriteria')
                date_crit.setValue(0)
                date_crit.setDateRange('+')
                date_crit.setOperation('more')

            if 'crit__created_ATSortCriterion' in topic.objectIds():
                topic.deleteCriterion('crit__created_ATSortCriterion')
                topic.addCriterion('start', 'ATSortCriterion')

            # add custom fields to the events and highlight folders,
            # links don't need any as they shouldn't show anything in "detail"
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
        query = {'object_provides': 'eea.themecentre.interfaces.IThemeCentre'}
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
    """ Changes all IFeed marker interfaces to be IFeedContent markers
    """
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        return 'success'


class PromotionThemes(object):
    """ Old promotions might have themes as strings instead of lists
    """
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
        property instead.
    """

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
                    themecentre.manage_addProperty('default_page',
                                                   'intro',
                                                   'string')
                if not intro.hasProperty('layout'):
                    intro.manage_addProperty('layout',
                                             'themecentre_view',
                                             'string')
                themecentre._p_changed = True
        return str(len(brains)) + ' themecentres migrated'


class GenericThemeToDefault(object):
    """ Migrates theme tags ['G','e','n','e','r','i','c'] or
        ['D', 'e', 'f', 'a', 'u', 'l', 't'] to ['default'].
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        catalog = getToolByName(self.context, 'portal_catalog')
        query1 = { 'getThemes': 'G' }
        query2 = { 'getThemes': 'D' }
        query3 = { 'getThemes': 'g' }
        query4 = { 'getThemes': 'd' }
        queries = [query1, query2, query3, query4]
        output = ''
        for query in queries:
            brains = catalog.searchResults(query)
            for brain in brains:
                if (brain.getThemes == ['G', 'e', 'n', 'e', 'r', 'i', 'c'] or
                    brain.getThemes == ['g', 'e', 'n', 'e', 'r', 'i', 'c'] or
                    brain.getThemes == ['D', 'e', 'f', 'a', 'u', 'l', 't'] or
                    brain.getThemes == ['d', 'e', 'f', 'a', 'u', 'l', 't']):
                    obj = brain.getObject()
                    themes = IThemeTagging(obj)

                    output = (output + 'NOTOK: ' + obj.id + ': ' +
                              'brain.getThemes[0]: ' + brain.getThemes[0] +
                              ' themes.tags[0]: ' + (len(themes.tags) > 0 and
                                                     themes.tags[0] or '') +
                              ' URL: ' + obj.absolute_url() + '\r')

                    themes.tags = ['default']
                    obj.reindexObject()
                else:

                    output = (output + 'OK: ' + brain.id + ': ' +
                              'brain.getThemes[0]: ' + brain.getThemes[0] +
                              'URL:' + brain.getURL() + '\r')

        return 'themes are migrated, RESULT:\r' + output


class ChangeDefaultPageToProperty(object):
    """ Changes default_page to being a property so it's visible in ZMI
    """
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

            for folder in (x for x in (links, news, events) if x is not None):
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
        already.
    """
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

        return str(count) + " objects were tagged"


class ChangeMediaTypesDefault(object):
    """ Changes the media type on file's don't have any media type set.
        If media type not set, the type 'other' is set on the file.
    """
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        catalog = getToolByName(self.context, 'portal_catalog')
        brains = catalog.searchResults(
            object_provides='p4a.video.interfaces.IVideoEnhanced')
        for brain in brains:
            bfile = brain.getObject()
            media = IMediaType(bfile)
            if not media.types:
                media.types = ['other']
            file.reindexObject()

        return "migration successful"


class AddRichTextDescriptionToVideos(object):
    """ Adds an empty string to the rich_description field on all
        IVideoEnhanced objects. As this is a new field it's None
        and the edit page fails with a traceback.
    """
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        catalog = getToolByName(self.context, 'portal_catalog')
        brains = catalog.searchResults(
            object_provides='p4a.video.interfaces.IVideoEnhanced')
        for brain in brains:
            vfile = brain.getObject()
            video = IVideo(vfile)
            video.rich_description = u''
            video.urls = ()

        return str(len(brains)) + " videos where migrated."

class AddIVideoToVideos(object):
    """ Adds mediacentre IVideo marker interface to IVideoEnhanced objects
    """
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        catalog = getToolByName(self.context, 'portal_catalog')
        brains = catalog.searchResults(
            object_provides='p4a.video.interfaces.IVideoEnhanced',
            Language='all', show_inactive=True)
        count = 0
        for brain in brains:
            vfile = brain.getObject()
            if not IFlashAnimation.providedBy(vfile):
                alsoProvides(vfile, MIVideo)
                vfile.reindexObject(idxs=["object_provides"])
                count += 1
                if count % 50 == 0:
                    transaction.savepoint(optimistic=True)
        return str(len(brains)) + " videos where migrated."


class SetIVideoToAllVideosTopic(object):
    """ Change criteria on object_provides for all-videos Topic
    """
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        video = self.context.unrestrictedTraverse(
                                            'www/SITE/multimedia/all-videos')
        trans = video.getTranslations()
        for i in trans.values():
            topic = i[0]
            criteria = getattr(topic,
                    'crit__object_provides_ATSelectionCriterion', '')
            if criteria:
                criteria.setValue('eea.mediacentre.interfaces.IVideo')
        return "Done setting eea.mediacentre.interfaces.IVideo for all-videos"


class AddFolderAsLocallyAllowedTypeInLinks(object):
    """ Add the 'Folder' type as a locally addable type to
        all 'External link' folders in themecentres.
    """
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        catalog = getToolByName(self.context, 'portal_catalog')
        brains = catalog.searchResults(
            object_provides=IThemeCentre.__identifier__)
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
                    linkfolder.setImmediatelyAddableTypes(
                        immediate + ('Folder',))

        return 'successfully run'


class AddPressReleaseToHighlightsTopic(object):
    """ Adds PressRelease to the highlight topic's search criteria.
    """
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        catalog = getToolByName(self.context, 'portal_catalog')
        brains = catalog.searchResults(
            object_provides=IThemeCentre.__identifier__,
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
    """ Changes layout to mediacentre_view in the global multimedia folder
    """
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        portal_url = getToolByName(self.context, 'portal_url')
        portal = portal_url.getPortalObject()
        default_page = getattr(portal.SITE.multimedia, 'default_page', None)
        if default_page:
            multimedia = getattr(portal.SITE.multimedia, default_page)
            multimedia.manage_changeProperties(layout='mediacentre_view')
            return "layout property of %s is changed to %s." % \
                    (multimedia.absolute_url(), 'mediacentre_view')
        else:
            return "default_page property of multimedia not found, " \
                   "no migration done"


class MakeThemeMultimediaLayoutAProperty(object):
    """ Multimedia folders in themecentres have a layout property that's
        not visible in ZMI. Add it as a real property.
    """
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        catalog = getToolByName(self.context, 'portal_catalog')
        themeCentres = catalog.searchResults(
            object_provides=IThemeCentre.__identifier__)
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
        EEAWEBSITE_ECOTIP_Migration.csv file
    """
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
        """ Return
        """
        msg = "You called this script with this parameters:"
        msg += "\n\tsafe=%s" % self.safe
        msg += "\n\tpublish=%s" % self.publish
        msg += "\n\treindex=%s" % self.reindex
        msg += "\n\tlanguage=%s" % ', '.join(self.languages)
        msg += "\n\n"

        if self.safe:
            msg += "Translations NOT imported with %s warning(s). " % len(
                self.errors)
            msg += "To import ignoring warnings set safe param to False"
        else:
            msg += "Translations imported with %s error(s)" % len(self.errors)

        msg += "\n\n"

        return msg + '\n'.join(self.errors)

    def _raise(self, msg):
        """ Raise
        """
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
        """ Import
        """
        filename = os.path.join(os.path.dirname(__file__),
                                'EEAWEBSITE_ECOTIP_Migration.csv')
        reader = csv.reader(open(filename, 'r'),
                            delimiter='\t',
                            quotechar='"')
        reader.next()
        for index, row in enumerate(reader):
            if len(row) < 5:
                self._raise("Invalid row(%d) in csv file." % (index + 2))

            lang = row[0].strip().lower()
            en_title = row[1].strip()
            tr_title = row[2].strip()
            tr_desc = row[4].strip()
            key = self.tips.get(en_title, None)
            if not key:
                self._raise("I can not find this title in my green tips. "
                            "Language: %s, Title: %s" % (lang, en_title))
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
                self._raise('No translations found for %s(%s), '
                        '\n\tlanguages:\t%s' % (tip, title, ', '.join(junk)))

    def _add_translation(self, key, lang, title, description):
        """ Add trannslation
        """
        if lang not in self.languages:
            return

        translation = lang in self.imported.get(key, [])
        if translation:
            self._raise('Duplicated translation in csv file: '
                        '%s language: %s' % (key, lang))
            return

        self.imported.setdefault(key, [])
        self.imported[key].append(lang)

        tip = self.context._getOb(key)
        translation = tip.getTranslation(lang)
        if translation:
            self._raise("Already imported. I'll override it: %s, %s" %
                                                                (lang, key))

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
        """ Publish
        """
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
            self.logger.info('Published translation %s',
                             translation.absolute_url())

    def _reindex(self, translation):
        """ Reindex
        """
        if self.safe:
            return
        if not self.reindex:
            return

        ctool = getToolByName(self.context, 'portal_catalog')
        ctool.reindexObject(translation)
        self.logger.info('Reindexed translation %s', translation.absolute_url())

    def __call__(self, safe=True, publish=True, reindex=True, language='all'):
        if not self.context.getId() == 'green-tips':
            return ("Ops, you can run this migration script "
                    "only in green-tips context")

        self.safe = safe in [True, 1, 'True', '1', 'yes', 'on']
        self.publish = publish in [True, 1, 'True', '1', 'yes', 'on']
        self.reindex = reindex in [True, 1, 'True', '1', 'yes', 'on']
        if language == 'all':
            language = []
        if isinstance(language, str):
            language = [language, ]
        self.languages = language or self.context.getTranslations().keys()
        if 'en' in self.languages:
            self.languages.remove('en')
        self._prepare_tips()

        self._import()
        return self._return()


class MigrateDatesInCallForTendersAndInterests(object):
    """ #1787 required us to set value on the expiration and effective fields.
        This copies the dates open -> effective and close -> expire.
    """
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        catalog = getToolByName(self.context, 'portal_catalog')
        for b in catalog({'portal_type' : ['CallForTender',
                                           'CallForInterest']}):
            obj = b.getObject()
            obj.setCloseDate(obj.getCloseDate())
            obj.setOpenDate(obj.getOpenDate())


class FixImages(BrowserView):
    """ Fixes: some image blobs have no attribute "filename" set
    """

    def __call__(self):
        query = {'portal_type':{
                'query':[
                    'Image',
                    'Highlight',
                    'Article',
                    'Promotion',
                    'Speech',
                    'PressRelease',
                    'Blob' ,
                    'HelpCenterInstructionalVideo'
                    ],
                'operator':'or'
            }}

        brains = self.context.portal_catalog(query)
        for brain in brains:
            obj = brain.getObject()

            fields = ['image', 'screenshot']

            for name in fields:
                field = obj.getField(name)
                if field:
                    raw = field.getRaw(obj)
                    try:
                        if not raw.filename:
                            logger.info(
                                "Settings filename for field %s for %s" %
                                (name, obj))
                            raw.filename = obj.getId()
                    except Exception:
                        logger.error(
                            "MIGRATION ERROR when setting filename for %s",
                            brain.getURL())

        logger.info("Migration of field image filenames done")
        return "Done"


class ImageFSToBlobImageMigrator(ATFileToBlobMigrator):
    """migrator
    """
    src_portal_type = "ImageFS"
    src_meta_type = "ImageFS"
    dst_portal_type = "Image"
    dst_meta_type = "ATBlob"

    fields_map = {'image':'image'}

    def migrate_data(self):
        """override for migrate_data
        """
        #this is not needed because imagefs is already a blob
        #self.new.getField('image').getMutator(self.new)(self.old)


def getImageFSMigrationWalker(self):
    """walker
    """
    return getMigrationWalker(self, migrator=ImageFSToBlobImageMigrator)


class MigrateImageFS(BlobMigrationView):
    """migration
    """

    walker = getImageFSMigrationWalker

    def migration(self):
        """does migration
        """
        return migrate(self, walker=getImageFSMigrationWalker)


class MigratePortalRegistry(BrowserView):
    """ Fix portal_registry tuple field records
    """
    def __call__(self):
        util = getToolByName(self.context, 'portal_registry')
        recs = util.records
        faulty = []
        for k, v in recs.items():
            if not hasattr(v.field, 'defaultFactory'):
                v.field.defaultFactory = None
                faulty.append((k, v.fieldName))

            if hasattr(v.field, 'value_type'):
                ff = v.field.value_type
                if not hasattr(ff, 'defaultFactory'):
                    ff.defaultFactory = None
                    faulty.append((k, v.fieldName, 'value_type', ff))

            if hasattr(v.field, 'key_type'):
                ff = v.field.key_type
                if not hasattr(ff, 'defaultFactory'):
                    ff.defaultFactory = None
                    faulty.append((k, v.fieldName, 'key_type', ff))

        return "Fixed %s" % faulty


class FixPortalRelationItems(object):
    """ Fix attribute _at_creation_flag wrongly set to True of items to avoid 
    id renaming on title change
    """

    def __call__(self):
        relations = getToolByName(self.context, 'portal_relations')
        items = relations.objectItems()
        for i in items:
            if i[1]._at_creation_flag == True:
                i[1]._at_creation_flag = False
        return 'success'


class FixVocabularyTerms(object):
    """ Fix attribute _at_creation_flag wrongly set to True of
        vocabulary terms to avoid id renaming on title change
    """

    def __call__(self):
        catalog = getToolByName(self.context, 'portal_catalog')
        res = catalog.searchResults(portal_type =
                                    ['SimpleVocabularyTerm',
                                     'TreeVocabularyTerm'])
        for brain in res:
            obj = brain.getObject()
            try:
                if obj._at_creation_flag == True:
                    obj._at_creation_flag = False
                    obj._p_changed = True
                    logger.info("Creation flag updated: %s" % \
                                obj.absolute_url())
            except AttributeError:
                obj._at_creation_flag = False
                logger.info("Set creation flag: %s" % obj.absolute_url())
        return 'Vocabulary term updated.'



class MigrateGeotagsCountryGroups(BrowserView):
    """ Add Geotags Country Groups as individual countries
    """

    def startCapture(self, newLogLevel = None):
        """ Start capturing log output to a string buffer.

        http://opensourcehacker.com/2011/02/23/
                temporarily-capturing-python-logging-output-to-a-string-buffer/

        @param newLogLevel: Optionally change the global logging level, e.g. 
        logging.DEBUG
        """
        self.buffer = StringIO()

        print >> self.buffer, "Log output"

        rootLogger = logging.getLogger()

        if newLogLevel:
            self.oldLogLevel = rootLogger.getEffectiveLevel()
            rootLogger.setLevel(newLogLevel)
        else:
            self.oldLogLevel = None

        self.logHandler = logging.StreamHandler(self.buffer)
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s"
                                                            " - %(message)s")
        self.logHandler.setFormatter(formatter)
        rootLogger.addHandler(self.logHandler)

    def stopCapture(self):
        """ Stop capturing log output.
        @return: Collected log output as string
        """

        # Remove our handler
        rootLogger = logging.getLogger()

        # Restore logging level (if any)
        if self.oldLogLevel:
            rootLogger.setLevel(self.oldLogLevel)

        rootLogger.removeHandler(self.logHandler)

        self.logHandler.flush()
        self.buffer.flush()

        return self.buffer.getvalue()

    def __call__(self):
        country_groups = ["EU15", "EU25", "EU27", "EEA32", "EFTA4",
                                                    "Pan-Europa"]
        catalog = getToolByName(self.context, 'portal_catalog')
        res = catalog.searchResults(object_provides =
                                'eea.geotags.storage.interfaces.IGeoTagged')
        country_dict = countryGroups()
        count = 0
        self.startCapture(logging.DEBUG)
        logger.info("Starting Addition of individual Countries for Country"
                                                                    " Groups")
        for item in res:
            try:
                if item.geotags and item.geotags != "{ }":
                    geotags = json.loads(item.geotags)
            except ValueError:
                logger.error("%s --> couldn't be decoded", item.getURL())
                continue
            features = geotags['features']
            for feature in features:
                title = feature['properties'].get('title')
                if title and title in country_groups:
                    obj = item.getObject()
                    features.extend(country_dict[title])
                    # remove country group from the geotags feature list
                    features.remove(feature)

                    location = obj.getField('location')
                    location.set(obj, geotags)
                    try:
                        obj.reindexObject(idxs=['geotags', 'location'])
                    except Exception:
                        logger.error("%s --> couldn't be reindexed",
                                                        obj.absolute_url(1))
                        continue
                    logger.info('%s' % obj.absolute_url(1))
                    count += 1
                    if count % 50 == 0:
                        transaction.savepoint(optimistic=True)

        logger.info("%s number of items were migrated with individual countries"
                                                                % count)
        logger.info("Ending step of individual Countries for Country Groups")
        return self.stopCapture()


class FixFigureCategoryType(BrowserView):
    """ Fix Figure category to only have either Map or Graph as provided
    interface
    """

    def __call__(self):
        """ BrowserView call
        """
        context = self.context
        res = context.portal_catalog.searchResults(portal_type='EEAFigure')
        maps = "eea.dataservice.interfaces.IEEAFigureMap"
        graph = "eea.dataservice.interfaces.IEEAFigureGraph"
        count = 0
        for figure in res:
            if all([items in figure.object_provides for items in (maps,
                                                                  graph)]):
                obj = figure.getObject()
                figureType = obj.getField('figureType').getRaw(obj)
                if figureType == 'map':
                    directlyProvides(obj,
                                     directlyProvidedBy(obj) - IEEAFigureGraph)
                    logger.info('%s item has %s removed' % (
                        obj.get_absolute_url(1), 'IEEAFigureGraph interface'))
                elif figureType == 'graph':
                    directlyProvides(obj,
                                     directlyProvidedBy(obj) - IEEAFigureMap)
                    logger.info('%s item has %s removed' % (obj.absolute_url(
                        1), 'IEEAFigureMap interface'))
                obj.reindexObject(idxs=['object_provides'])
                count += 1
                if count % 50 == 0:
                    transaction.savepoint(optimistic=True)

        logger.info("%s number of items were migrated with fixed "
                    "FigureCategory"
                    % count)
        return "Done"

class RemoveInactivePromotions(object):
    """ Old promotions might have themes as strings instead of lists
    """
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        catalog = getToolByName(self.context, 'portal_catalog')
        query = {
            'object_provides':
                'eea.promotion.interfaces.IPromoted'
        }
        brains = catalog.searchResults(query)
        not_migrated = ''
        for brain in brains:
            obj = brain.getObject()
            promo = IPromotion(obj)
            if not promo.active:
                #import pdb; pdb.set_trace()
                noLongerProvides(obj, IPromoted)
                obj.reindexObject(idxs=['object_provides'])
        if not_migrated:
            return 'Some objects were not migrated\n' + not_migrated
        else:
            return 'success'


class MigrateGeographicalCoverageToGeotags(object):
    """ Migrate Geographical Coverage to Geotags
    """
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        """ Call method
        """
        catalog = getToolByName(self.context, 'portal_catalog')
        query = {
            'portal_type':
                'Data'
        }

        util = queryUtility(ICountryAvailability)
        all_countries = util.getCountries()
        brains = catalog.searchResults(query)
        differentGeotagsLength = []
        country_dicts = countryDicts()
        count = 0
        for brain in brains:
            countries_names = set()
            location = brain.location
            coverage = brain.getGeographicCoverage
            len_location = len(location)
            len_coverage = len(coverage)
            if len_location < len_coverage:
                for country in coverage:
                    countries_names.add(all_countries.get(country)['name'])
                extra_countries = countries_names.difference(location)
                obj = brain.getObject()
                geotags = json.loads(brain.geotags)
                for country in extra_countries:
                    features = geotags['features']
                    features.extend(country_dicts.get(country, ''))
                location = obj.getField('location')
                location.set(obj, geotags)
                try:
                    obj.reindexObject(idxs=['geotags', 'location'])
                except Exception:
                    logger.error("%s --> couldn't be reindexed",
                                 obj.absolute_url(1))
                    continue
                logger.info('%s' % obj.absolute_url(1))
                count += 1
                if count % 50 == 0:
                    transaction.savepoint(optimistic=True)
                differentGeotagsLength.append(brain.getURL())
        if differentGeotagsLength:
            return 'Some objects were not migrated\n' + ",\n".join(
                   differentGeotagsLength) + " items " + str(len(
                differentGeotagsLength))
        else:
            return 'success'
