""" Monkey patch for collective.quickupload
"""
import json
import urllib
import mimetypes
from collective.quickupload import logger
from collective.quickupload.browser.quick_upload import getDataFromAllRequests
from collective.quickupload.browser.interfaces import IQuickUploadFileFactory
from Products.CMFCore.utils import getToolByName
from Acquisition import aq_inner

from thread import allocate_lock

import transaction
from AccessControl import Unauthorized
from ZODB.POSException import ConflictError
from zope import component
from zope.event import notify
from zope.app.container.interfaces import INameChooser

from plone.i18n.normalizer.interfaces import IIDNormalizer
from Products.Archetypes.event import ObjectInitializedEvent

from Products.Archetypes.utils import shasattr

upload_lock = allocate_lock()

def quick_upload_file(self):
    """ Quick upload
    """
    context = aq_inner(self.context)
    request = self.request
    response = request.RESPONSE

    response.setHeader('Expires', 'Sat, 1 Jan 2000 00:00:00 GMT')
    response.setHeader('Cache-control', 'no-cache')
    # the good content type woul be text/json or text/plain but IE
    # do not support it
    response.setHeader('Content-Type', 'text/html; charset=utf-8')

    if request.HTTP_X_REQUESTED_WITH :
        # using ajax upload
        file_name = urllib.unquote(request.HTTP_X_FILE_NAME)
        upload_with = "XHR"
        try :
            ofile = request.BODYFILE
            file_data = ofile.read()
            ofile.seek(0)
        except AttributeError :
            # in case of cancel during xhr upload
            logger.info("Upload of %s has been aborted", file_name)
            # not really useful here since the upload block
            # is removed by "cancel" action, but
            # could be useful if someone change the js behavior
            return  json.dumps({u'error': u'emptyError'})
        except :
            logger.info(
                "Error when trying to read the file %s in request", file_name)
            return json.dumps({u'error': u'serverError'})
    else :
        # using classic form post method (MSIE<=8)
        file_data = request.get("qqfile", None)
        filename = getattr(file_data, 'filename', '')
        file_name = filename.split("\\")[-1]
        upload_with = "CLASSIC FORM POST"
        # we must test the file size in this case (no client test)
        if not self._check_file_size(file_data) :
            logger.info("Test file size : the file %s is too big,"
                        "upload rejected", file_name)
            return json.dumps({u'error': u'sizeError'})


    if not self._check_file_id(file_name) or file_name in context:
        logger.debug("The file id for %s already exists,"
                     "upload rejected", file_name)
        return json.dumps({u'error': u'serverErrorAlreadyExists'})

    content_type = mimetypes.guess_type(file_name)[0]
    # sometimes plone mimetypes registry could be more powerful
    if not content_type :
        mtr = getToolByName(context, 'mimetypes_registry')
        koct = mtr.globFilename(file_name)
        if koct is not None :
            content_type = str(koct)

    portal_type = getDataFromAllRequests(request, 'typeupload') or ''
    title =  getDataFromAllRequests(request, 'title') or ''
    description =  getDataFromAllRequests(request, 'description') or ''

    if not portal_type :
        ctr = getToolByName(context, 'content_type_registry')
        portal_type = ctr.findTypeName(file_name.lower(),
                                       content_type, '') or 'File'

        # Our patch to detect context rules
        portal_type = detect_context_rules(context, portal_type)

    if file_data:
        factory = IQuickUploadFileFactory(context)
        logger.info("uploading file with %s : filename=%s,"
                    "title=%s, description=%s, content_type=%s,"
                    "portal_type=%s", upload_with, file_name, title,
                    description, content_type, portal_type)

        try :
            f = factory(file_name, title, description,
                        content_type, file_data, portal_type)
        except Exception:
            return json.dumps({u'error': u'serverError'})

        if f['success'] is not None :
            o = f['success']
            logger.info("file url: %s" % o.absolute_url())
            msg = {u'success': True}
        else :
            msg = {u'error': f['error']}
    else :
        msg = {u'error': u'emptyError'}

    return json.dumps(msg)

def detect_context_rules(context, portal_type):
    """ Detect context rules
    """

    # Rule for uploading DataFile(s) under DataTable(s)
    if context.portal_type == 'DataTable':
        portal_type = 'DataFile'
    # Rule for uploading EEAFigureFile(s) under EEAFigure(s)
    elif context.portal_type == 'EEAFigure':
        portal_type = 'EEAFigureFile'

    return portal_type

def QuickUploadCapableFileFactory__call__(self, name, title, description, 
                                            content_type, data, portal_type):
    """ Patched __call__ for QuickUploadCapableFileFactory """
    
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
        # in standard uploader - see also XXX in quick_upload.py
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
                        # XXX when getting file through request.BODYFILE 
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
