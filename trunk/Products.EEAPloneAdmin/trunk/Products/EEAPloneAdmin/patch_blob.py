""" Blob patch
"""

from Products.CMFCore.utils import getToolByName
from ZODB.POSException import POSKeyError
from ZODB.utils import oid_repr
from os import fstat
from plone.app.blob.utils import getImageSize, openBlob
from plone.app.imaging.interfaces import IImageScaleHandler
import binascii
import logging
import os
import os.path

logger = logging.getLogger("Products.EEAPloneAdmin")


def patched_field_get_size(self):
    try:
        blob = openBlob(self.blob)
        size = fstat(blob.fileno()).st_size
        blob.close()
    except POSKeyError:
        oid = self.blob._p_oid

        directories = []
        # Create the bushy directory structure with the least significant byte
        # first
        for byte in str(oid):
            directories.append('0x%s' % binascii.hexlify(byte))
        path = os.path.sep.join(directories)
        cached = self.blob._p_blob_committed

        logger.error("BLOBWARNING: Could not get "
                       "field size for blob %r. Info about blob: "
                       "OID (oid, repr, path on zeo storage): %r > %r > %r "
                       "CACHED (path to cached blob): %r "
                        % (self, oid_repr(oid), oid.__repr__(), path, cached))
        size = 0
    return size


def patched_class_get_size(self):
    f = self.getPrimaryField()
    if f is None:
        return 0
    try:
        return f.get_size(self) or 0
    except POSKeyError:
        logger.error("BLOBWARNING: Error when doing get_size "
                       "for field %r for %r" % (f, self))
        return 0


def patched_field_index_html(self, instance, REQUEST=None,
                           RESPONSE=None, disposition='inline'):
    try:
        blob = self._old_index_html(instance, REQUEST=REQUEST,
                            RESPONSE=RESPONSE, disposition=disposition)
        if blob:
            return blob
        raise POSKeyError()
    except POSKeyError:
        logger.error("BLOBWARNING: Error when doing index_html "
           "for field %r for %r with request %r" % (self, instance, REQUEST))
        if not RESPONSE:
            RESPONSE = instance.REQUEST.RESPONSE
        putils = getToolByName(instance, 'plone_utils')
        putils.addPortalMessage('Missing BLOB file for %r' %
                            instance.absolute_url_path(), type='error')
        RESPONSE.redirect(instance.absolute_url()+'/view')


def patched_getScale(self, instance, scale=None, **kwargs):
    if scale is None:
        return self.getUnwrapped(instance, **kwargs)
    handler = IImageScaleHandler(self, None)
    if handler is not None:
        try:
            return handler.getScale(instance, scale)
        except POSKeyError:
            logger.error("BLOBWARNING: Could not get "
                           "scale %r for %r" % (scale, instance))
    return None


def patched_getSize(self):
    """ return image dimensions of the blob """
    # TODO: this should probably be cached...
    try:
        blob = openBlob(self.blob)
    except POSKeyError:

        oid = self.blob._p_oid

        directories = []
        # Create the bushy directory structure with the least significant byte
        # first
        for byte in str(oid):
            directories.append('0x%s' % binascii.hexlify(byte))
        path = os.path.sep.join(directories)
        cached = self.blob._p_blob_committed

        logger.error("BLOBWARNING: Could not get "
                       "image size for blob %r. Info about blob: "
                       "OID (oid, repr, path on zeo storage): %r > %r > %r "
                       "CACHED (path to cached blob): %r "
                        % (self, self.blob._p_oid, oid_repr(oid),
                           oid.__repr__(), path, cached))

        return 0

    size = getImageSize(blob)
    blob.close()
    return size

# vim: set sw=4 ts=4 ai et:

