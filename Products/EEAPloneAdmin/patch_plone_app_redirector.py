""" Patching plone.app.redirector to also redirect direct file download
    links (e.g. at_download/fileField) when the containing object 
    defines an alias
"""

def RedirectionStorage_get(self, old_path, default=None):
    """ Get alias
    """
    old_path = self._canonical(old_path)
    # Start patch
    if 'at_download' in old_path:
        at_split = old_path.split('at_download')
        parent_path = self._canonical(at_split[0])
        field_name = at_split[1][1:] # "/fieldName" -> "fieldName"
        new_path = self._paths.get(parent_path, default)
        if new_path != default:
            return '%s/at_download/%s' % (new_path, field_name)
    # End patch
    return self._paths.get(old_path, default)
