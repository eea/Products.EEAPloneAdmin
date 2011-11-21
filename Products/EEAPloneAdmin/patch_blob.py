""" Blob patch
"""
from plone.app.blob.utils import getImageSize, openBlob
from ZODB.POSException import POSKeyError

def patched_getSize(self):
    """ return image dimensions of the blob """
    # TODO: this should probably be cached...
    try:
        blob = openBlob(self.blob)
    except POSKeyError:
        return 0
    size = getImageSize(blob)
    blob.close()
    return size
