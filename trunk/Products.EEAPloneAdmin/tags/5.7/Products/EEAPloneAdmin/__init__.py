""" Init patches
"""

from Products.LinguaPlone import config

config.AUTO_NOTIFY_CANONICAL_UPDATE = 0

# We tried to implement these as monkeypatches with
#   collective.monkeypatcher, but didn't succeed.

# Patch for plone.app.caching ver 1.0 to add extra headers
from Products.EEAPloneAdmin import patch_cache

# Patch plone.app.discussion ver >= 2.0.10, not to fail on migrate
# workflows when "Discussion Item" has no workflow assigned
from Products.EEAPloneAdmin import patch_plone_app_discussion

# Patch Products.statusmessages ver 4.0, due to #9445
from Products.EEAPloneAdmin import patch_statusmessages

# Patch plone.app.layout ver 2.2.7, due to #9518
from Products.EEAPloneAdmin import patch_plone_app_layout

__all__ = [ patch_cache.__name__,
            patch_plone_app_discussion.__name__,
            patch_plone_app_layout.__name__,
            patch_statusmessages.__name__ ]