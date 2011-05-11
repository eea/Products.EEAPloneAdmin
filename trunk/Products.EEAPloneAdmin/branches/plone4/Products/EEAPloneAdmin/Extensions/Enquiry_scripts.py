# -*- coding: utf-8 -*-
#
# File: EEAEnquiry.py
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


# Workflow Scripts for: Enquiry

##code-section workflow-script-header #fill in your manual code here
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

##/code-section workflow-script-header


def sendToIC(self, state_change, **kw):
    enq = state_change.object
    portal = enq.portal_url.getPortalObject()
    question=enq.Description().replace('\r','')
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


