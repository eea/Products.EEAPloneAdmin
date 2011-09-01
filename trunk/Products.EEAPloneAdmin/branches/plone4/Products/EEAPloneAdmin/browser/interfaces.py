""" Interfaces
"""
from zope.interface import Interface, Attribute

class IObjectTitle(Interface):
    """ IObjectTitle
    """
    title = Attribute(u'Object title or object + parent title')

class ILinguaPlone(Interface):
    """ ILinguaPlone
    """
    def setLanguages():
        """ Extract language from filename-LANG and set it on object
        """

    def connectTranslations():
        """ Make all filename-LANG a translation of filename or filename-en
        """

class IPloneAdmin(Interface):
    """ IPloneAdmin
    """
    def isCmsMode():
        """ Return true if we are in administration/cms mode. Usually that is
            when you are logged and/or when using a specific skin
        """

class IContextState(Interface):
    """ IContextState
    """
    def is_empty():
        """ Return true if context is empty (but only for anonymous)
        """

    def browser_title():
        """ Return the computed title for the curent context
        """

class IPortalState(Interface):
    """ IPortalState
    """
    def local_site():
        """ Return the base url for the local site
        """
