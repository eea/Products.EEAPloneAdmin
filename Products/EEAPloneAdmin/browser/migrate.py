""" Migrate
"""
import csv
import logging
import os
import urllib
import transaction
import json
from zope.annotation import IAnnotations
from zope.interface import alsoProvides
from zope.interface import directlyProvides
from zope.interface import directlyProvidedBy
from zope.interface import noLongerProvides
from zope.component import queryUtility
from zope.component import queryAdapter
from zope.component import ComponentLookupError
from zope.component import getMultiAdapter
from zope.component.interface import nameToInterface
from Acquisition import aq_base
from DateTime.DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.CMFCore.permissions import AccessContentsInformation, View
from pprint import pprint
from eea.promotion.interfaces import IPromotion, IPromoted
from eea.themecentre.browser.themecentre import PromoteThemeCentre
from eea.themecentre.interfaces import IThemeCentreSchema, IThemeRelation
from eea.themecentre.interfaces import IThemeTagging, IThemeCentre
from eea.themecentre.themecentre import createFaqSmartFolder, getThemeCentre
from plone.app.blob.browser.migration import BlobMigrationView
from plone.app.blob.migrations import ATFileToBlobMigrator, getMigrationWalker
from plone.app.blob.migrations import migrate
from plone.app.layout.navigation.interfaces import INavigationRoot
from plone.app.layout.viewlets.content import ContentHistoryView
from eea.mediacentre.interfaces import IVideo as MIVideo
from Products.EEAContentTypes.content.interfaces import IFlashAnimation
from cStringIO import StringIO
from eea.dataservice.interfaces import IEEAFigureMap, IEEAFigureGraph
from plone.i18n.locales.interfaces import ICountryAvailability

from Products.EEAPloneAdmin.browser.migration_helper_data import \
    countryDicts, countryGroups, data_versions, urls_for_73422

from eea.geotags.interfaces import IJsonProvider
from eea.workflow.interfaces import IObjectArchivator

try:
    from eea.versions.versions import IVersionControl
    has_versions = True
except ImportError:
    has_versions = False

logger = logging.getLogger("Products.EEAPloneAdmin")

url = 'http://themes.eea.europa.eu/migrate/%s?theme=%s'

# Some new theme ids are not same as old
themeIdMap = {'coasts_seas' : 'coast_sea',
              'fisheries' : 'fishery',
              'human_health' : 'human',
              'natural_resources' : 'natural',
              'env_information' : 'information',
              'env_management' : 'management',
              'env_reporting' : 'reporting',
              'env_scenarios' : 'scenarios',
              'various' : 'other_issues'}


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
                    currentThemes = [currentThemes,]
                newThemes = [themeIdMap.get(r, r) for r in currentThemes]
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
                                           id='theme_image',
                                           title='%s - Theme image' %
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
        related = [theme.strip() for theme in related.split(',')]
        theme = IThemeRelation(self.context)
        themeCentres = self.context.portal_catalog.searchResults(
            object_provides='eea.themecentre.interfaces.IThemeCentre')
        tcs = {}
        for tc in themeCentres:
            tcs[tc.getId] = tc.getObject().UID()
        themeCentres = tcs

        # map old theme id to new
        related = [themeIdMap.get(r, r) for r in related]

        # ZZZ need to find UID for the related theme centres
        related = [themeCentres.get(rel) for rel in related]
        related = [rl for rl in related if rl is not None]
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
            slots = ['here/portlet_themes/macros/portlet',]
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
        query = {'portal_type': 'Topic',
                 'id': 'events_topic'}
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
        query = {'portal_type': 'Topic',
                 'id': 'highlights_topic'}
        brains = catalog.searchResults(query)
        for brain in brains:
            topic = brain.getObject()
            topic.setCustomViewFields(['EffectiveDate'])

        # remove custom field on all link topics
        query = {'portal_type': 'Topic',
                 'id': 'links_topic'}
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
        query = {'portal_type': 'Topic',
                 'path': '/'.join(self.context.getPhysicalPath())}
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
        query = {'portal_type': 'Promotion'}
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
        query1 = {'getThemes': 'G'}
        query2 = {'getThemes': 'D'}
        query3 = {'getThemes': 'g'}
        query4 = {'getThemes': 'd'}
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


# class AddRichTextDescriptionToVideos(object):
#     """ Adds an empty string to the rich_description field on all
#         IVideoEnhanced objects. As this is a new field it's None
#         and the edit page fails with a traceback.
#     """
#     def __init__(self, context, request):
#         self.context = context
#         self.request = request
#
#     def __call__(self):
#         catalog = getToolByName(self.context, 'portal_catalog')
#         brains = catalog.searchResults(
#             object_provides='p4a.video.interfaces.IVideoEnhanced')
#         for brain in brains:
#             vfile = brain.getObject()
#             video = IVideo(vfile)
#             video.rich_description = u''
#             video.urls = ()
#
#         return str(len(brains)) + " videos where migrated."

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
            language = [language,]
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
                    'Blob',
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
                                "Settings filename for field %s for %s",
                                name, obj)
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
            if i[1]._at_creation_flag is True:
                i[1]._at_creation_flag = False
        return 'success'


class FixVocabularyTerms(object):
    """ Fix attribute _at_creation_flag wrongly set to True of
        vocabulary terms to avoid id renaming on title change
    """

    def __call__(self):
        catalog = getToolByName(self.context, 'portal_catalog')
        res = catalog.searchResults(portal_type=
                                    ['SimpleVocabularyTerm',
                                     'TreeVocabularyTerm'])
        for brain in res:
            obj = brain.getObject()
            try:
                if obj._at_creation_flag is True:
                    obj._at_creation_flag = False
                    obj._p_changed = True
                    logger.info("Creation flag updated: %s",
                                obj.absolute_url())
            except AttributeError:
                obj._at_creation_flag = False
                logger.info("Set creation flag: %s", obj.absolute_url())
        return 'Vocabulary term updated.'


