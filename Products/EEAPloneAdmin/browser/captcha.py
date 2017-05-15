""" Override captcha
"""
# Captcha validator

from zope.interface import Interface
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.component import adapts
from plone.app.discussion.borwser import captcha
from Products.EEAPloneAdmin.browser.comments import CommentForm

class CaptchaExtender(captcha.CaptchaExtender):
    """Override plone.app.discussion.browser.captcha CaptchaExtender
    """
    # context, request, form
    adapts(Interface, IDefaultBrowserLayer, CommentForm)
