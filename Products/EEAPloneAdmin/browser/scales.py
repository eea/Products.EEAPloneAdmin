""" Utilities
"""
import logging
from Products.Five import BrowserView
logger = logging.getLogger('Products.EEAPloneAdmin')

class RecreateImageScales(BrowserView):
    """ Recreate image scales """

    def __call__(self):
        obj = self.context
        field = obj.getField('image')

        if field is not None:
            logger.info('INFO: updating scales for %s', obj.absolute_url())
            field.removeScales(obj)
            field.createScales(obj)
            msg = 'Done'
            logger.info(msg)
        else:
            msg = 'ERROR: no "image" field found for %s' % obj.absolute_url()
            logger.info(msg)

        return msg