def startCapture(self, newLogLevel=None):
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

class MigrateGeotagsCountryGroups(BrowserView):
    """ Add Geotags Country Groups as individual countries
    """


    def __call__(self):
        country_groups = ["EU15", "EU25", "EU27", "EEA32", "EFTA4",
                                                    "Pan-Europa"]
        catalog = getToolByName(self.context, 'portal_catalog')
        res = catalog.searchResults(object_provides=
                                'eea.geotags.storage.interfaces.IGeoTagged')
        country_dict = countryGroups()
        count = 0
        startCapture(self, logging.DEBUG)
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
                    logger.info('%s', obj.absolute_url(1))
                    count += 1
                    if count % 50 == 0:
                        transaction.savepoint(optimistic=True)

        logger.info("%s number of items were migrated with individual countries"
                                                                , count)
        logger.info("Ending step of individual Countries for Country Groups")
        return stopCapture(self)


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
                    logger.info('%s item has %s removed',
                        obj.get_absolute_url(1), 'IEEAFigureGraph interface')
                elif figureType == 'graph':
                    directlyProvides(obj,
                                     directlyProvidedBy(obj) - IEEAFigureMap)
                    logger.info('%s item has %s removed', obj.absolute_url(
                        1), 'IEEAFigureMap interface')
                obj.reindexObject(idxs=['object_provides'])
                count += 1
                if count % 50 == 0:
                    transaction.savepoint(optimistic=True)

        logger.info("%s number of items were migrated with fixed "
                    "FigureCategory", count)
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
            'portal_type': ['Assessment', 'Data', 'EEAFigure']
        }
        log = logging.getLogger("GeographicalCoverageToGeotags")

        util = queryUtility(ICountryAvailability)
        all_countries = util.getCountries()
        brains = catalog.searchResults(query)
        differentGeotagsLength = []
        country_dicts = countryDicts()
        missing_countries_message = set()
        non_matching_countries_message = set()
        count = 0

        acronymes = {
            'Russian Federation': 'Russia',
            'Czech Republic': 'Czechia',
            'Macedonia the former Yugoslavian Republic of': 'Macedonia',
            'Moldova Republic of': 'Moldova'}
        jsonservice = queryAdapter(self.context, IJsonProvider)

        for brain in brains:
            brain_url = brain.getURL()
            countries_names = set()
            location = brain.location
            coverage = brain.getGeographicCoverage
            len_location = len(location)
            len_coverage = len(coverage)
            missing_countries = []
            non_matching_countries = []
            if len_location < len_coverage:
                for country in coverage:
                    try:
                        name = all_countries.get(country)['name']
                        potential_dulicated_name = acronymes.get(name)
                        if potential_dulicated_name and \
                                        potential_dulicated_name in \
                            location:
                            continue
                        countries_names.add(name)
                    except Exception:
                        missing_countries.append(country)
                    continue
                if missing_countries:
                    missing_countries_message.add("For %s --> %s countries "
                                                  "DO NOT EXIST" % (
                        brain_url, missing_countries
                    ))

                extra_countries = countries_names.difference(location)
                obj = brain.getObject()
                if brain.geotags and brain.geotags != "{ }":
                    geotags = json.loads(brain.geotags)
                else:
                    geotags = {'type': "FeatureCollection", 'features': []}
                features = geotags['features']
                for country in extra_countries:
                    res = country_dicts.get(country, '')
                    if res:
                        features.append(res)
                    else:
                        if country == 'Serbia and Montenegro':
                            features.append(country_dicts.get('Serbia'))
                            features.append(country_dicts.get(
                                'Montenegro'))
                            continue
                        match = jsonservice.search(q=country,
                                                   maxRows=1)['features']
                        if match:
                            match = match[0]
                            features.append(match)
                            country_dicts[country] = match
                        else:
                            non_matching_countries.append(country)
                if non_matching_countries:
                    non_matching_countries_message.add("For %s --> %s "
                                                "countries ARE NOT FOUND" % (
                        brain_url, non_matching_countries
                    ))
                features.sort(key=lambda k: k['properties']['title'])
                location = obj.getField('location')
                try:
                    location.set(obj, geotags)
                    obj.reindexObject(idxs=['geotags', 'location'])
                except Exception:
                    log.error("%s --> couldn't be reindexed",
                                 obj.absolute_url(1))
                    continue
                count += 1
                if count % 50 == 0:
                    transaction.savepoint(optimistic=True)
                differentGeotagsLength.append(brain_url)
        if differentGeotagsLength:
            length_message = 'These %d objects were migrated\n %s' % (len(
                differentGeotagsLength), ",\n".join(differentGeotagsLength))

            non_existing_country_message = "\n\n these objects had countries " \
                        "which aren't existing %s" % \
                                        ",\n".join(missing_countries_message)

            not_found_country_message = '\n\n these objects had countries ' \
                        'which are not found %s' % \
                                    ",\n".join(non_matching_countries_message)

            log.info(length_message + not_found_country_message +
                            non_existing_country_message)

            return length_message + not_found_country_message + \
                            non_existing_country_message



class RenameMisnamedLocations(object):
    """ Rename Country Names with mapping found withing countries_mapping
        vocabulary
    """
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        """ Call method
        """
        log = logging.getLogger("RenameMisnamedLocations")
        log.info("Starting Renaming of CountryNames")
        catalog = getToolByName(self.context, 'portal_catalog')
        query = {
            'object_provides': 'eea.geotags.storage.interfaces.IGeoTagged'
        }
        atvm = getToolByName(self.context, 'portal_vocabularies')
        voc = atvm.get('countries_mapping')
        keys = voc.keys()
        count = 0
        found = 0
        set_keys = set(keys)
        res = catalog.unrestrictedSearchResults(query)
        for brain in res:
            set_brain = set(brain.location)
            matches = set_keys.intersection(set_brain)
            if matches:
                obj = brain.getObject()
                geotags = json.loads(brain.geotags)
                features = geotags['features']
                for key in matches:
                    title = voc.get(key).title
                    for feature in features:
                        if feature['properties']['description'] == key:
                            feature['properties']['description'] = title
                            feature['properties']['title'] = title
                            break
                try:
                    location = obj.getField('location')
                    location.set(obj, geotags)
                    log.info(obj.absolute_url(1))
                    obj.reindexObject(idxs=['geotags', 'location'])

                except Exception:
                    log.error("%s --> couldn't be reindexed",
                              obj.absolute_url(1))
                    continue
                found += 1
                count += 1
                if count % 50 == 0:
                    transaction.commit()
        log.info("Ending Renaming of CountryNames")
        return "Done renaming %s objects" % found


class CheckRemainingInterfaces(object):
    """ Check all objects on site for matching text found within the
        object_provides tuple
    """
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        """ Call method
        """
        log = logging.getLogger("CheckRemainingInterfaces")
        match = {}
        search_term = self.request.get('term')
        if not search_term:
            return "NO search terms has been passed"
        log.info("START checking for %s within object_provides of all objects",
                 search_term)
        ca = self.context.portal_catalog
        res = ca.searchResults(Language="all")
        for f in res:
            provides = f.object_provides
            for item in provides:
                if search_term in item:
                    if item not in match:
                        match[item] = 1
                    else:
                        match[item] += 1
        log.info("END checking for %s within object_provides of all objects",
                 search_term)
        return pprint(match)


def remove_interface(context, iname):
    """ Helper method to get rid of interfaces
    """
    log = logging.getLogger("remove_interface")
    count = 0

    ca = context.portal_catalog
    res = ca.searchResults(object_provides=iname, Language="all")
    total = len(res)
    log.info("STARTED removal of %s from all %s objects that provide it",
             iname, total)
    try:
        provided_interface = nameToInterface(context, iname)
    except ComponentLookupError:
        log.warn('Cant find interface from %s name', iname)
        provided_interface = False
    for f in res:
        obj = f.getObject()
        try:
            if provided_interface:
                noLongerProvides(obj, provided_interface)
            obj.reindexObject(idxs=["object_provides"])
        except Exception:
            log.error("%s --> couldn't be reindexed",
                      obj.absolute_url(1))
        count += 1
        if count % 100 == 0:
            transaction.commit()
            log.info('INFO: Subtransaction committed to zodb (%s/%s)', count,
                                                                          total)
    log.info("ENDED removal of %s from all %s, objects that provide it",
             iname, count)
    return "ENDED removal of %s from all %s, objects that provide it" % (iname,
                                                                         total)


class CreatorAssignment(object):
    """ Add as primary creator the user that made the last version
    """
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        """ Call method
        """
        log = logging.getLogger("CreatorFix")
        log.info("Starting Creators index fix")
        catalog = getToolByName(self.context, 'portal_catalog')
        count = 0
        #history_error = "\n\n HISTORY ERRORS \n"
        reindex_error = "\n\n REINDEX ERRORS \n"
        set_error = "\n\n SETCREATION ERRORS \n"
        not_found = "\n\n OBJ NOT FOUND \n"
        res_creators = "\n\n RESULTING CREATORS \n"

        ptypes = ["Article", "Assessment", "AssessmentPart", "CallForInterest",
                "CallForTender", "CloudVideo", "Collection",
                "CommonalityReport", "Data", "DataFile", "DataFileLink",
                "DataSourceLink", "DataTable", "DavizVisualization",
                "DiversityReport", "Document", "EEAFigure", "EEAVacancy",
                "EcoTip", "EpubFile", "Event", "ExternalDataSpec",
                "EyewitnessStory", "FactSheetDocument", "Fiche", "File",
                "FlashFile", "FlexibilityReport", "Folder", "GIS Application",
                "HelpCenter", "HelpCenterDefinition",
                "HelpCenterErrorReferenceFolder", "HelpCenterFAQ",
                "HelpCenterFAQFolder", "HelpCenterGlossary", "HelpCenterHowTo",
                "HelpCenterHowToFolder", "HelpCenterInstructionalVideo",
                "HelpCenterInstructionalVideoFolder", "HelpCenterLink",
                "HelpCenterLinkFolder", "HelpCenterReferenceManualFolder",
                "HelpCenterTutorialFolder", "Highlight", # "Image",
                "IndicatorFactSheet", "Infographic", "KeyMessage", "Link",
                "MethodologyReference", "News Item", "Newsletter",
                "Organisation", "PolicyDocumentReference", "PolicyQuestion",
                "PressRelease", "Promotion", "QuickEvent",
                "RationaleReference", "RelatedIndicatorLink", "Report",
                "SOERCountry", "SOERKeyFact", "SOERMessage", "Sparql",
                "SparqlBookmarksFolder", "Specification", "Speech", "Topic"]
        res = catalog.unrestrictedSearchResults(portal_type=ptypes)
        context = self.context
        hunter = getMultiAdapter((context, self.request), name='pas_search')
        total = len(res)
        #request = self.context.REQUEST
        for brain in res:
            obj_url = brain.getURL(1)
            # try:
            #     obj = brain.getObject()
            # except Exception:
            #     not_found += obj_url + "\n"
            #     continue
            # history = None
            # try:
            #     history = ContentHistoryView(obj, request).fullHistory()
            # except Exception, err:
            #     history_error += "%s --> %s \n" % (obj_url, err)
            # if not history:
            #     continue
            # first_state = history[-1]
            # creators = []
            # for entry in history:
            #     if entry['action'] == 'New version' or entry == first_state:
            #         user = entry['actorid']
            #         if user and user not in creators:
            #             creators.append(user)
            # original_creators = obj.Creators()
            # for creator in original_creators:
            #     if creator and creator not in creators:
            #         creators.append(creator)
            original_creators = brain.listCreators
            creators = list(original_creators)
            for creator in original_creators:
                if len(creator.split(' ')) > 1:
                    try:
                        obj = brain.getObject()
                    except Exception:
                        not_found += obj_url + "\n"
                        continue
                    users = hunter.searchUsers(**{'fullname': creator})
                    if not users:
                        continue
                    for user in users:
                        if user.get('userid') in creators:
                            creators.remove(creator)

            if original_creators == tuple(creators):
                continue
            res_creators += "\n %s --> %s --> %s \n" % (obj_url,
                                                        original_creators,
                                                        creators)
            try:
                obj.setCreators(creators)
            except Exception, err:
                set_error += "%s --> %s \n" % (obj_url, err)
            try:
                obj.reindexObject(idxs=['Creator'])
            except Exception, err:
                reindex_error += "%s --> %s \n" % (obj_url, err)
                continue
            count += 1
            if count % 100 == 0:
                log.info('INFO: Subtransaction committed to zodb (%s/%s)',
                         count, total)
                transaction.commit()

        log.info("Ending Creators index fix for %d objects", count)

        return res_creators + reindex_error + set_error + not_found


