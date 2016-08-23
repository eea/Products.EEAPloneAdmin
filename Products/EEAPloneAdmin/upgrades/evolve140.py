""" Cleanup Zope Versions Control
"""
from zope.component import getUtility
from Products.EEAPloneAdmin.interfaces import IZVCleanup


def cleanup_zvc_helpcenter(context):
    """ Cleanup history for removed HelpCenter content-types
    """
    zvc = getUtility(IZVCleanup)
    zvc.cleanup_portal_type('HelpCenterFAQ')


def cleanup_zvc_removed(context):
    """ Cleanup history for Removed objects
    """
    zvc = getUtility(IZVCleanup)
    zvc.cleanup_removed()


def cleanup_zvc_figurefile(context):
    """ Cleanup history for EEA Figure File
    """
    zvc = getUtility(IZVCleanup)
    zvc.cleanup_portal_type('EEAFigureFile')
