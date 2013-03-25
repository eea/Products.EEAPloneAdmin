""" Patch for plone.session version 3.5.2 to expire cookie on timeout
"""
import time
from email.Utils import formatdate
from plone.session.plugins.session import SessionPlugin as BasedSessionPlugin
import plone.session.plugins.session

class PatchedSessionPlugin(BasedSessionPlugin):
    """ Session authentication plugin.
    """

    def refresh(self, REQUEST):
        """Refresh the cookie"""
        setHeader = REQUEST.response.setHeader
        # Disable HTTP 1.0 Caching
        setHeader('Expires', formatdate(0, usegmt=True))
        if self.refresh_interval < 0:
            return self._refresh_content(REQUEST)
        now = time.time()
        refreshed = self._refreshSession(REQUEST, now)
        if not refreshed:
            # We have an unauthenticated user
            REQUEST.response.expireCookie(self.cookie_name, path='/')
            setHeader('Cache-Control',
                      'public, must-revalidate, max-age=%d, s-max-age=86400' %
                                self.refresh_interval)
            setHeader('Vary', 'Cookie')
        else:
            setHeader(
       'Cache-Control',
       'private, must-revalidate, proxy-revalidate, max-age=%d, s-max-age=0' %
                                self.refresh_interval)
        return self._refresh_content(REQUEST)

plone.session.plugins.session.SessionPlugin = PatchedSessionPlugin
