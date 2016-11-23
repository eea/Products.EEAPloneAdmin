""" Products.PloneLDAP patches
"""
from Products.PluggableAuthService.UserPropertySheet import UserPropertySheet
import logging

logger = logging.getLogger()

def __patched_init__(self, oid, user):
    self.id = oid

    acl = self._getLDAPUserFolder(user)
    self._ldapschema = [(x['ldap_name'], x['public_name'],
                    x['multivalued'] and 'lines' or 'string') \
                for x in acl.getSchemaConfig().values() \
                if x['public_name']]

    properties = self._getCache(user)
    logger.info(properties)
    if not properties:
        properties = self.fetchLdapProperties(user)
        if properties:
            self._setCache(user, properties)
    if isinstance(properties, tuple):
        logger.debug(properties)
        properties = properties[0] if properties else {}
    UserPropertySheet.__init__(self, oid,
            schema=[(x[1], x[2]) for x in self._ldapschema], **properties)
