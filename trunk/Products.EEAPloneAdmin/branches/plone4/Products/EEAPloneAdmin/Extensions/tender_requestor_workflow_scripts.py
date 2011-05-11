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


# Workflow Scripts for: tender_requestor_workflow

##code-section workflow-script-header #fill in your manual code here
#from Products.CMFCore.utils import getToolByName
from Products.EEAContentTypes.config import DEBUG
##/code-section workflow-script-header


def sendCFTLink(self, state_change, **kw):
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

    return mhost.secureSend(msg, toEmail, fromEmail, subject, debug=DEBUG)


