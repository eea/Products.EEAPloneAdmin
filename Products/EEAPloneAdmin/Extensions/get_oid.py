""" Get OID
"""
from ZODB.utils import oid_repr
import os
import binascii

def get_oid(self):
    """get oid"""
    field = self.getField('image')
    blob = field.getRaw(self).getBlob()
    oid = blob._p_oid

    directories = []
    # Create the bushy directory structure with the least significant byte
    # first
    for byte in str(oid):
        directories.append('0x%s' % binascii.hexlify(byte))
    path = os.path.sep.join(directories)

    cached = blob._p_blob_committed
    return """<html><body>
    oid (oid, repr, path on zeo storage): %s > %s > %s <br/>
    cached (path to cached blob): %s <br/>
    </body></html>
    """ % (oid_repr(oid), oid.__repr__(), path, cached)

