#
# Base TestCase for EEAPloneAdmin
#

from Testing import ZopeTestCase
from Products.PloneTestCase import PloneTestCase
from Products.EEAPloneAdmin.config import DEPENDENCIES

from Products.PloneTestCase.layer import onsetup
from Products.Five import zcml
from Products.Five import fiveconfigure

PRODUCTS = ['FiveSite', 'ATVocabularyManager', 'EEAPloneAdmin', 
            'EEAContentTypes', 'PloneLanguageTool']
PRODUCTS += DEPENDENCIES

@onsetup
def setup_eeaploneadmin():
    fiveconfigure.debug_mode = True
    import Products.Five
    import Products.FiveSite
    zcml.load_config('meta.zcml', Products.Five)
    zcml.load_config('configure.zcml', Products.FiveSite)
    fiveconfigure.debug_mode = False

    PloneTestCase.installProduct('Five')
    PloneTestCase.installProduct('FiveSite')
    PloneTestCase.installProduct('ATVocabularyManager')
    for dependency in DEPENDENCIES:
        PloneTestCase.installProduct(dependency)
    PloneTestCase.installProduct('EEAPloneAdmin')

setup_eeaploneadmin()
PloneTestCase.setupPloneSite(products=PRODUCTS)

class EEAPloneAdminTestCase(PloneTestCase.PloneTestCase):
    """Base TestCase for EEAContentTypes."""

class EEAPloneAdminFunctionalTestCase(PloneTestCase.FunctionalTestCase):
    """ """
