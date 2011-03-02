from StringIO import StringIO
from Products.CMFCore.utils import getToolByName
import transaction

def install(portal, reinstall=False):
    """ install and default configuration. """
    out = StringIO()

    setup_tool = getToolByName(portal, 'portal_setup')
    setup_tool.setImportContext('profile-EEAPloneAdmin:default')
    setup_tool.runAllImportSteps()
