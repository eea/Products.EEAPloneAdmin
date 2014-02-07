""" Re-mount catalogs.

Copied from redturtle.catalogmount-0.3.egg.
Credits for the original script goes to Andrew Mleczko, RedTurtle
"""
from Products.ZODBMountPoint.MountedObject import (
    manage_getMountStatus,
    MountedObject,
    setMountPoint,
    CustomTrailblazer
)
from StringIO import StringIO
import tempfile
from App.config import getConfiguration
import transaction
import logging
logger = logging.getLogger('Products.EEAPloneAdmin')

def mount(self, out=None):
    """ Mount catalogs
    """
    if out is None:
        out = StringIO()

    to_mount = manage_getMountStatus(self)
    items = [item for item in to_mount if 'catalog' in item['path']
                  and '** Something is in the way **' in item['status']]

    msg = 'Mounting... %s catalogs' % len(items)
    logger.warn(msg)
    out.write(msg)

    for item in items:
        path = item['path']
        logger.info('Mounting %s', path)
        oid = path.split('/')[-1]
        old_obj = self.unrestrictedTraverse(path)
        old_parent = old_obj.aq_parent.aq_base
        db_name = item['name']
        db = getConfiguration().dbtab.getDatabase(path)
        new_trans = db.open()

        root = new_trans.root()
        if not root.has_key('Application'):
            from OFS.Application import Application
            root['Application'] = Application()
            transaction.savepoint(optimistic=True)

        root = root['Application']

        f = tempfile.TemporaryFile()
        old_obj._p_jar.exportFile(old_obj._p_oid, f)
        f.seek(0)

        new_obj = root._p_jar.importFile(f)
        f.close()

        blazer = CustomTrailblazer(root)
        obj = blazer.traverseOrConstruct(path)
        obj.aq_parent._setOb(oid, new_obj)

        mo = MountedObject(path)
        mo._create_mount_points = True

        old_parent._p_jar.add(mo)
        old_parent._setOb(oid, mo)
        setMountPoint(old_parent, oid, mo)
        msg = "Path: %s, mounted to db:%s" % (path, db_name)
        logger.warn(msg)
        out.write(msg)

        msg = ("Done mounting 1 catalog. Breaking. "
               "Please rerun this until all catalogs are mounted")
        logger.warn(msg)
        out.write(msg)
        break

    return out.getvalue()
