""" Blob patch
"""
import binascii
import logging

import os
import os.path
from os import fstat
from cgi import escape

from Products.CMFCore.utils import getToolByName
from ZODB.POSException import POSKeyError
from ZODB.utils import oid_repr
from plone.app.blob.utils import getImageSize, openBlob
from plone.app.imaging.interfaces import IImageScaleHandler

logger = logging.getLogger("Products.EEAPloneAdmin")


def patched_field_get_size(self):
    """ Patch for get_size
    """
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
                       "CACHED (path to cached blob): %r ",
                        self, oid_repr(oid), oid.__repr__(), path, cached)
        size = 0
    return size

def patched_class_get_size(self):
    """ Patch for get_size
    """
    f = self.getPrimaryField()
    if f is None:
        return 0
    try:
        return f.get_size(self) or 0
    except POSKeyError:
        logger.error("BLOBWARNING: Error when doing get_size "
                     "for field %r for %r", f, self)
        return 0

def patched_field_index_html(self, instance, REQUEST=None,
                           RESPONSE=None, disposition='inline'):
    """ Patch for index_html for field
    """
    try:
        blob = self._old_index_html(instance, REQUEST=REQUEST,
                            RESPONSE=RESPONSE, disposition=disposition)
        if blob:
            return blob
        raise POSKeyError()
    except POSKeyError:
        logger.warning("BLOBWARNING: When doing index_html "
           "for field %r for %r with request %r return an empty file", self,
            instance, REQUEST)
        if not RESPONSE:
            RESPONSE = instance.REQUEST.RESPONSE
        putils = getToolByName(instance, 'plone_utils')
        putils.addPortalMessage('Discovered an empty BLOB file for %r' %
                            instance.absolute_url_path(), type='warning')
        RESPONSE.redirect(instance.absolute_url()+'/view')

def patched_getScale(self, instance, scale=None, **kwargs):
    """ Patch for getScale
    """
    if scale is None:
        return self.getUnwrapped(instance, **kwargs)
    handler = IImageScaleHandler(self, None)
    if handler is not None:
        try:
            return handler.getScale(instance, scale)
        except POSKeyError:
            logger.error("BLOBWARNING: Could not get "
                           "scale %r for %r", scale, instance)
    return None

def patched_getSize(self):
    """ Return image dimensions of the blob
    """
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
                     "CACHED (path to cached blob): %r ",
                     self.blob._p_oid, oid_repr(oid),
                     oid.__repr__(), path, cached)

        return 0

    size = getImageSize(blob)
    blob.close()
    return size


def patched_tag(self, instance, scale=None, height=None, width=None, alt=None,
            css_class=None, title=None, **kwargs):
        """ Create a tag including scale
        """
        image = self.getScale(instance, scale=scale)
        if image:
            try:
                size = self.getSize(instance, scale=scale)
                if isinstance(size, int):
                    raise POSKeyError
                if len(size) < 2:
                    raise POSKeyError

                img_width, img_height = self.getSize(instance, scale=scale)
            except POSKeyError:
                RESPONSE = instance.REQUEST.RESPONSE
                message_path = instance.absolute_url_path() + '/' \
                    + instance.REQUEST.steps[-1]
                putils = getToolByName(instance, 'plone_utils')
                putils.addPortalMessage('Discovered an empty BLOB file for %r' %
                                    message_path, type='warning')
                img_height = 0
                img_width = 0
                RESPONSE.redirect(instance.absolute_url()+'/view')
        else:
            img_height = 0
            img_width = 0

        if height is None:
            height = img_height
        if width is None:
            width = img_width

        url = instance.absolute_url()
        if scale:
            url += '/' + self.getScaleName(scale)
        else:
            url += '/' + self.getName()

        if alt is None:
            alt = instance.Title()
        if title is None:
            title = instance.Title()

        values = {'src': url,
                  'alt': escape(alt, quote=True),
                  'title': escape(title, quote=True),
                  'height': height,
                  'width': width,
                 }

        result = '<img src="%(src)s" alt="%(alt)s" title="%(title)s" '\
                 'height="%(height)s" width="%(width)s"' % values

        if css_class is not None:
            result = '%s class="%s"' % (result, css_class)

        for key, value in kwargs.items():
            if value:
                result = '%s %s="%s"' % (result, key, value)

        return '%s />' % result