class FixEffectiveDateForPublishedObjects(object):
    """ Fix published objects with no effective date
    """
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        """ Call method
        """
        log = logging.getLogger("EffectiveDate fix:")
        log.info("Starting Effective Date index report")
        catalog = getToolByName(self.context, 'portal_catalog')

        search_date = DateTime('1001/01/01 00:00:00')
        search_no_effective_date = {
            'query': search_date,
            'range': 'max'
        }

        no_effective_date = DateTime('1000/01/01 00:00:00')
        no_effective_date_str = 'None'

        log.info("Catalog search start")
        brains = catalog(review_state="published",
                         Language="all",
                         effective=search_no_effective_date,
                         show_inactive=True)
        request = self.context.REQUEST
        batch = request.get('b', None)
        log.info("Catalog search ended")

        res_objs = ["\n\n AFFECTED OBJS \n"]
        skipped_objs = ["\n\n SKIPPED OBJS WITH TRANSLATIONS" \
                    " THAT HAVE EFFECTIVE DATE LOWER THAN THE CREATION DATE \n"]
        reindex_error = ["\n\n REINDEX ERRORS \n"]
        not_found = ["\n\n OBJ NOT FOUND \n"]
        history_error = ["\n\n HISTORY ERRORS \n"]

        if brains:
            log.error(
                "Objects with affected EffectiveDate found: %s", len(brains)
        )

        if batch is not None and batch.isdigit():
            brains = brains[:int(batch)]

        total = len(brains)
        count = 0
        count_progress = 0
        skipped_objs_count = 0
        ignore_brain = 0

        log.info("Starting Effective Date index fix for %d objects", total)

        default_lang = ["en"]
        for brain in brains:
            count_progress += 1
            if ignore_brain:
                if brain.getURL() == 'MY_URL_TO_BE_SKIPPED':
                    ignore_brain = 0
                log.info("%s/%s :: SKIPPING brain %s", count_progress,
                                                       total, brain.getURL())
                continue
            log.info("%s/%s :: Current brain %s", count_progress, total,
                                                  brain.getURL())
            created_date = brain.created
            effective_date = brain.effective
            obj_url = brain.getURL(1)
            try:
                obj = brain.getObject()
            except Exception:
                not_found.append("%s \n" % obj_url)
                log.info("SKIPPED not found")
                continue

            if obj.getTranslationLanguages() != default_lang:
                # set effective date only for objects where even their
                # translations have no date and the effective date is bigger
                # than the creation date of any of the translations otherwise
                # we might set a wrong effective date for them
                translations = obj.getTranslations().values()
                translations = [translation[0] for translation in translations]
                canSetEffectiveDate = True
                effective_dates_list = []
                creation_dates_list = []
                for translation in translations:
                    date = translation.effective()
                    string_date = translation.EffectiveDate()
                    creation_dates_list.append(translation.creation_date)
                    if string_date != no_effective_date_str:
                        effective_dates_list.append(date)
                for ef_date in effective_dates_list:
                    for cr_date in creation_dates_list:
                        if ef_date < cr_date:
                            canSetEffectiveDate = False
                if not canSetEffectiveDate:
                    skipped_objs.append("%s \n" % obj_url)
                    skipped_objs_count += 1
                    log.info("SKIPPED getTranslationLanguages")
                    continue
            history = None
            try:
                history = ContentHistoryView(obj, request).fullHistory()
            except Exception, err:
                history_error.append("%s --> %s \n" % (obj_url, err))
            if not history:
                log.info("No history, set creation date")
                obj.edit(effectiveDate=created_date)
                log.info("EFFECTIVE DATE set: %s", created_date)
                res_objs.append("\n %s - Effective Date before --> %s "
                          "after --> %s \n" % (obj_url, effective_date,
                                                        created_date))
                if obj.effective() == no_effective_date:
                    obj.setEffectiveDate(created_date)
                obj.reindexObject(idxs=["EffectiveDate"])
                count += 1
                continue
            first_state = history[-1]
            for entry in history:

                if entry['transition_title'] == 'Publish' or entry == \
                        first_state:
                    date = entry['time']
                    creationIsAfterPublish = False
                    if created_date > date:
                        #obj.setEffectiveDate(created_date)
                        obj.edit(effectiveDate=created_date)
                        if obj.effective() == no_effective_date:
                            obj.setEffectiveDate(created_date)
                        log.info("EFFECTIVE DATE set: %s", created_date)
                        creationIsAfterPublish = True
                    else:
                        #obj.setEffectiveDate(date)
                        obj.edit(effectiveDate=date)
                        if obj.effective() == no_effective_date:
                            obj.setEffectiveDate(date)
                        log.info("EFFECTIVE DATE set: %s", date)
                    try:
                        obj.reindexObject(idxs=["EffectiveDate"])
                    except Exception, err:
                        reindex_error.append("%s --> %s \n" % (obj_url, err))
                        log.info("ERROR on reindex")
                        continue

                    if creationIsAfterPublish:
                        res_objs.append("\n %s -Effective Date before --> %s"
                                " after --> %s from Creation Date because"
                                " it is after date from history --> %s \n" % (
                                obj_url, effective_date, created_date, date))
                    else:
                        res_objs.append("\n %s - Effective Date before --> %s "
                            "after --> %s \n" % (obj_url, effective_date, date))
                    log.info("### BREAK")
                    break
            if count_progress % 5 == 0:
                log.info('Transaction committed to zodb (%s/%s)',
                         count_progress, total)
                transaction.commit()
        skipped_obj_count_message = "\n SKIPPED OBJECTS TOTAL: %d" % \
                skipped_objs_count

        count_message = "\n MODIFIED OBJECTS TOTAL: %d" % count

        log.info("DONE Effective Date index fix for %d objects", count)
        res_objs_msg = " ".join(res_objs)
        skipped_objs_msg = " ".join(skipped_objs)
        reindex_error_msg = " ".join(reindex_error)
        history_error_msg = " ".join(history_error)
        not_found_msg = " ".join(not_found)
        return "%s %s %s %s %s %s %s " % (count_message, res_objs_msg,
                                          skipped_obj_count_message,
                                          skipped_objs_msg,
                                          reindex_error_msg,
                                          history_error_msg, not_found_msg)


