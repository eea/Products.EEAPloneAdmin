""" Patch plone.app.discussion ver >= 2.0.10: 
        - not to fail on migrate workflows when "Discussion Item" has no 
          workflow assigned;
        - migration script;
        - allow comments on folderish objects
"""
import plone.app.discussion.browser.controlpanel
from Products.CMFCore.utils import getToolByName
from zope.app.component.hooks import getSite
from plone.registry.interfaces import IRecordModifiedEvent
from plone.app.controlpanel.interfaces import IConfigurationChangedEvent
from zope.component import queryUtility
from plone.app.discussion.interfaces import IDiscussionSettings
from plone.registry.interfaces import IRegistry

from Acquisition import aq_base
from Acquisition import aq_chain
from Acquisition import aq_inner, aq_parent
from Products.CMFCore.interfaces import IFolderish
from Products.CMFCore.interfaces._content import IDiscussionResponse
from Products.CMFPlone.interfaces import INonStructuralFolder
from Products.CMFPlone.interfaces import IPloneSiteRoot
from plone.app.discussion.browser.migration import DT2dt
from plone.app.discussion.comment import CommentFactory
from plone.app.discussion.interfaces import IConversation, IReplies, IComment
import transaction

def notify_configuration_changed(event):
    """Event subscriber that is called every time the configuration changed.
    """
    portal = getSite()
    wftool = getToolByName(portal, 'portal_workflow', None)

    if IRecordModifiedEvent.providedBy(event):
        # Discussion control panel setting changed
        if event.record.fieldName == 'moderation_enabled':
            # Moderation enabled has changed
            if event.record.value == True:
                # Enable moderation workflow
                wftool.setChainForPortalTypes(('Discussion Item',),
                                              'comment_review_workflow')
            else:
                # Disable moderation workflow
                wftool.setChainForPortalTypes(('Discussion Item',),
                                              'one_state_workflow')

    if IConfigurationChangedEvent.providedBy(event):
        # Types control panel setting changed
        if 'workflow' in event.data:
            registry = queryUtility(IRegistry)
            settings = registry.forInterface(IDiscussionSettings, check=False)

            # Patch
            wf = wftool.getChainForPortalType('Discussion Item')
            if wf:
                if wf[0] == 'one_state_workflow':
                    settings.moderation_enabled = False
                elif wf[0] == 'comment_review_workflow':
                    settings.moderation_enabled = True
                else:
                    # Custom workflow
                    pass

plone.app.discussion.browser.controlpanel.notify_configuration_changed = \
                                                notify_configuration_changed


