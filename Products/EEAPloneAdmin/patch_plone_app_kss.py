""" Patch for plone.app.kss ver 1.7.0
"""
import logging
from Acquisition import aq_inner
from plone.locking.interfaces import ILockable
from urlparse import urlsplit
from kss.core import kssaction, KSSExplicitError
from Products.CMFPlone import PloneMessageFactory as _

logger = logging.getLogger('Products.EEAPloneAdmin')

def changeWorkflowState(self, url):
    context = aq_inner(self.context)
    ksscore = self.getCommandSet('core')
    zopecommands = self.getCommandSet('zope')
    plonecommands = self.getCommandSet('plone')

    locking = ILockable(context, None)
    if locking is not None and not locking.can_safely_unlock():
        selector = ksscore.getHtmlIdSelector('plone-lock-status')
        zopecommands.refreshViewlet(selector, 'plone.abovecontent', 'plone.lockinfo')
        plonecommands.refreshContentMenu()
        return self.render()

    (proto, host, path, query, anchor) = urlsplit(url)
    if not path.endswith('content_status_modify'):
        raise KSSExplicitError, 'content_status_modify is not handled'
    action = query.split("workflow_action=")[-1].split('&')[0]
    context.content_status_modify(action)
    selector = ksscore.getCssSelector('.contentViews')
    zopecommands.refreshViewlet(selector, 'plone.contentviews', 'plone.contentviews')
    plonecommands.refreshContentMenu()
    self.issueAllPortalMessages()
    self.cancelRedirect()
