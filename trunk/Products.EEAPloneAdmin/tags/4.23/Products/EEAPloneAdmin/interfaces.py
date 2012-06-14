""" Interfaces
"""

from zope.interface import Interface, Attribute

class IWorkflowEmails(Interface):
    """ Interface
    """

    action = Attribute("List of emails to recieve action email")
    confirmation = Attribute("List of emails to recieve confirmation email")
    sender = Attribute("Email for current user or portal email")
    subject = Attribute("Email subject")
