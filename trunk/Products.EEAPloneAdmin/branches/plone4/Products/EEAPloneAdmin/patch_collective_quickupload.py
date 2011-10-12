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

def quick_upload_file(self) :
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
            file = request.BODYFILE
            file_data = file.read()
            file.seek(0)
        except AttributeError :
            # in case of cancel during xhr upload
            logger.info("Upload of %s has been aborted", file_name)
            # not really useful here since the upload block
            # is removed by "cancel" action, but
            # could be useful if someone change the js behavior
            return  json.dumps({u'error': u'emptyError'})
        except :
            logger.info("Error when trying to read the file %s in request", file_name)
            return json.dumps({u'error': u'serverError'})
    else :
        # using classic form post method (MSIE<=8)
        file_data = request.get("qqfile", None)
        filename = getattr(file_data,'filename', '')
        file_name = filename.split("\\")[-1]
        upload_with = "CLASSIC FORM POST"
        # we must test the file size in this case (no client test)
        if not self._check_file_size(file_data) :
            logger.info("Test file size : the file %s is too big, upload rejected" % file_name)
            return json.dumps({u'error': u'sizeError'})


    if not self._check_file_id(file_name) or file_name in context:
        logger.debug("The file id for %s already exists, upload rejected" % file_name)
        return json.dumps({u'error': u'serverErrorAlreadyExists'})

    content_type = mimetypes.guess_type(file_name)[0]
    # sometimes plone mimetypes registry could be more powerful
    if not content_type :
        mtr = getToolByName(context, 'mimetypes_registry')
        oct = mtr.globFilename(file_name)
        if oct is not None :
            content_type = str(oct)

    portal_type = getDataFromAllRequests(request, 'typeupload') or ''
    title =  getDataFromAllRequests(request, 'title') or ''
    description =  getDataFromAllRequests(request, 'description') or ''

    if not portal_type :
        ctr = getToolByName(context, 'content_type_registry')
        portal_type = ctr.findTypeName(file_name.lower(), content_type, '') or 'File'

        # Our patch to detect context rules
        portal_type = detect_context_rules(context, portal_type)

    if file_data:
        factory = IQuickUploadFileFactory(context)
        logger.info("uploading file with %s : filename=%s, title=%s, description=%s, content_type=%s, portal_type=%s" % \
                (upload_with, file_name, title, description, content_type, portal_type))

        try :
            f = factory(file_name, title, description, content_type, file_data, portal_type)
        except :
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
