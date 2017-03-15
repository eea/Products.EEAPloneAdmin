""" Cleanup Zope Versions Control
"""
from zope.component import getUtility
from Products.EEAPloneAdmin.interfaces import IZVCleanup

def cleanup_zvc_helpcenter(context):
    """ Cleanup history for removed HelpCenter content-types
    """
    zvc = getUtility(IZVCleanup)
    zvc.cleanup_portal_type("HelpCenterFAQ")


def cleanup_zvc_removed(context):
    """ Cleanup history for Removed objects
    """
    zvc = getUtility(IZVCleanup)
    zvc.cleanup_removed()


def cleanup_zvc_figurefile(context):
    """ Cleanup history for EEA Figure File
    """
    zvc = getUtility(IZVCleanup)
    zvc.cleanup_portal_type("EEAFigureFile")


def cleanup_zvc_sparql(context):
    """ Cleanup cached_result for EEA Sparql
    """
    zvc = getUtility(IZVCleanup)
    zvc.cleanup_attributes("Sparql", "cached_result")


def cleanup_zvc_image_fields(context):
    """ Cleanup image field for pdftheme
    """
    zvc = getUtility(IZVCleanup)
    ptypes = ["Fiche", "GIS Application"]
    for ptype in ptypes:
        zvc.cleanup_image_fields(ptype, "image")
