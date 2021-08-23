"""
    plone.app.imaging traverse.py patches
"""

from logging import exception
from plone.protect.interfaces import IDisableCSRFProtection
from zope.globalrequest import getRequest
from Products.Archetypes.Field import HAS_PIL
from zope.interface import alsoProvides
from ZODB.POSException import ConflictError


def getScale(self, instance, scale):
    """ return scaled and aq-wrapped version for given image data """
    field = self.context
    image_type = field.getContentType(self.context)
    available = field.getAvailableSizes(instance)
    if scale in available or scale is None:
        image = self.retrieveScale(instance, scale=scale)
        if not image:  # create the scale if it doesn't exist
            width, height = available[scale]
            data = self.createScale(instance, scale, width, height)
            if data is not None:
                self.storeScale(instance, scale, **data)
                image = self.retrieveScale(instance, scale=scale)
        if image is not None and not isinstance(image, basestring):
            return image
    return None


def createScale(self, instance, scale, width, height, data=None):
    """ create & return a scaled version of the image as retrieved
        from the field or optionally given data """
    # disable CRSF on scale generation
    req = getRequest()
    if req:
        alsoProvides(req, IDisableCSRFProtection)
    field = self.context
    if HAS_PIL and width and height:
        if data is None:
            image = field.getRaw(instance)
            if not image:
                return None
            data = str(image.data)
        if data:
            id = field.getName() + '_' + scale
            try:
                imgdata, file_format = field.scale(data, width, height)
            except (ConflictError, KeyboardInterrupt):
                raise
            except Exception:
                if not field.swallowResizeExceptions:
                    raise
                else:
                    exception('could not scale ImageField "%s" of %s',
                              field.getName(), instance.absolute_url())
                    return None
            content_type = 'image/%s' % file_format.lower()
            filename = field.getFilename(instance)
            return dict(id=id, data=imgdata.getvalue(),
                        content_type=content_type, filename=filename)
    return None
