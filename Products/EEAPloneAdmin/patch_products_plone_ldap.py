""" Products.PloneLDAP patches
"""
from Products.PluggableAuthService.UserPropertySheet import UserPropertySheet
import logging

logger = logging.getLogger("patch_products_plone_ldap")

def __patched_init__(self, id, user):
    self.id = id

    acl = self._getLDAPUserFolder(user)
    self._ldapschema = [(x['ldap_name'], x['public_name'],
                    x['multivalued'] and 'lines' or 'string') \
                for x in acl.getSchemaConfig().values() \
                if x['public_name']]

    properties = self._getCache(user)
    if not properties:
        properties = self.fetchLdapProperties(user)
        if properties:
            self._setCache(user, properties)
    if isinstance(properties, tuple):
        logger.warning(properties)
        properties = properties[0] if properties else {}
    if isinstance(properties, dict):
        id = properties.pop('id', id)
    UserPropertySheet.__init__(self, id,
            schema=[(x[1], x[2]) for x in self._ldapschema], **properties)