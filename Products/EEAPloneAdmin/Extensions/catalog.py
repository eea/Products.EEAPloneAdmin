""" Helper methods to debug and fix catalog
"""
import logging
logger = logging.getLogger('EEAPloneAdmin')


#
# Start a debugger on your catalog
#
def debug(self):
    """ Debug """
    import pdb; pdb.set_trace()
    return 'Done'


def cleanup_key(self, key):
    """ Unindex orphan key from catalog indexes """
    if not isinstance(key, int):
        key = int(key)

    path = self._catalog.paths.get(key)
    if path:
        return "Can't remove valid key {key} path {path}".format(
            key=key, path=path)

    data = self._catalog.data.get(key)
    if data:
        return "Can't remove valid key {key} path {data}".format(
            key=key, data=data)

    uid = [(k, v) for k, v in self._catalog.uids.iteritems() if v == key]
    if uid:
        return "Can't remove valid key {key} path {uid}".format(
            key=key, uid=uid)

    path = '/www/dummy-cleanup-brain'
    self._catalog.paths[key] = path
    self._catalog.uids[path] = key
    self._catalog.data[key] = ()
    self._catalog._length.change(1)
    self._catalog.uncatalogObject(path)
    return "Removed key {key}".format(key=key)
