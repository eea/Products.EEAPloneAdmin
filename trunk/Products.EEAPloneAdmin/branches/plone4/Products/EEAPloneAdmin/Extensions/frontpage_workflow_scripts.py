# -*- coding: utf-8 -*-
#
# File: EEAContentTypes.py
#
# Copyright (c) 2006 by []
# Generator: ArchGenXML Version 1.5.1-svn
#            http://plone.org/products/archgenxml
#
# GNU General Public License (GPL)
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.
#

__author__ = """unknown <unknown>"""
__docformat__ = 'plaintext'

from zope.component import queryAdapter
from Products.EEAContentTypes.interfaces import IWorkflowEmails
# Workflow Scripts for: frontpage_workflow
from Products.EEAContentTypes.config import DEBUG
if DEBUG:
    import socket
    socket.setdefaulttimeout(100)
##code-section workflow-script-header #fill in your manual code here
from Products.CMFCore.utils import getToolByName

message = """

    Type: %s
    Title: %s
    --
    %s

    Log in at:
    %s

    Regards
    EEA web team
    """


infoMessage = """

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


class WorkflowManagement(object):

    def __init__(self, state_change, role):
        self.obj = obj = state_change.object
        self.mhost = obj.MailHost
        self.toEmail = self.toConfirmationEmail = self.fromEmail = ""
        props = getattr(getToolByName(obj, 'portal_properties'), 'workflow_properties', None)
        portal = getToolByName(obj, 'portal_url').getPortalObject()
        self.portalType = obj.portal_type.lower()
        emails = queryAdapter(obj, IWorkflowEmails, state_change.new_state.getId(), None)
        if emails is not None and role is None:
            self.toEmail = emails.action
            self.toConfirmationEmail = emails.confirmation
            self.fromEmail = emails.sender
        else:
            # old behaviour - deprecated
            if role is None:
                role = ''
            defaultEmails = getattr(props, 'default_'+role, [])
            self.toEmail = list(getattr(props, self.portalType + '_' + role, defaultEmails))
            confirmationRoles = getattr(props, self.portalType + '_confirmation', [])
            self.toConfirmationEmail = []
            for role in confirmationRoles:
                for email in getattr(props, self.portalType + '_' + role, []):
                    if email not in self.toEmail:
                        self.toConfirmationEmail.append(email)

            self.fromEmail = self._getUserEmail(portal)
        self.subject = '[EEA CMS] - %s ' + state_change.new_state.title
            
        #absObjUrl = obj.absolute_url()
        objUrl = obj.absolute_url(1)
        if objUrl.startswith('SITE/'):
            objUrl = objUrl[5:]
        cmsUrl = getattr(props, 'cms_url', 'https://www-cms.eea.europa.eu/SITE/')
        editUrl = cmsUrl + objUrl + '/edit'
        #publishUrl = cmsUrl + objUrl + '/content_status_modify?workflow_action=publish'
        comment = state_change.kwargs.get('comment', '')
        if comment:
            comment = '%s\n--' % comment

        msg = obj.unrestrictedTraverse('workflow_action_message')
        self.msg = msg(obj, type=self.portalType, comment=comment, editUrl=editUrl )

        confirmationMsg = obj.unrestrictedTraverse('workflow_confirmation_message')
        self.confirmationMsg = confirmationMsg(obj, type=self.portalType, comment=comment, editUrl=editUrl )

    def _getUserEmail(self, portal):
        mt = getToolByName(portal, 'portal_membership')
        member = mt.getAuthenticatedMember()
        name = portal.email_from_name
        email = portal.email_from_address
        if member is not None:
            email = member.getProperty('email', None) or email
            name = member.getProperty('fullname', None) or name
            
        return "%s <%s>" % (name, email)
            
    def sendEmail(self, subject):
        if not getattr(self.obj, 'send_workflow_emails', True):
            # workflow emails disabled in this aquisition tree
            return
        
        if subject is None:
            subject = self.subject
        subject = subject % self.portalType

	# Add extra headers for the email, default as normal
	#	Importance:         Can be 'Normal', 'High', 'Low'
	#	X-MSMail-Priority:  Can be 'Normal', 'High', 'Low'
	#	X-Priority:         Can be '1 (Highest)', '2 (High)', '3 (Normal)', '4 (Low)' or '5 (Lowest)'
	#	Priority:           Can be 'normal', 'urgent' or 'non-urgent' (try to influence speed and delivery)
	#
	# 'Importance' and 'X-MSMail-Priority' are used by Outlook and Outlook Express while 'X-Priority' is used by Thunderbird and Eudora

        kwargs = {'Importance': 'Normal',
            'X-MSMail-Priority': 'Normal',
            'X-Priority': '3',
            'Priority': 'normal'}

        if len(self.toEmail) > 0:
            kwargs['Importance'] = 'High'
            kwargs['X-MSMail-Priority'] = 'High'
            kwargs['X-Priority'] = '1 (Highest)'
            kwargs['Priority'] = 'urgent'
            a_subject = 'Action: %s' % subject
            self.mhost.secureSend(self.msg, self.toEmail, self.fromEmail, a_subject, subtype="html", charset='utf-8', debug=DEBUG, **kwargs)

        if len(self.toConfirmationEmail) > 0:
            kwargs['Importance'] = 'Low'
            kwargs['X-MSMail-Priority'] = 'Low'
            kwargs['X-Priority'] = '5 (Lowest)'
            kwargs['Priority'] = 'non-urgent'
            c_subject = 'Confirmation: %s' % subject
            self.mhost.secureSend(self.confirmationMsg, self.toConfirmationEmail, self.fromEmail, c_subject, subtype="html", charset='utf-8', debug=DEBUG, **kwargs)

##/code-section workflow-script-header

def submitForProofReading(self, state_change, **kw):
    wf = WorkflowManagement(state_change, 'proofreader')
    subject = '[EEA CMS] - %s submitted for proof reading' 
    return wf.sendEmail(subject)

def submitForContentReview(self, state_change, **kw):
    wf = WorkflowManagement(state_change, 'reviewer')
    subject = '[EEA CMS] - %s submitted for content review' 
    return wf.sendEmail(subject)

def submitForWebQA(self, state_change, **kw):
    wf = WorkflowManagement(state_change, 'webqa')
    subject = '[EEA CMS] - %s submitted for Web QA' 
    return wf.sendEmail(subject)

def publish(self, state_change, **kw):
    wf = WorkflowManagement(state_change, '')
    subject = '[EEA CMS] - %s published' 
    return wf.sendEmail(subject)

def reject(self, state_change, **kw):
    wf = WorkflowManagement(state_change, 'owner')
    subject = '[EEA CMS] - %s sent back for revision' 
    return wf.sendEmail(subject)

def sendWorkflowEmail(self, state_change, **kw):
    wf = WorkflowManagement(state_change, None)
    subject = wf.subject or '[EEA CMS] - workflow changed for %s'
    return wf.sendEmail(subject)
