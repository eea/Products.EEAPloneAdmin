from zope.interface import Interface, Attribute

class IObjectTitle(Interface):
    
    title = Attribute(u'Object title or object + parent title')
    
class ILinguaPlone(Interface):

    def setLanguages():
        """ extract language from filename-LANG and set it on object. """

    def connectTranslations():
        """ make all filename-LANG a translation of filename or
            filename-en. """
        
class IPloneAdmin(Interface):

    def isCmsMode():
        """ Return true if we are in administration/cms mode. Usually that is
        when you are logged and/or when using a specific skin. """
