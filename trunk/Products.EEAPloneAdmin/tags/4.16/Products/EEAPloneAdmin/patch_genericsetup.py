""" Monkey patches for GenericSetup
"""

def manage_deleteImportSteps(self, ids, request=None):
    """ Delete import steps
    """
    if request is None:
        request = self.REQUEST
    for registry_id in ids:
        self._import_registry.unregisterStep(registry_id)
    self._p_changed = True
    url = self.absolute_url()
    request.RESPONSE.redirect("%s/manage_stepRegistry" % url)

def manage_deleteExportSteps(self, ids, request=None):
    """ Delete export steps
    """
    if request is None:
        request = self.REQUEST
    for registry_id in ids:
        self._export_registry.unregisterStep(registry_id)
    self._p_changed = True
    url = self.absolute_url()
    request.RESPONSE.redirect("%s/manage_stepRegistry" % url)

import time
from StringIO import StringIO
from tarfile import TarFile
from Products.GenericSetup.context import BaseContext

def __patched_init__( self, tool, encoding=None ):

    BaseContext.__init__( self, tool, encoding )

    timestamp = time.gmtime()
    archive_name = ( 'setup_tool-%4d%02d%02d%02d%02d%02d.tar.gz'
                   % timestamp[:6] )

    self._archive_stream = StringIO()
    self._archive_filename = archive_name
    self._archive = TarFile.open( archive_name, 'w:tar'
                                , self._archive_stream )
