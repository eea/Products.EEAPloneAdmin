# -*- coding: utf-8 -*-
""" Test workflow events
"""

from Products.EEAPloneAdmin.tests.PloneAdminTestCase import (
    EEAPloneAdminTestCase,
)
from unittest import TestSuite, makeSuite
import logging

logger = logging.getLogger("Products.EEAPloneAdmin.tests.testWorkflows")

class TestWorkflowEvents(EEAPloneAdminTestCase):
    """ Tests the workflow events triggers
    """

    def afterSetUp(self):
        """ After setup
        """

        self.workflow = self.portal.portal_workflow
        self.portal.acl_users._doAddUser('manager', 'secret', ['Manager'], [])
        self.setRoles('Manager')

        if not hasattr(self.folder, 'sandbox'):
            self.folder.invokeFactory('Folder', 'sandbox')

        self.sandbox = self.folder['sandbox']
        self.sandbox.invokeFactory('Document', 'test1')
        self.sandbox.invokeFactory('Document', 'test2')
        self.sandbox.invokeFactory('Document', 'test3')

    def test_retracted_publishing_date(self):
        """ Test effective date of retracted objects that should be
            the same date found when objects were not published
        """
        # Before state change modification dates
        objects = self.sandbox.objectValues()
        before = [doc.effective() for doc in objects]
        for doc in objects:
            self.workflow.doActionFor(doc, 'publish')
            self.workflow.doActionFor(doc, 'retract')
        after = [doc.effective() for doc in objects]
        self.failIf(before != after, "Objs shouldn't have any effective date")

    def test_copied_objects_publishing_date(self):
        """ Test that copied objects do not maintain the effective date
            set on the original objects
        """
        # Before state change modification dates
        objects = self.sandbox.objectValues()
        for doc in objects:
            self.workflow.doActionFor(doc, 'publish')
            doc.object_copy()
            doc.object_paste()

        objects = self.sandbox.objectValues()
        results = [obj for obj in objects if "copy" in obj.id]
        copies_effective_date = [doc.effective_date for doc in results]
        effective_dates = False
        for dtime in copies_effective_date:
            if dtime:
                effective_dates = True
                break
        self.failIf(effective_dates,
                    "Objs copied shouldn't have any effective date")


def test_suite():
    """ Test suite
    """
    suite = TestSuite()
    suite.addTest(makeSuite(TestWorkflowEvents))
    return suite
