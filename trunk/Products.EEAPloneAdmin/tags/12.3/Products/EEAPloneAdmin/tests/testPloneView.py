# -*- coding: utf-8 -*-
""" Test PloneView
"""

from Products.EEAPloneAdmin.browser.ploneview import ContextState
from Products.EEAPloneAdmin.tests.PloneAdminTestCase import (
    EEAPloneAdminTestCase,
)
from unittest import TestSuite, makeSuite
import logging

logger = logging.getLogger("Products.EEAPloneAdmin.tests.TestPloneView")

class TestPloneView(EEAPloneAdminTestCase):
    """ Tests the global plone view for functions we have overriden
    """

    def afterSetUp(self):
        """ After setup
        """
        self.folder.invokeFactory('Document', 'test',
                                  title='Test default page')

    def testObjectTitle(self):
        """ Test object title
        """
        view = ContextState(self.portal, self.app.REQUEST)

        self.setRoles(('Manager',))
        self.failUnless(view.browser_title() == 'EEA')
        self.portal.invokeFactory('Folder', id='f1')
        f1 = self.portal.f1
        f1.invokeFactory('Folder', id='f2')
        view = ContextState(f1, self.app.REQUEST)
        self.failUnless(view.browser_title() == 'f1')

        f2 = self.portal.f1.f2
        f2.invokeFactory('Folder', id='f3')
        view = ContextState(f2, self.app.REQUEST)
        self.failUnless(view.browser_title() == 'f2 - f1')

        f3 = self.portal.f1.f2.f3
        f3.invokeFactory('Folder', id='f4')
        view = ContextState(f3, self.app.REQUEST)
        self.failUnless(view.browser_title() == 'f3 - f2')

        f4 = self.portal.f1.f2.f3.f4
        view = ContextState(f4, self.app.REQUEST)
        self.failUnless(view.browser_title() == 'f4 - f3')

        f1.invokeFactory('Folder', id='lang', title=u'Svenska åäö')
        lang = self.portal.f1.lang
        lang.invokeFactory('Document', id='doc', title=u'Svenska åäö')
        view = ContextState(lang.doc, self.app.REQUEST)
        self.failUnless(
            view.browser_title().decode('utf8') == u'Svenska åäö - f1',
            view.browser_title())

def test_suite():
    """ Test suite
    """
    suite = TestSuite()
    suite.addTest(makeSuite(TestPloneView))
    return suite
