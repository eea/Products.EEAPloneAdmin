""" Patch for plone.session version 3.5.2 to expire cookie on timeout and
    to allow cookie_domain override from os environment
"""

from App.config import getConfiguration
from email.Utils import formatdate
from plone.session.plugins.session import SessionPlugin as BasedSessionPlugin
import binascii
import os
import plone.session.plugins.session
import time


class PatchedSessionPlugin(BasedSessionPlugin):
    """ Session authentication plugin.

    We patch:
    * ``refresh`` to expire/delete the auth cookie when it is timeout/invalid
    * ``_setCookie`` and ``resetCredentials`` to allow cookie_domain override
    from os environment. See http://taskman.eionet.europa.eu/issues/14118
    and http://taskman.eionet.europa.eu/issues/13992
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

    def _setCookie(self, cookie, response):
        cookie=binascii.b2a_base64(cookie).rstrip()
        # disable secure cookie in development mode, to ease local testing
        config = getConfiguration()
        if config.debug_mode:
            secure = False
        else:
            secure = self.secure

        options = dict(path=self.path, secure=secure, http_only=True)

        # Allow override based on system environment
        # during tests, config.environment doesn't exist
        environ = getattr(config, 'environment', os.environ)
        cookie_domain = environ.get('PLONE_COOKIE_DOMAIN', self.cookie_domain)
        if cookie_domain:
            options['domain'] = cookie_domain
        if self.cookie_lifetime:
            options['expires'] = cookie_expiration_date(self.cookie_lifetime)
        response.setCookie(self.cookie_name, cookie, **options)

    def resetCredentials(self, request, response):
        response=self.REQUEST["RESPONSE"]
        environ = getattr(config, 'environment', os.environ)
        cookie_domain = environ.get('PLONE_COOKIE_DOMAIN', self.cookie_domain)
        if cookie_domain:
            response.expireCookie(
                self.cookie_name, path=self.path, domain=cookie_domain)
        else:
            response.expireCookie(self.cookie_name, path=self.path)

plone.session.plugins.session.SessionPlugin = PatchedSessionPlugin
