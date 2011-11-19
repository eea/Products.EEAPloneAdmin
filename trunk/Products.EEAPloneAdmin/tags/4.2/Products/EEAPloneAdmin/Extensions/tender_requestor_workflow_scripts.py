""" Workflow Scripts for: tender_requestor_workflow
"""

#from Products.EEAPloneAdmin.config import DEBUG

def sendCFTLink(self, state_change, **kw):
    """ Send CFT Link
    """

    obj = state_change.object
    mhost = self.MailHost
    fromEmail = "%s <%s>" % (self.email_from_name, self.email_from_address)
    toEmail = obj.getEmail()
    subject = '[EEA] Your request for tender %s' % obj.getCallForId()
    message = """
    Your request has been accepted and you can download the tender at
    %s?cftrequestor=%s

    Regards
    EEA web team
    """

    msg = message % (
         obj.aq_parent.absolute_url(),
         obj.getId()
         )

    return mhost.send(msg, toEmail, fromEmail, subject)
