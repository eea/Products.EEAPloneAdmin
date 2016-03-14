""" This patch is related to ticket #9445

    The patch aim to catch the source of badly formatter cookies.
    This is a temporary fix, the final solution will come up
    once the source of badly formatted cookies is identified.
"""
import binascii
import logging
from Products.statusmessages import adapter
from Products.statusmessages.message import decode

logger = logging.getLogger('statusmessages')

def _decodeCookieValue(string):
    """Decode a cookie value to a list of Messages.
    """
    results = []
    # Return nothing if the cookie is marked as deleted
    if string == 'deleted':
        return results
    # Try to decode the cookie value
    try:
        value = binascii.a2b_base64(string)
        while len(value) > 1: # at least 2 bytes of data
            message, value = decode(value)
            if message is not None:
                results.append(message)
    except (binascii.Error, UnicodeEncodeError):
        # Start patch
        logger.exception('Unexpected value in statusmessages cookie: %s',
                         string)
        # End patch
        return []

    return results

adapter._decodeCookieValue = _decodeCookieValue
