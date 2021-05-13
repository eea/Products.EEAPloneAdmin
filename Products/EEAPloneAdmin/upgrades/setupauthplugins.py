"""
Restore deleted Zope root Basic authentication.
"""

from Products.CMFCore.utils import getToolByName

from Products.PlonePAS import setuphandlers


def setup_auth_plugins(self):
    """
    Restore deleted Zope root Basic authentication.
    """
    # Copied from the code that is run when adding a plone site to a fresh ZODB:
    # `./plone/app/upgrade/v30/profiles/beta1_beta2/import_steps.xml:32:
    # handler="Products.PlonePAS.setuphandlers.setupPlonePAS"`

    # Acquire parent user folder.
    parent = self.getPhysicalRoot()

    # Get the new uf
    uf = getToolByName(parent, 'acl_users')

    pas = uf.manage_addProduct['PluggableAuthService']
    plone_pas = uf.manage_addProduct['PlonePAS']
    setuphandlers.setupAuthPlugins(
        parent,
        pas,
        plone_pas,
        deactivate_basic_reset=False,
        deactivate_cookie_challenge=True,
    )
