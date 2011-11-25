""" Init
"""

from Products.LinguaPlone import config

config.AUTO_NOTIFY_CANONICAL_UPDATE = 0

#TODO: Check why collective.monkeypatcher don't apply this patch via zcml
from Products.EEAPloneAdmin import patch_cache
__all__ = [ patch_cache.__name__ ]


