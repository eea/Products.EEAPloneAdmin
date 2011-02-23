#
# Unit Tests for the style install and uninstall methods
#

import os, sys

from PloneAdminTestCase import EEAPloneAdminTestCase
from Products.CMFCore.utils import getToolByName
from Products.EEAPloneAdmin.config import EEA_LANGUAGES
from Products.EEAPloneAdmin.exportimport.localsite import translateFromSite

from eea.translations import _
from zope.i18n import translate
    


from Products.EEAPloneAdmin.config import *
PROJECTNAME = 'EEAPloneAdmin'

class testLocalSite(EEAPloneAdminTestCase):

    def afterSetUp(self):
        self.setRoles(['Manager'])
        self.portal.portal_languages.manage_setLanguageSettings('en', EEA_LANGUAGES)

        # create production structure that we need
        self.site = getattr(self.portal, 'SITE')

        for path, portalType, msgId in translateFromSite:
            paths = path.split('/')
            folder = self.site
            if len(paths) > 1:
                for p in paths[:-1]:
                    folder = getattr(folder, p)
            folder.invokeFactory(portalType, id=paths[-1])
            

        setup_tool = getToolByName(self.portal, 'portal_setup')
        setup_tool.setImportContext('profile-EEAPloneAdmin:local-site')
        setup_tool.runAllImportSteps()

    def testLocalSitePortalUrl(self):
        site = self.site
        
        plone = site.unrestrictedTraverse('@@plone')
        plone._initializeData()
        portal_url = self.portal.absolute_url()
        self.failUnless(plone._data['local_site'] == portal_url)
        siteLangView = site.unrestrictedTraverse('@@translatedSitesLanguages')
        languages = [ langcode for langcode, lang in siteLangView()
                                 if langcode != 'en' ]
        for lang in languages:
            local = getattr(site, lang)
            plone = local.unrestrictedTraverse('@@plone')
            plone._initializeData()
            localUrl = '%s/%s' % (portal_url, lang)
            self.failUnless(plone._data['local_site'] == localUrl, plone._data['local_site'])

    def testLocalSitesCreated(self):

        site = self.site
        navman = site.portal_navigationmanager
        
        siteLangView = site.unrestrictedTraverse('@@translatedSitesLanguages')
        languages = [ langcode for langcode, lang in siteLangView() ]

        title = _(u'European Environment Agency')

        for lang in languages:
            if lang == 'en':
                continue
            
            self.failUnless(hasattr(site, lang))
            localSite = site[lang]
            self.failUnless(localSite.Title() == translate(title, target_language=lang).encode('utf8'))
            self.failUnless(hasattr(localSite, 'introduction'), lang)
            self.failUnless(localSite.getDefaultPage() == 'introduction', lang)
            self.failUnless(hasattr(localSite, 'reports'), lang)
            self.failUnless(hasattr(localSite, 'reports-rss'), lang)            
            self.failUnless(hasattr(localSite, 'pressroom'), lang)

            for path, portalType, msgId in translateFromSite:
                paths = path.split('/')
                folder = localSite
                for p in paths:
                    self.failUnless(hasattr(folder, p), lang)
                    folder = getattr(folder, p)
                      
            self.failUnless(hasattr(navman, 'local-%s' % lang), lang)
            
import unittest
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(testLocalSite))
    return suite
