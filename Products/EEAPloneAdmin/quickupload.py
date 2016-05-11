""" Quick Upload
"""
from zope.interface import implements

from Products.Archetypes.interfaces import IBaseObject
from Products.Archetypes.utils import shasattr
from collective.quickupload import logger
from collective.quickupload.interfaces import IQuickUploadFileSetter
from zope.component import adapts


class ArchetypesFileSetter(object):
    """ File Setter
    """
    implements(IQuickUploadFileSetter)
    adapts(IBaseObject)

    def __init__(self, context):
        self.context = context

    def set(self, data, filename, content_type):
        """ Set
        """
        error = ''
        obj = self.context
        primaryField = obj.getPrimaryField()
        if primaryField is not None:
            mutator = primaryField.getMutator(obj)
            # mimetype arg works with blob files
            mutator(data, content_type=content_type, mimetype=content_type)
            if not obj.getFilename():
                obj.setFilename(filename)
                #patch:
                #check if setFilename worked,
                # if not we set the filename on the blob
                if not obj.getFilename():
                    field = obj.getPrimaryField()
                    if field:
                        blob = field.getUnwrapped(obj)
                        if blob is not None:
                            if shasattr(blob, 'setFilename'):
                                blob.setFilename(filename)
                #end of patch
            obj.reindexObject()
        else:
            # some products remove the 'primary' attribute
            # on ATFile or ATImage (which is very bad)
            error = 'serverError'
            logger.info("An error happens : impossible to get the primary field"
                        " for file %s, rawdata can't be created",
                        obj.absolute_url())

        return error
