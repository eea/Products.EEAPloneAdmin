""" Backup profiles
"""
from Products.EEAPloneAdmin.async import backup_profiles
from plone import api


def backup(context):
    """ Add async jobs to cleanup catalogs daily
    """
    stool = api.portal.get_tool(name='portal_setup')
    return backup_profiles(stool)
