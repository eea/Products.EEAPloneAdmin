from Products.LinguaPlone import config

config.AUTO_NOTIFY_CANONICAL_UPDATE = 0

#TODO: See why collective.monkeypatcher don't apply this patch via zcml
import patch_cache

