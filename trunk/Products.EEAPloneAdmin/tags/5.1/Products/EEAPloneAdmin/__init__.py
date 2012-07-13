""" Init
"""

from Products.LinguaPlone import config

config.AUTO_NOTIFY_CANONICAL_UPDATE = 0

#ZZZ: Check why collective.monkeypatcher don't apply patches below via zcml
from Products.EEAPloneAdmin import patch_cache
from Products.EEAPloneAdmin import patch_plone_app_discussion
__all__ = [ patch_cache.__name__,
            patch_plone_app_discussion.__name__ ]