class ReportEffectiveDateForPublishedObjects(object):
    """ Report published objects with no effective date
    """
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        """ Call method
        """
        log = logging.getLogger("EffectiveDate report:")
        log.info("*** Starting Effective Date index report")
        catalog = getToolByName(self.context, 'portal_catalog')

        search_date = DateTime('1001/01/01 00:00:00')
        search_no_effective_date = {
            'query': search_date,
            'range': 'max'
        }
        no_effective_date_str = 'None'

        log.info("Catalog search start")
        brains = catalog(review_state="published",
                         Language="all",
                         effective=search_no_effective_date,
                         show_inactive=True)
        request = self.context.REQUEST
        log.info("Catalog search ended")

        res_objs = ["\n\n AFFECTED OBJS \n"]
        skipped_objs = ["\n\n SKIPPED OBJS WITH TRANSLATIONS" \
                    " THAT HAVE EFFECTIVE DATE LOWER THAN THE CREATION DATE \n"]
        reindex_error = ["\n\n REINDEX ERRORS \n"]
        not_found = ["\n\n OBJ NOT FOUND \n"]
        history_error = ["\n\n HISTORY ERRORS \n"]

        total = len(brains)
        count = 0
        count_progress = 0
        skipped_objs_count = 0
        ignore_brain = 0

        log.info("Starting Effective Date index report for %d objects", total)

        default_lang = ["en"]
        for brain in brains:
            count_progress += 1
            if ignore_brain:
                if brain.getURL() == 'MY_URL_TO_BE_SKIPPED':
                    ignore_brain = 0
                log.info("%s/%s :: SKIPPING brain %s", count_progress,
                                                       total, brain.getURL())
                continue
            log.info("%s/%s :: Current brain %s", count_progress,
                                                  total, brain.getURL())
            created_date = brain.created
            effective_date = brain.effective
            obj_url = brain.getURL(1)
            try:
                obj = brain.getObject()
            except Exception:
                not_found.append("%s \n" % obj_url)
                log.info("SKIPPED not found")
                continue

            if obj.getTranslationLanguages() != default_lang:
                # set effective date only for objects where even their
                # translations have no date and the effective date is bigger
                # than the creation date of any of the translations otherwise
                #  we might set a wrong effective date for them
                translations = obj.getTranslations().values()
                translations = [translation[0] for translation in translations]
                canSetEffectiveDate = True
                effective_dates_list = []
                creation_dates_list = []
                for translation in translations:
                    date = translation.effective()
                    string_date = translation.EffectiveDate()
                    creation_dates_list.append(translation.creation_date)
                    if string_date != no_effective_date_str:
                        effective_dates_list.append(date)
                for ef_date in effective_dates_list:
                    for cr_date in creation_dates_list:
                        if ef_date < cr_date:
                            canSetEffectiveDate = False
                if not canSetEffectiveDate:
                    skipped_objs.append("%s \n" % obj_url)
                    skipped_objs_count += 1
                    log.info("SKIPPED getTranslationLanguages")
                    continue
            history = None
            try:
                history = ContentHistoryView(obj, request).fullHistory()
            except Exception, err:
                history_error.append("%s --> %s \n" % (obj_url, err))
            if not history:
                log.info("SKIPPED no history")
                continue
            first_state = history[-1]
            for entry in history:

                if entry['transition_title'] == 'Publish' or entry == \
                        first_state:
                    date = entry['time']
                    creationIsAfterPublish = False
                    if created_date > date:
                        creationIsAfterPublish = True

                    if creationIsAfterPublish:
                        res_objs.append("\n %s - %s -Effective Date before -->"
                                " %s after --> %s from Creation Date because"
                                " it is after date from history --> %s \n" % (
                                obj.portal_type, obj_url, effective_date,
                                created_date, date))
                    else:
                        res_objs.append("\n %s - %s - Effective Date before -->"
                            " %s after --> %s \n" % (obj.portal_type, obj_url,
                            effective_date, date))

                    count += 1
                    log.info("### BREAK ###")
                    break
        skipped_obj_count_message = "\n SKIPPED OBJECTS TOTAL: %d" % \
                skipped_objs_count

        count_message = "\n REPORTED OBJECTS TOTAL: %d" % count

        log.info("DONE Effective Date index report for %d objects", count)
        res_objs_msg = " ".join(res_objs)
        skipped_objs_msg = " ".join(skipped_objs)
        reindex_error_msg = " ".join(reindex_error)
        history_error_msg = " ".join(history_error)
        not_found_msg = " ".join(not_found)
        return "%s %s %s %s %s %s %s " % (count_message, res_objs_msg,
                                          skipped_obj_count_message,
                                          skipped_objs_msg,
                                          reindex_error_msg,
                                          history_error_msg, not_found_msg)


