""" Monkey patches for HTML5 integration
"""

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.links.viewlets import render_cachekey
from plone.app.layout.viewlets import ViewletBase
import plone.app.layout.links.viewlets

class PatchedNavigationViewlet(ViewletBase):
    """ Navigation viewlet """

    _template = ViewPageTemplateFile('navigation.pt')

    @ram.cache(render_cachekey)
    def render(self):
        """ Render """
        return ''

plone.app.layout.links.viewlets.NavigationViewlet = PatchedNavigationViewlet
