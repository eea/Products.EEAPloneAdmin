""" Interfaces
"""

import zope.i18nmessageid
from zope.interface import Interface, Attribute
from zope import schema

_ = zope.i18nmessageid.MessageFactory('eea')

class IWorkflowEmails(Interface):
    """ Interface
    """

    action = Attribute("List of emails to recieve action email")
    confirmation = Attribute("List of emails to recieve confirmation email")
    sender = Attribute("Email for current user or portal email")
    subject = Attribute("Email subject")

class IEEACacheSettings(Interface):
    """Settings stored in the registry.
    """

    contentTypeURLMapping = schema.Dict(
            title=_(u"Content type/url mapping"),
            description=_(u"Maps content type names to purge paths"),
            key_type=schema.ASCIILine(title=_(u"Content type name")),
            value_type=schema.List(
                title=_(u"URL Paths"),
                value_type=schema.ASCIILine(title=_(u"Path"))
            ),
        )
