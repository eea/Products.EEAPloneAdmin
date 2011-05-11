from Products.CMFCore.utils import getToolByName

def publishContent(self,state_change, **kw):
    obj = state_change.object
    portalType = obj.portal_type
    oid = obj.getId()
    if portalType == 'QuickEvent':
        srcFldr = obj.aq_parent
        dstFldr = srcFldr.aq_parent
        objs = srcFldr.manage_cutObjects([oid,])
        dstFldr.manage_pasteObjects(objs)
        new_obj = dstFldr[oid]
        new_obj.setLayout('event_view')
        raise state_change.ObjectMoved(new_obj, new_obj)

        
    
def submitContent(self, state_change, **kw):
    """ DEPRECATED """
    obj = state_change.object
    mhost = self.MailHost
    props = getToolByName(self, 'portal_properties').workflow_properties
    portalType = obj.portal_type.lower()
    defaultEmails = getattr(props, 'default_webqa', ['sasha.vincic@eea.europa.eu'])
    toEmail = list(getattr(props, self.portalType + '_webqa', defaultEmails))
    fromEmail = "%s <%s>" % (self.email_from_name, self.email_from_address)
    
    subject = '[EEA CMS] - %s submitted for review' % portalType
    message = """

    Type: %s
    Titel: %s

    --
    
    To - edit
    Please go to
    %s
    to edit the submitted content. (Log in if needed.)

    Regards
    EEA web team
    """

    #absObjUrl = object.absolute_url()
    objUrl = object.absolute_url(1)
    cmsUrl = getattr(props, 'cms_url', 'https://www-cms.eea.europa.eu/SITE/')
    editUrl = cmsUrl + objUrl + '/edit'
    #publishUrl = cmsUrl + objUrl + '/content_status_modify?workflow_action=publish'
    msg = message % (
          portalType,
          object.Title(),
          editUrl
         )

    return mhost.secureSend(msg, toEmail, fromEmail, subject)
