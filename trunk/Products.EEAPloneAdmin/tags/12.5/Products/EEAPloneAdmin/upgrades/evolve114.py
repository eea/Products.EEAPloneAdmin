""" Removing 'zc.async' left over from old single database configuration
"""
import logging
import transaction
logger = logging.getLogger('Products.EEAPloneAdmin')

def remove_old_async(context):
    """ Cleanup old zc.async queue from Data.fs
    """
    logger.info('Removing zc.async from Data.fs')
    queue = context._p_jar.root().pop('zc.async', None)
    if queue is None:
        logger.info("Nothing to do - zc.async not found within Data.fs.")
        return

    logger.info("Found 1 zc.async. Removing it...")
    transaction.commit()
