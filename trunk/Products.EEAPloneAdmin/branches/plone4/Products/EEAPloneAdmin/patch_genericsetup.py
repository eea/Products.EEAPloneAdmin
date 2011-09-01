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
