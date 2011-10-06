""" Monkey patches for p4a.fileimage
"""
import os
import tempfile
from zope.publisher.http import HTTPRequest
import logging

logger = logging.getLogger("Products.EEAPloneAdmin")

def write_ofsfile_to_tempfile(obj, preferred_name=None):
    """Assumes the file obj is of type OFS.Image.File and will write
    it to a temporary file returning the filename of the temp file.  Uses
    the possibly acquired index_html method to fetch the file.  This
    is a little more compatible with objects that seem like OFS.Image.File
    instances.
    """

    filename = preferred_name
    if filename is None:
        filename = obj.id
        if callable(filename):
            filename = filename()
    fd, filename = tempfile.mkstemp('_'+filename)
    os.close(fd)
    fout = open(filename, 'wb')

    class TempResponse(object):
        """ Teml response
        """
        def getHeader(self, n):
            """ Get header
            """
            pass

        def setHeader(self, n, v):
            """ Set header
            """
            pass

        def setBase(self, v):
            """ Set base
            """
            pass

        def write(self, d):
            """ Write
            """
            fout.write(d)

    class TempRequest(HTTPRequest):
        """ Temp request
        """
        def get_header(self, n, default=None):
            """ Get header
            """
            if default is not None:
                return default
            return ''

    temp_res = TempResponse()
    req = TempRequest(obj, {}, temp_res)
    if hasattr(obj, 'index_html'):
        res = obj.index_html(req, temp_res)
    else:
        res = obj.data  #assumes this is a plone.app.blob.field.BlobWrapper

    if res:
        if isinstance(res, str):
            fout.write(res)
        else:
            # assumes some sort of iterator
            for x in res:
                try:
                    fout.write(x)
                except UnicodeEncodeError:
                    logger.warn('Invalid characted found.')
                    continue

    fout.close()

    return filename
