""" Init patches
"""
from Products.LinguaPlone import config


# We tried to implement these as monkeypatches with
#   collective.monkeypatcher, but didn't succeed.

# Patch for plone.app.caching ver 1.0 to add extra headers
# Patch for plone.app.caching ver 1.1.8 to proper check method names
#    - patch for the 1.1.8 was merged to core under version > 1.1.8

# Patch plone.app.discussion ver >= 2.0.10, not to fail on migrate
# workflows when "Discussion Item" has no workflow assigned

# Patch plone.app.layout ver 2.2.7, due to #9518
from Products.EEAPloneAdmin.patches import patch_plone_app_layout, \
    patch_plone_app_caching, patch_plone_session, patch_plone_app_folder, \
    patch_plone_app_discussion

# Patch plone.session ver 3.5.2, due to #13992
# To be removed once plone.session ver > 3.5.3 (patch submitted to Plone core)
from Products.EEAPloneAdmin import translation_negotiator

#134252 patch content rules engine to go beyond site folder.
from plone.app.contentrules import handlers
from patches.patch_plone_app_contentrules_handlers import execute as \
                                                          patched_execute

# 135801 patch plone.restapi to use portal properties list of transitions
# to set EffectiveDate
has_restapi = True
try:
    from plone.restapi.services.workflow import transition
    from patches.plone_restapi_workflow_transition import \
        patched_recurse_transition
    from plone.restapi.deserializer.relationfield import \
        RelationChoiceFieldDeserializer
    from patches.patch_plone_restapi_deserializer_relationfield import \
        patched_call
except ImportError:
    has_restapi = False


# Patch plone.app.folder ver 1.1.3 due to #120304
# we have a folder "themes" that has an illegal ID name as a property name

config.AUTO_NOTIFY_CANONICAL_UPDATE = 0

__all__ = [patch_plone_app_caching.__name__,
           patch_plone_app_discussion.__name__,
           patch_plone_app_layout.__name__,
           patch_plone_app_folder.__name__,
           patch_plone_session.__name__,
           translation_negotiator.__name__]

handlers.execute = patched_execute
if has_restapi:
    transition.WorkflowTransition.recurse_transition = \
        patched_recurse_transition
    RelationChoiceFieldDeserializer.__call__ = patched_call
