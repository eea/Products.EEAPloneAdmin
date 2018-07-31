"""Override comments
"""
# -*- coding: utf-8 -*-
from datetime import datetime
from Acquisition import aq_inner

from AccessControl import Unauthorized
from AccessControl import getSecurityManager


from zope.component import createObject, queryUtility

from z3c.form import button

from Products.CMFCore.utils import getToolByName
from Products.statusmessages.interfaces import IStatusMessage

from plone.registry.interfaces import IRegistry


from plone.app.discussion import PloneAppDiscussionMessageFactory as _
from plone.app.discussion.interfaces import IConversation
from plone.app.discussion.interfaces import IReplies
from plone.app.discussion.interfaces import IDiscussionSettings
from plone.app.discussion.interfaces import ICaptcha

from plone.app.discussion.browser.validator import CaptchaValidator



class CommentsViewlet(comments.CommentsViewlet):
    """Override CommentsViewlet
    """
    form = CommentForm
