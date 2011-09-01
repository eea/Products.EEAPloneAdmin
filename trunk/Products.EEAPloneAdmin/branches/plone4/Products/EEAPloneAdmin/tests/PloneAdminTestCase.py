""" Base TestCase for EEAPloneAdmin
"""

from Products.EEAPloneAdmin.config import DEPENDENCIES
from Products.PloneTestCase import PloneTestCase
from Products.PloneTestCase.layer import onsetup

from Products.Five import fiveconfigure
from Products.Five import zcml

#from Testing import ZopeTestCase

PRODUCTS = [
            'ATVocabularyManager',
            'EEAContentTypes',
            'EEAPloneAdmin',
            'valentine.linguaflow',
            ]

PRODUCTS = list(set(PRODUCTS).union(DEPENDENCIES))

PROFILES = [
        'valentine.linguaflow:default',
        ]

#PloneTestCase.installProduct('valentine.linguaflow')
#PloneTestCase.installPackage('valentine.linguaflow')

@onsetup
def setup_eeaploneadmin():
    """ Setup EEA Plone Admin
    """

    for dependency in DEPENDENCIES:
        PloneTestCase.installProduct(dependency)

    fiveconfigure.debug_mode = True
    #import Products.Five
    #import Products.FiveSite
    import valentine.linguaflow
    zcml.load_config('configure.zcml', valentine.linguaflow)
    fiveconfigure.debug_mode = False

    #zcml.load_config('configure.zcml', Products.FiveSite)
    #PloneTestCase.installProduct('Five')
    #PloneTestCase.installProduct('FiveSite')
    #PloneTestCase.installProduct('ATVocabularyManager')
    #PloneTestCase.installProduct('EEAPloneAdmin')

setup_eeaploneadmin()
PloneTestCase.setupPloneSite(products=PRODUCTS, extension_profiles=PROFILES)

class EEAPloneAdminTestCase(PloneTestCase.PloneTestCase):
    """ Base TestCase for EEAContentTypes
    """

class EEAPloneAdminFunctionalTestCase(PloneTestCase.FunctionalTestCase):
    """ Functional test case
    """
