""" Products.EEAPloneadmin 980 upgrade steps
"""
from Products.CMFCore.utils import getToolByName


def add_plugins(setuptool):
    """ Adds new readability checker plugin
    """
    tinymce = getToolByName(setuptool, 'portal_tinymce')
    plugins = u'\neeareadabilitychecker|portal_skins/eea_tinymce_plugins' \
              u'/eeareadabilitychecker/editor_plugin.js'

    tinymce.customplugins += plugins
