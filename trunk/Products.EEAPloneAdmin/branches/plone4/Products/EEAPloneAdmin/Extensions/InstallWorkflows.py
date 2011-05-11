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


from Products.CMFCore.utils import getToolByName
from Products.ExternalMethod.ExternalMethod import ExternalMethod

##code-section module-header #fill in your manual code here
##/code-section module-header

def installWorkflows(self, package, out):
    """Install the custom workflows for this product."""

    productname = 'EEAContentTypes'
    workflowTool = getToolByName(self, 'portal_workflow')

    ourProductWorkflow = ExternalMethod('temp', 'temp',
                                        productname+'.'+'CallForTender',
                                        'createCallForTender')
    workflow = ourProductWorkflow(self, 'CallForTender')
    if 'CallForTender' in workflowTool.listWorkflows():
        print >> out, 'CallForTender already in workflows.'
    else:
        workflowTool._setObject('CallForTender', workflow)
    workflowTool.setChainForPortalTypes(['CallForTender', 'CallForInterest'], workflow.getId())

    ourProductWorkflow = ExternalMethod('temp', 'temp',
                                        productname+'.'+'frontpage_workflow',
                                        'createfrontpage_workflow')
    workflow = ourProductWorkflow(self, 'frontpage_workflow')
    if 'frontpage_workflow' in workflowTool.listWorkflows():
        print >> out, 'frontpage_workflow already in workflows.'
    else:
        workflowTool._setObject('frontpage_workflow', workflow)
    workflowTool.setChainForPortalTypes(['Highlight', 'PressRelease', 'Speech'], workflow.getId())

    ourProductWorkflow = ExternalMethod('temp', 'temp',
                                        productname+'.'+'tender_requestor_workflow',
                                        'createtender_requestor_workflow')
    workflow = ourProductWorkflow(self, 'tender_requestor_workflow')
    if 'tender_requestor_workflow' in workflowTool.listWorkflows():
        print >> out, 'tender_requestor_workflow already in workflows.'
    else:
        workflowTool._setObject('tender_requestor_workflow', workflow)
    workflowTool.setChainForPortalTypes(['CFTRequestor'], workflow.getId())

    ##code-section after-workflow-install #fill in your manual code here
    ##/code-section after-workflow-install

    return workflowTool

def uninstallWorkflows(self, package, out):
    """Deinstall the workflows.

    This code doesn't really do anything, but you can place custom
    code here in the protected section.
    """

    ##code-section workflow-uninstall #fill in your manual code here
    ##/code-section workflow-uninstall

    pass