class FixEEAFigureFilesPublishDate(object):
    """ Fix EEAFigureFile objects with old effective date
    """
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        """ Call method
        """
        log = logging.getLogger("EffectiveFixForEEAFigureFile")
        catalog = getToolByName(self.context, 'portal_catalog')
        brains = catalog(portal_type="EEAFigureFile", show_inactive="True")
        count = 0
        total = len(brains)
        log.info("START effective date index fix for %d objects", total)
        urls = []
        for brain in brains:
            if brain.EffectiveDate != 'None':
                obj = brain.getObject()
                parent = obj.aq_parent
                obj_date = obj.effective_date
                parent_date = parent.effective_date
                if obj_date < parent_date:
                    count += 1
                    obj.setEffectiveDate(parent_date)
                    obj.reindexObject(idxs=["effective"])
                    urls.append(obj.absolute_url(1))
                    if count % 100 == 0:
                        log.info('INFO: Transaction committed to zodb (%s/%s)',
                                 count, total)
                        transaction.commit()
        log.info("Fixed %d EEAFigureFile effectiveDate", count)
        log.info("END effective date index fix for %d objects", total)
        res_objs_urls = "\n".join(urls)
        return res_objs_urls


class MigrateDavizAnnotationData(object):
    """ Migrate existing data to conform to current data spec
    """
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        """ Call method
        """
        log = logging.getLogger(__name__)
        catalog = getToolByName(self.context, 'portal_catalog')
        brains = catalog(portal_type="DavizVisualization", show_inactive="True")
        log.info("START data annotation fix for Daviz objects")
        msgs = []
        for brain in brains:
            obj = brain.getObject()
            anno = IAnnotations(obj)
            daviz = anno.get('eea.daviz.config.json')
            if not daviz:
                continue
            prop = daviz.get('properties')
            if prop:
                order = 0
                for key, value in prop.items():
                    if isinstance(value, unicode):
                        order += 1
                        new_val = {'valueType': value, 'columnType': value,
                                   'order': order, 'label': key.capitalize()}
                        prop[key] = new_val
                        daviz._p_changed = True
                        objurl = obj.absolute_url()
                        msg = 'Broken DavizVisualization at %s changed data' \
                              ' from %s to %s \n' % (objurl, key, new_val)
                        msgs.append(msg)
                        log.info(msg)
        log.info("END data annotation fix for Daviz objects")
        return msgs




class CheckTemplatesForArchiveMessage(object):
    """ Check folder contents with each template if archive message is present
    """
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        context = self.context
        res = context.getFolderContents()
        match = {}
        for brain in res:
            obj = brain.getObject()
            ptype = obj.portal_type
            match[ptype] = []
            adapter = IObjectArchivator(obj)
            adapter.archive(obj, **dict(initiator='ichimdav',
                                        reason='content_is_outdated',
                                        custom_message=''))
            layouts = obj.getAvailableLayouts()
            for layout_tuple in layouts:
                tname = layout_tuple[0]
                template = obj.restrictedTraverse(tname)()
                if 'archive_status' not in template:
                    match[ptype].append(tname)
        return pprint(match)


class SetSparqlRefreshFrequencyToWeekly(object):
    """ Change Sparql Refresh frequency to weekly
    """
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        """ Call method
        """
        log = logging.getLogger("Sparql refresh frequency")
        log.info("*** Starting Sparql refresh frequency report")
        catalog = getToolByName(self.context, 'portal_catalog')

        log.info("*** Catalog search start")
        brains = catalog(review_state="published",
                         Language="all",
                         portal_type="Sparql",
                         show_inactive=True)
        log.info("*** Catalog search ended")

        res_objs = ["\n\n AFFECTED OBJS \n"]

        log.info("TOTAL affected: %d objects", len(brains))
        total = len(brains)
        count = 0
        count_progress = 0

        log.info("Starting Sparql refresh for %d objects", total)
        not_found = []
        for brain in brains:
            count_progress += 1
            brain_url = brain.getURL()
            log.info("%s/%s :: Current brain %s", count_progress, total,
                     brain_url)
            try:
                obj = brain.getObject()
            except Exception:
                not_found.append("%s \n" % brain_url)
                log.info("### SKIPPED not found")
                continue
            # no need to change Once or Weekly sparql objects
            if obj.refresh_rate in ['Once', 'Weekly']:
                continue
            obj.setRefresh_rate('Weekly')
            count += 1
            if count % 50 == 0:
                transaction.savepoint(optimistic=True)

        count_message = "\n MODIFIED OBJECTS TOTAL: %d" % count

        log.info("DONE Sparql refresh fix for %d objects", count)
        res_objs_msg = " ".join(res_objs)
        not_found_msg = " ".join(not_found)
        return "%s %s %s " % (count_message, res_objs_msg, not_found_msg)


