#
# Test methods used to make ...
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Products.EEAPloneAdmin.tests.PloneAdminTestCase import EEAPloneAdminTestCase
from Products.CMFPlone.tests import dummy

from Products.CMFPlone.utils import _createObjectByType

from Products.CMFPlone.URLTool import URLTool
from Products.CMFPlone.MembershipTool import MembershipTool
from Products.CMFPlone.GroupsTool import GroupsTool
from Products.CMFPlone.GroupDataTool import GroupDataTool
from Products.CMFPlone.ActionsTool import ActionsTool
from Products.CMFPlone.ActionIconsTool import ActionIconsTool

from Products.CMFCore.WorkflowTool import WorkflowTool

from Products.CMFPlone.InterfaceTool import InterfaceTool
from Products.CMFPlone.SyndicationTool import SyndicationTool

from Products.EEAPloneAdmin.browser.plone import PloneAdmin as Plone

class TestPloneView(EEAPloneAdminTestCase):
    """Tests the global plone view for functions we have overriden."""

    def afterSetUp(self):
        # We need to fiddle the request for zope 2.9+
        try:
            from zope.app.publication.browser import setDefaultSkin
            setDefaultSkin(self.app.REQUEST)
        except ImportError:
            # BBB: zope 2.8
            pass
        self.folder.invokeFactory('Document', 'test',
                                  title='Test default page')
        self.view = Plone(self.portal, self.app.REQUEST)
        self.view._initializeData()
        
    def testObjectTitle(self):
        self.setRoles(('Manager',))
        self.failUnless(self.view._data['browser_title'] == 'EEA')
        self.portal.invokeFactory('Folder', id='f1')
        f1 = self.portal.f1
        f1.invokeFactory('Folder', id='f2')
        view = Plone(f1, self.app.REQUEST)
        view._initializeData()
        self.failUnless(view._data['browser_title'] == 'f1')


        f2 = self.portal.f1.f2
        f2.invokeFactory('Folder', id='f3')
        view = Plone(f2, self.app.REQUEST)
        view._initializeData()
        self.failUnless(view._data['browser_title'] == 'f2 - f1')

        f3 = self.portal.f1.f2.f3
        f3.invokeFactory('Folder', id='f4')
        view = Plone(f3, self.app.REQUEST)
        view._initializeData()
        self.failUnless(view._data['browser_title'] == 'f3 - f2')

        f4 = self.portal.f1.f2.f3.f4
        view = Plone(f4, self.app.REQUEST)
        view._initializeData()
        self.failUnless(view._data['browser_title'] == 'f4 - f3')

        f1.invokeFactory('Folder', id='lang', title=u'Svenska едц')
        lang = self.portal.f1.lang
        lang.invokeFactory('Document', id='doc', title=u'Svenska едц')
        view = Plone(lang.doc, self.app.REQUEST)
        view._initializeData()
        self.failUnless(view._data['browser_title'].decode('utf8') == u'Svenska едц - f1', view._data['browser_title'])



def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestPloneView))
    return suite

if __name__ == '__main__':
    framework()
