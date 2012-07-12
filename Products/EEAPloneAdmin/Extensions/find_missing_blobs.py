""" Find missing blobs
"""

from Products.CMFCore.utils import getToolByName
from ZODB.utils import oid_repr
from plone.app.blob.interfaces import IBlobField
from zope.component import getMultiAdapter
import binascii
import logging
import os
import pprint

logger = logging.getLogger('eea')


def FindMissingBlobs(self):
    """ Find missing blobs
    """

    #res = {}
    cat = getToolByName(self, 'portal_catalog', None)
    #content_types = ['EEAFigureFile',
    #                 'Image',
    #                 'ImageFS',
    #                 'DataFile',
    #                 'File',
    #                 'FlashFile',
    #                 'FactSheetDocument',
    #                 'Report',
    #                 'Speech',
    #                 'PressRelease',
    #                 'Promotion',
    #                 'Highlight',
    #                 'Article']
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
            #filesize = filefield.get_size()
            filefield.get_size()

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
        logger.info('###--- %s *** %s *** %s *** /%s' % (i, k.portal_type,
                        k.getPath(), blob_path))

        if obj.portal_type in ['EEAFigureFile', 'DataFile', 'File',
                            'FlashFile', 'FactSheetDocument', 'Report']:
            file_field = obj.getField('file')
        else:
            file_field = obj.getField('image')
        filefield = file_field.getAccessor(obj)()
        #filesize = filefield.get_size()
        filefield.get_size()

    logger.info('Report done.')
    return "Done."


def getBlobOid(self):
    """ Get blob oid
    """
    if self.portal_type in ['EEAFigureFile', 'DataFile', 'File',
                            'FlashFile', 'FactSheetDocument', 'Report']:
        field = self.getField('file')
    else:
        field = self.getField('image')

    blob = field.getRaw(self).getBlob()
    oid = blob._p_oid
    serial = blob._p_serial

    #filename = field.getRaw(self).getFilename()
    field.getRaw(self).getFilename()

    directories = []
    # Create the bushy directory structure with the least significant byte
    # first
    for byte in str(oid):
        directories.append('0x%s' % binascii.hexlify(byte))
    path = os.path.sep.join(directories)

    nice_serial = "0x" + "".join([binascii.hexlify(x) for x in serial]) + \
                  ".blob"

    return '%s/%s' % (path, nice_serial)

def get_list_of_blobs(self):
    """ Get list of all blobs with their OID
    """
#   query = {'portal_type':{
#           'query':[
#               'Article',
#               'Blob' ,
#               'DataFile',
#               'EEAFigureFile',
#               'FactSheetDocument',
#               'File',
#               'FlashFile',
#               'HelpCenterInstructionalVideo',
#               'Highlight',
#               'Image',
#               'ImageFS',
#               'PressRelease',
#               'Promotion',
#               'Report'
#               'Speech',
#               ],
#           'operator':'or'
#       }}

    query = {
        'Language': 'all',
    }
    tree = {}

    cat = getToolByName(self, 'portal_catalog', None)
    brains = cat(**query)
    for brain in brains:
        obj = brain.getObject()
        schema = getattr(obj.aq_inner.aq_self, 'schema', None)
        if not schema:
            continue
        fields = [f for f in schema.fields() if IBlobField.providedBy(f)]
        for f in fields:
            bw = f.getRaw(obj)
            blob = bw.getBlob()
            tree[oid_repr(blob._p_oid)] = (f.getName(),
                                           brain.portal_type,
                                           brain.getURL())

    return pprint.pformat(tree)

def find_missing_blob_scales(self):
    """ Find missing blobs under scales
    """

    cat = getToolByName(self, 'portal_catalog', None)

    query = {'portal_type': ['Article']}

    brains = cat(**query)
    for brain in brains:
        obj = brain.getObject()

        logger.info('Object path /%s' % obj.absolute_url(1))
        sizes = obj.getField('image').getAvailableSizes(obj)
        for size in sizes:
            scale = obj.getField('image').getScale(obj, size)
            if not scale:
                continue
            scale_field = scale.getField('image')
            scalefield = scale_field.getAccessor(scale)()
            scale_size = scalefield.get_size()
            logger.info('%s *** %s' % (size, scale_size))

    return 'Done.'

def find_missing_scales(self):
    """ Find missing scales """
    cat = getToolByName(self, 'portal_catalog', None)

    content_types = ['EEAFigureFile',
                     'Image',
                     'ImageFS',
                     'DataFile',
                     'File',
                     'FlashFile',
                     'FactSheetDocument',
                     'Report',
                     'Speech',
                     'PressRelease',
                     'Promotion',
                     'Highlight',
                     'Article']


    query = {'portal_type': content_types, "Language":'all'}
    img_sizes = {}

    props = self.portal_properties.imaging_properties
    sizes = props.getProperty('allowed_sizes')
    for size in sizes:
        name, info = size.split(' ')
        w, h = info.split(':')
        img_sizes[name] = (int(w), int(h))

    broken = []

    brains = cat(**query)
    for brain in brains:
        obj = brain.getObject()

        for size in img_sizes.keys():
            #print obj.absolute_url(), size
            try:
                view = getMultiAdapter((obj, self.REQUEST), name="image_" \
                                                                    + size)
                view()
            except Exception:
                broken.append((obj, size))

    f = open("/tmp/out.txt", "w")
    f.writelines([" - ".join(x) for x in broken])
    return """<html><body><h3>Broken:</h3><ul>%s</ul></body></html""" % \
            "\n".join(["<li>%s - %s</li>" % x for x in broken])