class RemoveAcquireFlagForNewWorkflowState(object):
    """ Remove acquire flag for new workflow state
    """
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        """ Call method
        """
        log = logging.getLogger("New state permisssion removal")
        log.info("*** New state permisssion removal")
        catalog = getToolByName(self.context, 'portal_catalog')

        log.info("*** Catalog search start")
        brains = catalog(review_state="new",
                         Language="all",
                         show_inactive=True)
        log.info("*** Catalog search ended")

        res_objs = ["\n\n AFFECTED OBJS \n"]
        skipped_objs = ["\n\n SKIPPED OBJS \n"]

        log.info("TOTAL affected: %d objects", len(brains))
        total = len(brains)
        count = 0
        count_progress = 0

        log.info("Starting new state refresh for %d objects", total)
        not_found = []
        for brain in brains:
            count_progress += 1
            brain_url = brain.getURL()
            log.info("%s/%s :: Current brain %s", count_progress, total,
                     brain_url)
            try:
                obj = brain.getObject()
                obj_id = obj.id
                if '.pdf' in brain_url or '.epub' in brain_url:
                    parent = obj.aq_parent
                    if parent.id == obj_id.split('.')[0]:
                        skipped_objs.append(brain_url)

                view_permissions = obj.rolesOfPermission("View")
                view_roles = [i['name'] for i in view_permissions if
                              i['selected'] == 'SELECTED']
                access_permissions = obj.rolesOfPermission(
                    "Access contents information")
                access_roles = [i['name'] for i in access_permissions if
                              i['selected'] == 'SELECTED']
                obj.manage_permission(AccessContentsInformation,
                                      access_roles, acquire=0)
                obj.manage_permission(View, view_roles, acquire=0)
                obj.reindexObjectSecurity()
                res_objs.append(obj.absolute_url())
            except Exception:
                not_found.append("%s \n" % brain_url)
                log.info("### SKIPPED not found")
                continue

            count += 1
            if count % 50 == 0:
                transaction.savepoint(optimistic=True)

        count_message = "\n MODIFIED OBJECTS TOTAL: %d" % count

        log.info("DONE new state refresh fix for %d objects", count)
        res_objs_msg = "\n".join(res_objs)
        not_found_msg = "\n".join(not_found)
        skipped_objs_msg = "\n".join(skipped_objs)
        return "%s %s %s %s" % (count_message, res_objs_msg, not_found_msg,
                                skipped_objs_msg)


class ReplaceDataVersionId(object):
    """ 72521 restore previous versionId for given data files
    """
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        """ Call method
        """
        if not has_versions:
            return "Versions not found, exiting"
        log = logging.getLogger("Data version migration")
        log.info("*** Starting Data version migration")
        res_objs = ["\n\n AFFECTED OBJS \n"]
        brains = data_versions()
        log.info("TOTAL affected: %d objects", 450)
        total = len(brains)
        count = 0
        count_progress = 0

        log.info("Starting data version migration for %d objects", total)
        not_found = []
        for brain in brains:
            count_progress += 1
            obj = self.context.get(brain[0])
            if not obj:
                not_found.append(brain[0])
                continue
            IVersionControl(obj).setVersionId(brain[1])
            obj.reindexObject(idxs=['getVersionId'])
            obj_url = obj.absolute_url(1)
            log.info('Migrated --> %s', obj_url)
            res_objs.append(url)
            count += 1
            if count % 50 == 0:
                transaction.savepoint(optimistic=True)

        count_message = "\n MODIFIED OBJECTS TOTAL: %d" % count

        log.info("DONE data version migration %d objects", count)
        res_objs_msg = "\n".join(res_objs)
        not_found_msg = "\n".join(not_found)
        return "Count: %s \nResults: %s \nNotFound: %s " % (count_message,
                                                            res_objs_msg,
                                                            not_found_msg)


