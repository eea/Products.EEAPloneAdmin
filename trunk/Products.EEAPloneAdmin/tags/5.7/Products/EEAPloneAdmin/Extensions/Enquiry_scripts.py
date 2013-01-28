""" Workflow Scripts for: Enquiry
"""

import quopri

enquiryTemplate = """From: %s
To: %s
Errors-to: %s
Subject: %s
Content-Type: text/plain; charset=utf-8
Content-Transfer-Encoding: 8bit

%s

<Type of requester: %s>
<Purpose: %s>"""

def sendToIC(self, state_change, **kw):
    """ Send to IC
    """
    enq = state_change.object
    portal = enq.portal_url.getPortalObject()
    question = enq.Description().replace('\r','')
    subject = "=?%s?q?%s?=" % ('utf-8', quopri.encodestring(enq.Title()))

    content = enquiryTemplate % (enq.getEmail(),
                                 portal.enquiry_email,
                                 portal.enquiry_email,
                                 subject,
                                 question,
                                 enq.getOccupation(),
                                 enq.getPurpuse())
    host = portal.MailHost
    host.send( content )
    print content
