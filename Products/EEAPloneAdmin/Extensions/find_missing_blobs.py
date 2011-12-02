""" Find missing blobs
"""
from ZODB.utils import oid_repr
import os
import binascii
import logging

logger = logging.getLogger('eea')

def FindMissingBlobs(self):

    from Products.CMFCore.utils import getToolByName
    res = {}
    cat = getToolByName(self, 'portal_catalog', None)
    #content_types = ['EEAFigureFile', 'Image', 'ImageFS', 'DataFile', 'File',
    #                 'FlashFile', 'FactSheetDocument', 'Report', 'Speech',
    #                 'PressRelease', 'Promotion', 'Highlight', 'Article']
    content_types = ['ImageFS']

    # Test everything will go well
    logger.info('Start testing')
    for ctype in content_types:
        logger.info('Testing %s' % ctype)
        tquery = { 'portal_type': [ctype],
                   'Language': 'all', }
        tbrains = cat(**tquery)

        for tk in tbrains[:1]:
            obj = tk.getObject()
            blob_path = getBlobOid(obj)
            logger.info('*** %s *** /%s' % (tk.getPath(), blob_path))
            if obj.portal_type in ['EEAFigureFile', 'DataFile', 'File',
                            'FlashFile', 'FactSheetDocument', 'Report']:
                file_field = obj.getField('file')
            else:
                file_field = obj.getField('image')
            filefield = file_field.getAccessor(obj)()
            filesize = filefield.get_size()

    logger.info('End testing')

    # Start checking all blobs
    query = {
        'portal_type': content_types,
        'Language': 'all',
    }

    brains = cat(**query)

    i = 0
    logger.info('Start report')
    for k in brains:
        i += 1
        obj = k.getObject()
        blob_path = getBlobOid(obj)
        logger.info('###--- %s *** %s *** %s *** /%s' % (i, k.portal_type, k.getPath(), blob_path))

        if obj.portal_type in ['EEAFigureFile', 'DataFile', 'File',
                            'FlashFile', 'FactSheetDocument', 'Report']:
            file_field = obj.getField('file')
        else:
            file_field = obj.getField('image')
        filefield = file_field.getAccessor(obj)()
        filesize = filefield.get_size()

    logger.info('Report done.')
    return "Done."

def getBlobOid(self):
    if self.portal_type in ['EEAFigureFile', 'DataFile', 'File',
                            'FlashFile', 'FactSheetDocument', 'Report']:
        field = self.getField('file')
    else:
        field = self.getField('image')

    blob = field.getRaw(self).getBlob()
    oid = blob._p_oid
    serial = blob._p_serial

    filename = field.getRaw(self).getFilename()

    directories = []
    # Create the bushy directory structure with the least significant byte
    # first
    for byte in str(oid):
        directories.append('0x%s' % binascii.hexlify(byte))
    path = os.path.sep.join(directories)

    nice_serial = "0x"+"".join([binascii.hexlify(x) for x in serial]) + ".blob"
    #xnice_serial = []
    #for x in str(serial):
        #xnice_serial.append('0x%s' % binascii.hexlify(x))
    #nice_serial = os.path.sep.join(xnice_serial)

    #cached = blob._p_blob_committed
    return '%s/%s' % (path, nice_serial)
