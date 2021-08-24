"""
    plone.app.imaging traverse.py patches
"""

from logging import exception
from plone.protect.interfaces import IDisableCSRFProtection
from zope.globalrequest import getRequest
from zope.annotation import IAnnotations
from zope.interface import alsoProvides
from ZODB.POSException import ConflictError
from Products.Archetypes.Field import HAS_PIL


def patched_getScale(self, instance, scale):
    """ return scaled and aq-wrapped version for given image data """
    field = self.context
    available = field.getAvailableSizes(instance)
    if scale in available or scale is None:
        image = self.retrieveScale(instance, scale=scale)
        if not image:  # create the scale if it doesn't exist
            width, height = available[scale]
            data = self.createScale(instance, scale, width, height)
            if data is not None:
                self.storeScale(instance, scale, **data)
                image = self.retrieveScale(instance, scale=scale)

        # retrieve scale width and height from annotation for image that has
        # missing info, this happens when we get the svg scale
        if image and not image.width:
            width, height = available[scale]
            annotations = IAnnotations(instance)
            scale_annotations = annotations.get('plone.scale')
            filename = image.getFilename()
            for value in scale_annotations.values():
                scale_key = value.get('key')
                scale_height = scale_key[1][1]
                scale_width = scale_key[2][1]
                if scale_height == height and scale_width == width and \
                        filename == value.get('filename'):
                    image.width = value.get('width')
                    image.height = value.get('height')
                    break
        if image is not None and not isinstance(image, basestring):
            return image
    return None


def data_as_func(obj):
    """ data as function decorator """
    def func():
        return obj.data
    return func


def patched_createScale(self, instance, scale, width, height, data=None):
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
                if 'svg' in field.getFilename(instance):
                    imgdata = instance.restrictedTraverse('@@images').scale(
                        field.getName(), scale, width=width, height=height)
                    imgdata.getvalue = data_as_func(imgdata)
                    file_format = 'svg+xml'
                else:
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
