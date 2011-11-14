""" Workflow scripts
"""
from zope.component import queryMultiAdapter
from Products.EEAPloneAdmin.config import DEBUG

if DEBUG:
    import socket
    socket.setdefaulttimeout(100)

def submitForProofReading(self, state_change, **kw):
    """ Submit for proof reading
    """
    obj = getattr(state_change, 'object', None)
    request = getattr(obj, 'REQUEST', None)
    wfsupport = queryMultiAdapter((obj, request), name=u'eea-workflow-support')
    if wfsupport:
        subject = '[EEA CMS] - %s submitted for proof reading'
        return wfsupport(state_change, 'proofreader').sendEmail(subject)

def submitForContentReview(self, state_change, **kw):
    """ Submit for content review
    """
    obj = getattr(state_change, 'object', None)
    request = getattr(obj, 'REQUEST', None)
    wfsupport = queryMultiAdapter((obj, request), name=u'eea-workflow-support')
    if wfsupport:
        subject = '[EEA CMS] - %s submitted for content review'
        return wfsupport(state_change, 'reviewer').sendEmail(subject)

def submitForWebQA(self, state_change, **kw):
    """ Submit for web QA
    """
    obj = getattr(state_change, 'object', None)
    request = getattr(obj, 'REQUEST', None)
    wfsupport = queryMultiAdapter((obj, request), name=u'eea-workflow-support')
    if wfsupport:
        subject = '[EEA CMS] - %s submitted for Web QA'
        return wfsupport(state_change, 'webqa').sendEmail(subject)

def publish(self, state_change, **kw):
    """ Publish
    """
    obj = getattr(state_change, 'object', None)
    request = getattr(obj, 'REQUEST', None)
    wfsupport = queryMultiAdapter((obj, request), name=u'eea-workflow-support')
    if wfsupport:
        subject = '[EEA CMS] - %s published'
        return wfsupport(state_change, '').sendEmail(subject)

def reject(self, state_change, **kw):
    """ Reject
    """
    obj = getattr(state_change, 'object', None)
    request = getattr(obj, 'REQUEST', None)
    wfsupport = queryMultiAdapter((obj, request), name=u'eea-workflow-support')
    if wfsupport:
        subject = '[EEA CMS] - %s sent back for revision'
        wfsupport(state_change, 'owner').sendEmail(subject)

def sendWorkflowEmail(self, state_change, **kw):
    """ Send workflow email
    """
    obj = getattr(state_change, 'object', None)
    request = getattr(obj, 'REQUEST', None)
    wfsupport = queryMultiAdapter((obj, request), name=u'eea-workflow-support')
    if wfsupport:
        wf = wfsupport(state_change, None)
        subject = wf.subject or '[EEA CMS] - workflow changed for %s'
        return wf.sendEmail(subject)
