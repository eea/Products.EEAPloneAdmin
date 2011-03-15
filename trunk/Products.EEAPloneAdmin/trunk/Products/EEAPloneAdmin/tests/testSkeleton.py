#
# This file is a skeleton test suite.
# It is here for letting you add new tests to the product without having to
# modify the existing testStyleInstallation.py module.
# You may modify its name to something that describes what it tests
# (keeping its 'test' prefix).
#

from Products.PloneTestCase import PloneTestCase

PloneTestCase.installProduct('EEAPloneAdmin')
PloneTestCase.setupPloneSite(products=['EEAPloneAdmin'])


class TestSomething(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        pass

    def testSomething(self):
        # Test something
        self.assertEqual(1+1, 2)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestSomething))
    return suite

