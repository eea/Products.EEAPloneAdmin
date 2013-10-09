""" Monkey patch for collective.quickupload
"""
from zope import component
from collective.quickupload import logger
from Acquisition import aq_inner
from thread import allocate_lock
import transaction
from AccessControl import Unauthorized
from ZODB.POSException import ConflictError
from zope.event import notify
from zope.container.interfaces import INameChooser
from plone.i18n.normalizer.interfaces import IIDNormalizer
from Products.Archetypes.event import ObjectInitializedEvent
from Products.Archetypes.utils import shasattr

upload_lock = allocate_lock()


def QuickUploadCapableFileFactory__call__(self, name, title, description,
                                            content_type, data, portal_type):
    """ Patched __call__ for QuickUploadCapableFileFactory
    """
    context = aq_inner(self.context)
    charset = context.getCharset()
    filename = name
    name = name.decode(charset)
    error = ''
    result = {}
    result['success'] = None
    normalizer = component.getUtility(IIDNormalizer)
    chooser = INameChooser(self.context)

    # normalize all filename but dots
    normalized = ".".join([normalizer.normalize(n) for n in name.split('.')])
    newid = chooser.chooseName(normalized, context)

    # consolidation because it's different upon Plone versions
    newid = newid.replace('_','-').replace(' ','-').lower()
    if not title :
        # try to split filenames because we don't want
        # big titles without spaces
        title = name.split('.')[0].replace('_',' ').replace('-',' ')
    if newid in context.objectIds() :
        # only here for flashupload method since a check_id is done
        # in standard uploader - see also ZZZ in quick_upload.py
        raise NameError, 'Object id %s already exists' % newid
    else :
        upload_lock.acquire()
        try:
            transaction.begin()
            try:
                context.invokeFactory(type_name=portal_type, id=newid,
                                        title=title, description=description)
            except Unauthorized :
                error = u'serverErrorNoPermission'
            except ConflictError :
                # rare with xhr upload / happens sometimes with flashupload
                error = u'serverErrorZODBConflict'
            except Exception, e:
                error = u'serverError'
                logger.exception(e)

            if not error :
                obj = getattr(context, newid)
                if obj :
                    primaryField = obj.getPrimaryField()
                    if primaryField is not None:
                        mutator = primaryField.getMutator(obj)
                        # mimetype arg works with blob files
                        mutator(data, content_type=content_type,
                                mimetype=content_type)
                        # ZZZ when getting file through request.BODYFILE
                        # (XHR direct upload) the filename is not inside
                        # the file and the filename must be a string, not
                        # unicode otherwise Archetypes raise an error
                        # (so we use filename and not name)
                        if not obj.getFilename() :
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
                        notify(ObjectInitializedEvent(obj))
                    else :
                        # some products remove the 'primary' attribute on
                        # ATFile or ATImage (which is very bad)
                        error = u'serverError'
                        logger.info("An error happens : impossible to get"\
                            " the primary field for file %s, rawdata can't"\
                            " be created" %obj.absolute_url())
                else:
                    error = u'serverError'
                    logger.info("An error happens with setId from filename,"\
                        " the file has been created with a bad id, can't"\
                        " find %s" %newid)
            transaction.commit()
        finally:
            upload_lock.release()

    result['error'] = error
    if not error :
        result['success'] = obj
    return result
