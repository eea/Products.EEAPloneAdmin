"""Override comments
"""
# -*- coding: utf-8 -*-
from Acquisition import aq_inner

from AccessControl import Unauthorized
from AccessControl import getSecurityManager

from datetime import datetime

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

from plone.app.discussion.browser import comments
class CommentForm(comments.CommentForm):
    """Override CommentForm
    """
    @button.buttonAndHandler(_(u"add_comment_button", default=u"Comment"),
                             name='comment')
    def handleComment(self, action):
        """Override handleComment
        """
        context = aq_inner(self.context)

        # Check if conversation is enabled on this content object
        if not self.__parent__.restrictedTraverse(
            '@@conversation_view').enabled():
            raise Unauthorized("Discussion is not enabled for this content "
                               "object.")

        # Validation form
        data, errors = self.extractData()
        if errors:
            return

        # Validate Captcha
        registry = queryUtility(IRegistry)
        settings = registry.forInterface(IDiscussionSettings, check=False)
        portal_membership = getToolByName(self.context, 'portal_membership')
        if settings.captcha != 'disabled' and \
        settings.anonymous_comments and \
        portal_membership.isAnonymousUser():
            if not 'captcha' in data:
                data['captcha'] = u""
            captcha = CaptchaValidator(self.context,
                                       self.request,
                                       None,
                                       ICaptcha['captcha'],
                                       None)
            captcha.validate(data['captcha'])

        # some attributes are not always set
        author_name = u""
#        author_email = u""
#        user_notification = None

        # Create comment
        comment = createObject('plone.Comment')
        # Set comment attributes (including extended comment form attributes)
        for attribute in self.fields.keys():
            setattr(comment, attribute, data[attribute])
        # Make sure author_name is properly encoded
        if 'author_name' in data:
            author_name = data['author_name']
            if isinstance(author_name, str):
                author_name = unicode(author_name, 'utf-8')

        # Set comment author properties for anonymous users or members
        can_reply = getSecurityManager().checkPermission('Reply to item',
                                                         context)
        portal_membership = getToolByName(self.context, 'portal_membership')
        if portal_membership.isAnonymousUser() and \
           settings.anonymous_comments:
            # Anonymous Users
            comment.creator = author_name
            comment.author_name = author_name
#            comment.author_email = author_email
#            comment.user_notification = user_notification
            comment.creation_date = datetime.utcnow()
            comment.modification_date = datetime.utcnow()
        elif not portal_membership.isAnonymousUser() and can_reply:
            # Member
            member = portal_membership.getAuthenticatedMember()
            username = member.getUserName()
            email = member.getProperty('email')
            fullname = member.getProperty('fullname')
            if not fullname or fullname == '':
                fullname = member.getUserName()
            # memberdata is stored as utf-8 encoded strings
            elif isinstance(fullname, str):
                fullname = unicode(fullname, 'utf-8')
            if email and isinstance(email, str):
                email = unicode(email, 'utf-8')
            comment.creator = fullname
            comment.author_username = username
            comment.author_name = fullname
            comment.author_email = email
#            comment.user_notification = user_notification
            comment.creation_date = datetime.utcnow()
            comment.modification_date = datetime.utcnow()
        else:  # pragma: no cover
            raise Unauthorized("Anonymous user tries to post a comment, but "
                "anonymous commenting is disabled. Or user does not have the "
                "'reply to item' permission.")

        # Add comment to conversation
        conversation = IConversation(self.__parent__)
        if data['in_reply_to']:
            # Add a reply to an existing comment
            conversation_to_reply_to = conversation.get(data['in_reply_to'])
            replies = IReplies(conversation_to_reply_to)
            comment_id = replies.addComment(comment)
        else:
            # Add a comment to the conversation
            comment_id = conversation.addComment(comment)

        # Redirect after form submit:
        # If a user posts a comment and moderation is enabled, a message is
        # shown to the user that his/her comment awaits moderation. If the user
        # has 'review comments' permission, he/she is redirected directly
        # to the comment.
        can_review = getSecurityManager().checkPermission('Review comments',
                                                          context)
        workflowTool = getToolByName(context, 'portal_workflow')
        comment_review_state = workflowTool.getInfoFor(comment, 'review_state')
        if comment_review_state == 'pending' and not can_review:
            # Show info message when comment moderation is enabled
            IStatusMessage(self.context.REQUEST).addStatusMessage(
                _("Your comment awaits moderator approval."),
                type="info")
            self.request.response.redirect(self.action)
        else:
            # Redirect to comment (inside a content object page)
            self.request.response.redirect(self.action + '#' + str(comment_id))

    @button.buttonAndHandler(_(u"Cancel"))
    def handleCancel(self, action):
        """handleCancel
        """
        # This method should never be called, it's only there to show
        # a cancel button that is handled by a jQuery method.
        pass  # pragma: no cover


class CommentsViewlet(comments.CommentsViewlet):
    """Override CommentsViewlet
    """
    form = CommentForm
