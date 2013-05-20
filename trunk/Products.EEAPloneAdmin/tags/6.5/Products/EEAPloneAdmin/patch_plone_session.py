""" Patch for plone.session version 3.5.2 to expire cookie on timeout and
    to allow cookie_domain override from os environment
"""

from App.config import getConfiguration
from email.Utils import formatdate
from plone.session.plugins.session import SessionPlugin as BasedSessionPlugin
import binascii
import os
import plone.session.plugins.session as plsession
import time


COOKIENAME = "PLONE_COOKIE_DOMAIN"


class PatchedSessionPlugin(BasedSessionPlugin):
    """ Session authentication plugin.

    We patch:
    * ``refresh`` to expire/delete the auth cookie when it is timeout/invalid
    * ``_setCookie`` and ``resetCredentials`` to allow cookie_domain override
    from os environment. See http://taskman.eionet.europa.eu/issues/14118
    and http://taskman.eionet.europa.eu/issues/13992
    """

    # IAuthenticationPlugin implementation
    def authenticateCredentials(self, credentials):
        if not credentials.get("source", None)=="plone.session":
            return None

        ticket=credentials["cookie"]
        ticket_data = self._validateTicket(ticket)
        if ticket_data is None:
            self.refresh(self.REQUEST)
            return None
        (digest, userid, tokens, user_data, timestamp) = ticket_data
        pas=self._getPAS()
        info=pas._verifyUser(pas.plugins, user_id=userid)
        if info is None:
            self.refresh(self.REQUEST)
            return None

        return (info['id'], info['login'])

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
            self.resetCredentials(REQUEST, REQUEST.response)
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

    def _get_cookie_domain(self, config):
        """Get the proper cookie domain for the environment.

        Order of priorities:
        * os.environ gets 1st priority
        * zope.conf environment, can be set in buildout file, comes second
        * last is option set in Data.fs
        """
        cookie_domain = os.environ.get(COOKIENAME, None)
        if cookie_domain:
            return cookie_domain

        environ = getattr(config, 'environment', {})
        cookie_domain = environ.get(COOKIENAME, self.cookie_domain)
        return cookie_domain

    def _setCookie(self, cookie, response):
        """ Set cookie helper method
        """
        cookie = binascii.b2a_base64(cookie).rstrip()
        # disable secure cookie in development mode, to ease local testing
        config = getConfiguration()
        if config.debug_mode:
            secure = False
        else:
            secure = self.secure

        options = dict(path=self.path, secure=secure, http_only=True)

        cookie_domain = self._get_cookie_domain(config)

        # Allow override based on system environment
        # during tests, config.environment doesn't exist
        if cookie_domain:
            options['domain'] = cookie_domain
        if self.cookie_lifetime:
            options['expires'] = plsession.cookie_expiration_date(
                                                        self.cookie_lifetime)
        response.setCookie(self.cookie_name, cookie, **options)

    def resetCredentials(self, request, response):
        """ resetCredential by expiring auth cookie
        """
        config = getConfiguration()
        cookie_domain = self._get_cookie_domain(config)
        if cookie_domain:
            response.expireCookie(
                self.cookie_name, path=self.path, domain=cookie_domain)
        else:
            response.expireCookie(self.cookie_name, path=self.path)

plsession.SessionPlugin = PatchedSessionPlugin
