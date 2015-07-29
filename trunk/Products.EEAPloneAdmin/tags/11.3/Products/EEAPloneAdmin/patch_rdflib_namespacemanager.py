""" RDFLib patches
"""
import os
import time
import logging
from urllib import pathname2url
from urlparse import urljoin, urldefrag

from rdflib import URIRef


logger = logging.getLogger("Products.EEAPloneAdmin")


def _patched_absolutize(self, uri, defrag=1):
    """ return absolute path
    """
    try:
        cwd = os.getcwd()
    except OSError:
        # log, wait a little and try again
        logger.exception("First attempt to get cwd failed")
        time.sleep(0.5)
        cwd = os.getcwd()
        logger.exception("Second attempt to get cwd succeeded, value: %r", cwd)
    path_url = pathname2url(cwd)
    base = urljoin("file:", path_url)
    result = urljoin("%s/" % base, uri, allow_fragments=not defrag)
    if defrag:
        result = urldefrag(result)[0]
    if not defrag:
        if uri and uri[-1] == "#" and result[-1] != "#":
            result = "%s#" % result
    return URIRef(result)
