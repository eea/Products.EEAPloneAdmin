""" Patched to load EEA mail configuration
"""
import os
from Globals import package_home
from Acquisition import aq_base
from Prodcuts.MaildropHost.MaildropHost import DEFAULT_CONFIG_PATH

EEA_CONFIG_PATH = os.path.join(package_home(globals()), 'eea_mailhost_config')
CONFIG_PATHS = {'DEFAULT' : DEFAULT_CONFIG_PATH,
                'EEA': EEA_CONFIG_PATH}

def patched_getConfigPath(self):
    """ Get the path to the currently active configuration file
    """
    return getattr(aq_base(self), 'config_path', EEA_CONFIG_PATH)

def patched_getCandidateConfigPaths(self):
    """ Retrieve the config paths set in zope.conf
    """
    path_keys = CONFIG_PATHS.keys()
    path_keys.sort()
    return tuple([(x, CONFIG_PATHS.get(x)) for x in path_keys])
