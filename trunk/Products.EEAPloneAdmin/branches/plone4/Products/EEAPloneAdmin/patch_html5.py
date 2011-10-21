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

def render(self):
    """ We need to generate the link in every case, since the new url
        base detection algorithm of kss relies on it. """
    return (u'<link rel="alternate" data-kss-base-url="kss-base-url" '
            'href="%s/" />' % self.context_state.object_url())