class ReplaceWrongCreationDate(object):
    """ 73422 restore previous creation date for given objects
    """
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        """ Call method
        """
        log = logging.getLogger("Creation date migration")
        log.info("*** Starting Creation date migration")
        res_objs = ["\n\n AFFECTED OBJS \n"]
        brains = urls_for_73422()
        total = len(brains)
        log.info("TOTAL affected: %d objects", total)
        count = 0
        count_progress = 0

        mt = getToolByName(self.context, 'portal_membership', None)
        wf = getToolByName(self.context, "portal_workflow", None)
        pr = getToolByName(self.context, 'portal_repository', None)
        actor = mt.getAuthenticatedMember().id
        log.info("Starting data version migration for %d objects", total)
        not_found = []
        type_workflow = {}
        for brain in brains:
            count_progress += 1
            obj = self.context.restrictedTraverse(brain, None)
            if not obj:
                not_found.append(brain)
                continue
            obj_url = obj.absolute_url(1)

            previous_creation_date = obj.created()

            history = obj.workflow_history  # persistent mapping
            review_state = wf.getInfoFor(obj, 'review_state', 'None')
            ptype = obj.portal_type
            if not type_workflow.get(ptype):
                type_workflow[ptype] = wf.getWorkflowsFor(obj)[0].id
            for name, wf_entries in history.items():
                if type_workflow.get(ptype, '') == name:
                    wf_entries = list(wf_entries)
                    for e in reversed(wf_entries):
                        cmt = e.get('comments')
                        if '73422' in cmt:
                            mdate = cmt.split('from ')[1].split(' to')[0]
                            comment = "Restore creation date migration " \
                                      " (issue 73422). Changed creation date" \
                                      " from %s to --> %s." % (
                                          previous_creation_date,
                                          mdate)
                            obj.setCreationDate(mdate)
                            wf_entries.append({'action': 'Edited',
                                               'review_state': review_state,
                                               'comments': comment,
                                               'actor': actor,
                                               'time': DateTime()})
                            history[name] = tuple(wf_entries)
                            pr.save(obj=obj, comment=comment)
                            obj.reindexObject(idxs=['created'])
                            msg = '%d %s to %s for --> %s' % (count,
                                  previous_creation_date, mdate, obj_url)
                            log.info(msg)
                            res_objs.append(msg)
                            count += 1
                            if count % 50 == 0:
                                transaction.commit()

        count_message = "\n MODIFIED OBJECTS TOTAL: %d" % count

        log.info("DONE data version migration %d objects", count)
        res_objs_msg = "\n".join(res_objs)
        not_found_msg = "\n".join(not_found)
        return "Count: %s \nResults: %s \nNotFound: %s " % (count_message,
                                                            res_objs_msg,
                                                            not_found_msg)


class SetEmptyFLVOnMediaFiles(object):
    """ Set placeholder flv for IMedia files with missing files
    """
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        """ Call method
        """
        log = logging.getLogger("IMedia without files")
        log.info("*** Starting fix for IMedia without files")
        catalog = getToolByName(self.context, 'portal_catalog')

        log.info("*** Catalog search start")
        brains = catalog(Language="all",
                         portal_type="File",
                         object_provides='eea.mediacentre.interfaces.IVideo',
                         show_inactive=True)
        log.info("*** Catalog search ended")

        res_objs = ["\n\n AFFECTED OBJS \n"]

        log.info("TOTAL affected: %d objects", len(brains))
        total = len(brains)
        count = 0
        count_progress = 0

        log.info("Starting IMedia file fix for %d objects", total)
        not_found = []
        path = os.path.join(os.path.dirname(__file__), "data", "empty.flv")
        for brain in brains:
            count_progress += 1
            brain_url = brain.getURL()
            try:
                obj = brain.getObject()
            except Exception:
                not_found.append("%s \n" % brain_url)
                log.info("### SKIPPED not found")
                continue
            if obj.getFilename() != "empty.flv":
                continue
            afile = open(path, "r")
            obj.setFile(afile)
            afile.close()
            obj.reindexObject()
            log.info("%s/%s :: Set empty.flv for %s", count_progress, total,
                     brain_url)
            res_objs.append("\n %s" % brain_url)
            count += 1
            if count % 50 == 0:
                transaction.commit()

        count_message = "\n MODIFIED OBJECTS TOTAL: %d" % count

        log.info("DONE media file fix for %d objects", count)
        res_objs_msg = " ".join(res_objs)
        not_found_msg = " ".join(not_found)
        return "%s %s %s " % (count_message, res_objs_msg, not_found_msg)


class SynchronizeThemes(BrowserView):
    """ Synchronize older versions themes with the latest one
    """
    def __init__(self, context, request):
        super(SynchronizeThemes, self).__init__(context, request)
        self.ignore_types = ['Report']
        self.ignore_themes = ['technology']
        self.ignore_states = ['marked_for_deletion']

    def __call__(self, dry_run=True, **kwargs):
        dry_run = dry_run in (0, False, "0", "False", "no")

        ctool = getToolByName(self.context, 'portal_catalog')
        versions = ctool.Indexes.get('getVersionId').uniqueValues()
        logs = []
        logger.info("Synchronizing older versions themes: dry_run=%s", dry_run)
        for idx, version in enumerate(versions):
            brains = ctool(getVersionId=version)
            if len(brains) < 2:
                continue

            try:
                brains = sorted(brains, reverse=1, key=lambda b: max(
                    b.effective.asdatetime(), b.created.asdatetime()))
            except Exception as err:
                logger.warn("Can't fix version id: %s", version)
                logger.exception(err)
                continue

            themes = None
            state = None
            if (idx + 1) % 500 == 0:
                logger.info("\n\nProcessed version ids %s\n\n", idx)
                if not dry_run:
                    transaction.commit()

            for brain in brains:
                try:
                    old_themes = brain.getThemes
                    old_state = brain.review_state
                    old_type = brain.portal_type
                    old_url = brain.getURL()
                except Exception as err:
                    logger.exception(err)
                    continue

                # Skip some revisions
                if old_state in self.ignore_states:
                    continue

                # Skip some types
                if old_type in self.ignore_types:
                    continue

                # Latest version
                if not state:
                    state = old_state

                if not themes:
                    themes = old_themes
                    continue

                if sorted(themes) != sorted(old_themes):
                    msg = (
                        "Updating older version:\n"
                        "%s\t"
                        "%s\t"
                        "themes from\t"
                        "%s\tto\t%s\t"
                        "revision\t"
                        "%s\tto\t%s\t" % (
                        old_type, old_url,
                        old_themes, themes,
                        old_state, state)
                    )

                    logs.append(msg)
                    logger.warn(msg)
                    if dry_run:
                        continue

                    try:
                        doc = brain.getObject()
                        IThemeTagging(doc).tags = themes
                        doc.reindexObject(idxs=["getThemes"])
                    except Exception as err:
                        logger.exception(err)

        return "\n".join(logs)