def migrate_discussions(self, filter_callback=None):
    """Migrate discussions"""

    context = aq_inner(self.context)
    out = []
    self.total_comments_migrated = 0
    self.total_comments_deleted = 0

    dry_run = self.request.has_key("dry_run")

    # This is for testing only.
    # Do not use transactions during a test.
    test = self.request.has_key("test")

    if not test:
        transaction.begin() # pragma: no cover

    catalog = getToolByName(context, 'portal_catalog')

    def log(msg):
        """ log"""
        # encode string before sending it to external world
        if isinstance(msg, unicode):
            msg = msg.encode('utf-8') # pragma: no cover
        context.plone_log(msg)
        out.append(msg)

    def migrate_replies(context, in_reply_to, replies, depth=0, just_delete=0):
        """migrate_replies"""
        # Recursive function to migrate all direct replies
        # of a comment. Returns True if there are no replies to
        # this comment left, and therefore the comment can be removed.
        if len(replies) == 0:
            return True

        for reply in replies:

            # log
            indent = "  "
            for i in range(depth):
                indent += "  "
            log("%smigrate_reply: '%s'." % (indent, reply.title))

            should_migrate = True
            if filter_callback and not filter_callback(reply):
                should_migrate = False
            if just_delete:
                should_migrate = False

            new_in_reply_to = None
            if should_migrate:
                # create a reply object
                comment = CommentFactory()
                comment.title = reply.Title()
                comment.text = reply.cooked_text
                comment.mime_type = 'text/html'
                comment.creator = reply.Creator()

                email = reply.getProperty('email', None)
                if email:
                    comment.author_email = email

                comment.creation_date = DT2dt(reply.creation_date)
                comment.modification_date = DT2dt(reply.modification_date)

                comment.in_reply_to = in_reply_to

                if in_reply_to == 0:
                    # Direct reply to a content object
                    new_in_reply_to = conversation.addComment(comment)
                else:
                    # Reply to another comment
                    comment_to_reply_to = conversation.get(in_reply_to)
                    replies = IReplies(comment_to_reply_to)
                    new_in_reply_to = replies.addComment(comment)

            self.total_comments_migrated += 1

            # migrate all talkbacks of the reply
            talkback = getattr( reply, 'talkback', None )
            no_replies_left = migrate_replies(context,
                                              new_in_reply_to,
                                              talkback.getReplies(),
                                              depth=depth+1,
                                              just_delete=not should_migrate)

            if no_replies_left:
                # remove reply and talkback
                talkback.deleteReply(reply.id)
                obj = aq_parent(talkback)
                obj.talkback = None
                log("%sremove %s" % (indent, reply.id))
                self.total_comments_deleted += 1

        # Return True when all comments on a certain level have been
        # migrated.
        return True

    # Find content
    brains = catalog.searchResults(
        object_provides='Products.CMFCore.interfaces._content.IContentish')
    log("Found %s content objects." % len(brains))

    count_discussion_items = len(catalog.searchResults(
                                     Type='Discussion Item'))
    count_comments_pad = len(catalog.searchResults(
                                 object_provides=IComment.__identifier__))
    count_comments_old = len(catalog.searchResults(
                                 object_provides=IDiscussionResponse.\
                                     __identifier__))

    log("Found %s Discussion Item objects." % count_discussion_items)
    log("Found %s old discussion items." % count_comments_old)
    log("Found %s plone.app.discussion comments." % count_comments_pad)

    log("\n")
    log("Start comment migration.")

    # This loop is necessary to get all contentish objects, but not
    # the Discussion Items. This wouldn't be necessary if the
    # zcatalog would support NOT expressions.
    new_brains = []
    for brain in brains:
        if brain.portal_type != 'Discussion Item':
            new_brains.append(brain)

    # Recursively run through the comment tree and migrate all comments.
    count = 0
    for brain in new_brains:
        try:
            obj = brain.getObject()
        except Exception, err:
            log("Exception while migrating: %s %s" %(brain.getPath(), str(err)))
        talkback = getattr( obj, 'talkback', None )
        if talkback:
            replies = talkback.getReplies()
            if replies:
                conversation = IConversation(obj)
            log("\n")
            log("Migrate '%s' (%s)" % (obj.Title(),
                                       obj.absolute_url(relative=1)))
            migrate_replies(context, 0, replies)
            obj = aq_parent(talkback)
            obj.talkback = None
        count += 1
        if count == 10:
            count = 0
            transaction.commit()

    if self.total_comments_deleted != self.total_comments_migrated:
        log("Something went wrong during migration. The number of \
            migrated comments (%s) differs from the number of deleted \
            comments (%s)." # pragma: no cover
             % (self.total_comments_migrated, self.total_comments_deleted))
        if not test:  # pragma: no cover
            transaction.abort() # pragma: no cover
        log("Abort transaction")  # pragma: no cover

    log("\n")
    log("Comment migration finished.")
    log("\n")

    log("%s of %s comments migrated."
        % (self.total_comments_migrated, count_comments_old))

    if self.total_comments_migrated != count_comments_old:
        log("%s comments could not be migrated."
            % (count_comments_old - self.total_comments_migrated)) 
        log("Please make sure your portal catalog is up-to-date.")

    if dry_run and not test:
        transaction.abort() # pragma: no cover
        log("Dry run") # pragma: no cover
        log("Abort transaction") # pragma: no cover
    if not test:
        transaction.commit() # pragma: no cover
    return '\n'.join(out)


def conversation_enabled(self):
    """ Returns True if discussion is enabled for this conversation.

    This method checks five different settings in order to figure out if
    discussion is enable on a specific content object:

    1) Check if discussion is enabled globally in the plone.app.discussion
       registry/control panel.

    2) Don't check if folderish
       If the current content object is a folder, always return
       False, since we don't allow comments on a folder. This
       setting is used to allow/ disallow comments for all content
       objects inside a folder, not for the folder itself.

    3) Check if the allow_discussion boolean flag on the content object is
       set. If it is set to True or False, return the value. If it set to
       None, try further.

    4) Traverse to a folder with allow_discussion set to either True or
       False. If allow_discussion is not set (None), traverse further until
       we reach the PloneSiteRoot.

    5) Check if discussion is allowed for the content type.
    """
    context = aq_inner(self.context)

    # Fetch discussion registry
    registry = queryUtility(IRegistry)
    settings = registry.forInterface(IDiscussionSettings, check=False)

    # Check if discussion is allowed globally
    if not settings.globally_enabled:
        return False

# Don't chef if folderish
#    # Always return False if object is a folder
#    if (IFolderish.providedBy(context) and
#        not INonStructuralFolder.providedBy(context)):
#        return False

    def traverse_parents(context):
        """traverse parents
        """
        # Run through the aq_chain of obj and check if discussion is
        # enabled in a parent folder.
        for obj in aq_chain(context):
            if not IPloneSiteRoot.providedBy(obj):
                if (IFolderish.providedBy(obj) and
                    not INonStructuralFolder.providedBy(obj)):
                    flag = getattr(obj, 'allow_discussion', None)
                    if flag is not None:
                        return flag
        return None

    # If discussion is disabled for the object, bail out
    obj_flag = getattr(aq_base(context), 'allow_discussion', None)
    if obj_flag is False:
        return False

    # Check if traversal returned a folder with discussion_allowed set
    # to True or False.
    folder_allow_discussion = traverse_parents(context)

    if folder_allow_discussion:
        if not getattr(self, 'allow_discussion', None):
            return True
    else:
        if obj_flag:
            return True

    # Check if discussion is allowed on the content type
    portal_types = getToolByName(self, 'portal_types')
    document_fti = getattr(portal_types, context.portal_type)
    if not document_fti.getProperty('allow_discussion'):
        # If discussion is not allowed on the content type,
        # check if 'allow discussion' is overridden on the content object.
        if not obj_flag:
            return False

    return True
