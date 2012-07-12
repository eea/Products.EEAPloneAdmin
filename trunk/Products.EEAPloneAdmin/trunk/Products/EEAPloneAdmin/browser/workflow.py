""" Workflow scripts
"""

from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName
from Products.EEAPloneAdmin.interfaces import IWorkflowEmails
from zope.component import queryAdapter
from email.message import Message

message = u"""

    Type: %s
    Title: %s
    --
    %s

    Log in at:
    %s

    Regards
    EEA web team
    """


infoMessage = u"""

    Type: %s
    Titel: %s
    --
    %s

    To - edit
    Please go to
    %s
    to edit the submitted content. (Log in if needed.)

    Regards
    EEA web team
    """

class WorkflowSupport(BrowserView):
    """ EEA Workflow Support
    """
    def __call__(self, state_change, role):
        return WorkflowManagement(state_change, role)

class WorkflowManagement(object):
    """ Workflow email handler
    """
    def __init__(self, state_change, role):
        self.obj = obj = state_change.object
        self.mhost = obj.MailHost
        self.toEmail = self.toConfirmationEmail = self.fromEmail = ""
        props = getattr(
            getToolByName(obj, 'portal_properties'), 'workflow_properties',
            None)
        portal = getToolByName(obj, 'portal_url').getPortalObject()
        self.portalType = obj.portal_type.lower()
        emails = queryAdapter(obj, IWorkflowEmails,
                              state_change.new_state.getId(), None)
        if emails is not None and role is None:
            self.toEmail = emails.action
            self.toConfirmationEmail = emails.confirmation
            self.fromEmail = emails.sender
        else:
            # old behaviour - deprecated
            if role is None:
                role = ''
            defaultEmails = getattr(props, 'default_'+role, [])
            self.toEmail = list(getattr(props,
                                self.portalType + '_' + role, defaultEmails))
            confirmationRoles = getattr(props,
                                self.portalType + '_confirmation', [])

            self.toConfirmationEmail = []
            for role in confirmationRoles:
                for email in getattr(props, self.portalType + '_' + role, []):
                    if email not in self.toEmail:
                        self.toConfirmationEmail.append(email)

            self.fromEmail = self._getUserEmail(portal)
        self.subject = '[EEA CMS] - %s ' + state_change.new_state.title
        objUrl = obj.virtual_url_path()
        if objUrl.startswith('/SITE/'):
            objUrl = objUrl[6:]
        cmsUrl = getattr(props, 'cms_url',
                         'https://www-cms.eea.europa.eu/SITE/')
        editUrl = cmsUrl + objUrl + '/edit'
        comment = state_change.kwargs.get('comment', '')
        if comment:
            comment = u'%s\n--' % comment

        msg = obj.unrestrictedTraverse('workflow_action_message', None)
        if msg:
            self.msg = msg(obj, type=self.portalType,
                           comment=comment, editUrl=editUrl )
        else:
            self.msg = u'Action message for %s' % editUrl

        confirmationMsg = obj.unrestrictedTraverse(
            'workflow_confirmation_message', None)
        if confirmationMsg:
            self.confirmationMsg = confirmationMsg(obj,
                      type=self.portalType, comment=comment, editUrl=editUrl)
        else:
            self.confirmationMsg = u'Confirmation message for %s' % \
                                                       obj.absolute_url()

    def _getUserEmail(self, portal):
        """ Get user email
        """
        mt = getToolByName(portal, 'portal_membership')
        member = mt.getAuthenticatedMember()
        name = portal.email_from_name
        email = portal.email_from_address
        if member is not None:
            email = member.getProperty('email', None) or email
            name = member.getProperty('fullname', None) or name

        return "%s <%s>" % (name, email)

    def sendEmail(self, subject):
        """ Send email
        """
        if not getattr(self.obj, 'send_workflow_emails', True):
            # workflow emails disabled in this aquisition tree
            return

        if subject is None:
            subject = self.subject
        subject = subject % self.portalType

        # Add extra headers for the email, default as normal
        #   Importance:         Can be 'Normal', 'High', 'Low'
        #   X-MSMail-Priority:  Can be 'Normal', 'High', 'Low'
        #   X-Priority:         Can be '1 (Highest)', '2 (High)',
        #                       '3 (Normal)', '4 (Low)' or '5 (Lowest)'
        #   Priority:           Can be 'normal', 'urgent' or 'non-urgent'
        #                       (try to influence speed and delivery)
        #
        # 'Importance' and 'X-MSMail-Priority' are used by Outlook and
        #   Outlook Express while 'X-Priority' is used by Thunderbird and Eudora

        #ZZZ: plone4 ichimdav this was unused, see if it's still needed
        #kwargs = {'Importance': 'Normal',
        #    'X-MSMail-Priority': 'Normal',
        #    'X-Priority': '3',
        #    'Priority': 'normal'}

        if len(self.toEmail) > 0:
            m = Message()
            m.set_payload(self.msg, 'utf-8')
            m.set_type('text/html')
            m.add_header('Importance', 'High')
            m.add_header('X-MSMail-Priority', 'High')
            m.add_header('X-Priority', '1 (Highest)')
            m.add_header('Priority', 'urgent')
            a_subject = 'Action: %s' % subject

            self.mhost.send(m,
                            mto=self.toEmail,
                            mfrom=self.fromEmail,
                            subject=a_subject,
                            msg_type='text/html',
                            )

        if len(self.toConfirmationEmail) > 0:
            m = Message()
            m.set_payload(self.confirmationMsg, 'utf-8')
            m.set_type('text/html')
            m.add_header('Importance', 'High')
            m.add_header('X-MSMail-Priority', 'High')
            m.add_header('X-Priority', '1 (Highest)')
            m.add_header('Priority', 'urgent')
            a_subject = 'Action: %s' % subject
            c_subject = 'Confirmation: %s' % subject

            self.mhost.send(      m,
                                  mto=self.toConfirmationEmail,
                                  mfrom=self.fromEmail,
                                  subject=c_subject,
                                  msg_type="text/html",
                                  )
