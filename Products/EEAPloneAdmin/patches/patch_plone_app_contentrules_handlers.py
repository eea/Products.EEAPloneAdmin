""" Patch for plone.app.contentrules
"""
from plone.contentrules.engine.interfaces import IRuleExecutor
from plone.contentrules.engine.interfaces import IRuleStorage
from plone.contentrules.engine.interfaces import StopRule
from Products.CMFPlone.interfaces import IPloneSiteRoot
from zope.component import queryUtility
from Acquisition import aq_inner
from Acquisition import aq_parent
from plone.app.contentrules.handlers import init, _status


def execute(context, event):
    """Execute all rules relative to the context, and bubble as appropriate.
    """
    # Do nothing if there is no rule storage or it is not active
    storage = queryUtility(IRuleStorage)
    if storage is None or not storage.active:
        return
    init()

    rule_filter = _status.rule_filter

    # Stop if someone else is already executing. This could happen if,
    # for example, a rule triggered here caused another event to be fired.
    # We continue if we are in the context of a 'cascading' rule.

    if rule_filter.in_progress and not rule_filter.cascade:
        return

    # Tell other event handlers to be equally kind
    rule_filter.in_progress = True

    # Prepare to break hard if a rule demanded execution be stopped
    try:

        # Try to execute rules in the context. It may not work if the context
        # is not a rule executor, but we may still want to bubble events
        executor = IRuleExecutor(context, None)
        if executor is not None:
            executor(event, bubbled=False, rule_filter=rule_filter)

        # Do not bubble beyond the site root
        is_site = context.id == 'SITE'
        if not IPloneSiteRoot.providedBy(context) or is_site:
            parent = aq_parent(aq_inner(context))
            while parent is not None:
                parent_is_site = parent.id == 'SITE'
                executor = IRuleExecutor(parent, None)
                if executor is not None:
                    executor(event, bubbled=True, rule_filter=rule_filter)
                # 134252 set parent to none only if parent id != SITE
                if IPloneSiteRoot.providedBy(parent) and not parent_is_site:
                    parent = None
                else:
                    parent = aq_parent(aq_inner(parent))

    except StopRule:
        pass

    # We are done - other events that occur after this one will be allowed to
    # execute rules again
    rule_filter.in_progress = False
