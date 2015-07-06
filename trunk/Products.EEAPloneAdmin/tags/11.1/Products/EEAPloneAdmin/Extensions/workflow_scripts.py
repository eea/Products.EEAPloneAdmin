""" Workflow scripts
"""

from Products.CMFCore.utils import getToolByName

def moveObject(self, state_change, **kw):
    """ Move object
    """
    #ZZZ: ichimdav: i've added these because of unfound vars from line 15,
    #               check if is correct
    news_folder = kw['news_folder']
    highlight_folder = kw['highlight_folder']
    pressrelease_folder = kw['pressrelease_folder']
    # get the object and its ID
    obj = state_change.object
    oid = obj.getId()

    # get the src folder and the destination folder
    config = getToolByName(obj, 'portal_properties').frontpage_properties
    dstFldr = None
    types = (('News Item', news_folder),
             ('Highlight', highlight_folder),
             ('PressRelease', pressrelease_folder))

    for t, folderProp in types:
        if obj.portal_type == t:
            dstFldr = getattr(config, folderProp, None)
            break

    if not dstFldr:
        return

    if not dstFldr.startsWith('/'):
        portal = getToolByName(obj, 'portal_url')
        dstFldr = portal.getPortalObject().getPhysichalPath() + '/' + dstFldr

    dstFldr = obj.unrestrictedTraverse(dstFldr)
    srcFldr = obj.aq_parent

    # perform the move
    objs = srcFldr.manage_cutObjects([oid, ])
    dstFldr.manage_pasteObjects(objs)

    # get the new object
    new_obj = dstFldr[oid]

    # pass new_obj to the error, *twice*
    raise state_change.ObjectMoved(new_obj, new_obj)


def check_selfqa(statechange):
    """Checks if self-qa has been performed.

    This script should be used only for the indicators_workflow,
    the publish transition, as a 'script before'.
    """
    context = statechange.object
    if "Self-QA" in context.REQUEST.form.get("comment", ""):
        return True

    context.plone_utils.addPortalMessage(u'Cannot publish %s from bulk '
                u'publishing. Please publish from '
                u'its viewing page.' % context.Title())

    #There is no middle ground between a "before script" and a guard.
    #Output from beforescript is not checked to see if transition should
    #continue as it's expected that guards should take care of that problem.

    raise ValueError
