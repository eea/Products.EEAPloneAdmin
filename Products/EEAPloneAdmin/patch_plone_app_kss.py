""" Patch for plone.app.kss ver 1.7.0
"""
import logging
from Acquisition import aq_inner, Implicit
from plone.locking.interfaces import ILockable
from urlparse import urlsplit
from kss.core import kssaction, KSSExplicitError
from Products.CMFPlone import PloneMessageFactory as _
from zope.interface import implements
from plone.app.layout.globals.interfaces import IViewView
from plone.app.kss.interfaces import IPloneKSSView
from plone.app.kss.plonekssview import PloneKSSView

logger = logging.getLogger('Products.EEAPloneAdmin')

class ContentMenuView(Implicit, PloneKSSView):
    """ Patch plone.app.kss ver 1.7.0, not to fail silently
        and to display a visual progress on state change
    """

    implements(IPloneKSSView, IViewView)

    @kssaction
    def changeWorkflowState(self, url):
        """ KSS Change Workflow State
        """
        context = aq_inner(self.context)
        ksscore = self.getCommandSet('core')
        zopecommands = self.getCommandSet('zope')
        plonecommands = self.getCommandSet('plone')

        locking = ILockable(context, None)
        if locking is not None and not locking.can_safely_unlock():
            selector = ksscore.getHtmlIdSelector('plone-lock-status')
            zopecommands.refreshViewlet(selector,
                                        'plone.abovecontent',
                                        'plone.lockinfo')
            plonecommands.refreshContentMenu()
            return self.render()

        (proto, host, path, query, anchor) = urlsplit(url)
        if not path.endswith('content_status_modify'):
            raise KSSExplicitError, 'content_status_modify is not handled'
        action = query.split("workflow_action=")[-1].split('&')[0]

        #Patch not to silently fail
        try:
            context.content_status_modify(action)
        except Exception, err:
            logger.error('Error on state change [%s, %s]: %s' %
                                                  (action,
                                                   context.absolute_url(),
                                                   err))
            context.plone_utils.addPortalMessage(
                           _(u'An error occurred on state change. Contact '
                              'portal administrator for more details.'),
                            'error')

        selector = ksscore.getCssSelector('.contentViews')
        zopecommands.refreshViewlet(selector,
                                    'plone.contentviews',
                                    'plone.contentviews')
        plonecommands.refreshContentMenu()
        self.issueAllPortalMessages()
        self.cancelRedirect()
