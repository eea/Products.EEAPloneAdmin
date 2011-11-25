""" Patched to load EEA mail configuration
"""
import os
from Globals import package_home
from Acquisition import aq_base
from Products.MaildropHost.maildrop.stringparse import parse_assignments

EEA_CONFIG_PATH = os.path.join(package_home(globals()), 'eea_mailhost_config')
CONFIG_PATHS = {'DEFAULT' : EEA_CONFIG_PATH}

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

def patched_setConfigPath(self, path_key):
    """ Set the path to the currently active configuration file
    """
    config_path = CONFIG_PATHS.get(path_key, None)

    # Prevent passing in an invalid key, or maybe even a path
    if config_path is None:
        raise ValueError('Invalid path key %s' % path_key)

    # Make sure the provided configuration paths exist
    if not os.path.isfile(config_path):
        raise ValueError('Invalid config file path %s' % config_path)

    # Try to load the configuration to make sure we have a valid
    # configuration file.
    config = dict(parse_assignments(open(config_path).read()))
    for needed in ('SMTP_HOST', 'SMTP_PORT', 'MAILDROP_INTERVAL',
                   'MAILDROP_HOME', 'MAILDROP_TLS'):
        if config.get(needed, None) is None:
            raise RuntimeError('Invalid configuration file '
                               'at %s' % config_path)

    # Persist the new path, and then reload the configuration
    self.config_path = CONFIG_PATHS.get(path_key)
    self._load_config()
