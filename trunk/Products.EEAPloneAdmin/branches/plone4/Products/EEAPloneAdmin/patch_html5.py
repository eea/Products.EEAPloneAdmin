""" Monkey patches for HTML5 integration
"""

from plone.app.layout.links.viewlets import render_cachekey
from plone.app.layout.viewlets import ViewletBase
from plone.memoize import ram
import plone.app.layout.links.viewlets


class PatchedNavigationViewlet(ViewletBase):
    """ Navigation viewlet """

    @ram.cache(render_cachekey)
    def render(self):
        """ Render """
        return ''

plone.app.layout.links.viewlets.NavigationViewlet = PatchedNavigationViewlet
