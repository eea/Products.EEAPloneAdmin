""" Patch for plone.app.users ver 1.2 to fix roles listing on add user form
    when many roles are available
"""

from zope.interface import Interface
from zope import schema
from plone.app.users.browser.register import AddUserForm, CantSendMailWidget
from plone.app.users.browser.register import IAddUserSchema
from zope.component import getUtility
from Products.CMFCore.interfaces import ISiteRoot
from zope.component import getMultiAdapter
from plone.app.controlpanel.widgets import MultiCheckBoxVocabularyWidget
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFCore.utils import getToolByName
from zope.formlib import form


class IAddUserSchemaNoGroup(Interface):

    groups = schema.List(
        title=_(u'label_add_to_groups',
                default=u'Add to the following groups:'),
        description=u'Disabled: Too many groups to display. Role assignment cand be done after the user is created.',
        required=False,
        value_type=schema.Choice(()))


def get_patched_form_fields(self):
    defaultFields = super(AddUserForm, self).form_fields

    # The mail_me field needs special handling depending on the
    # validate_email property and on the correctness of the mail
    # settings.
    portal = getUtility(ISiteRoot)
    ctrlOverview = getMultiAdapter((portal, self.request),
                                   name='overview-controlpanel')
    mail_settings_correct = not ctrlOverview.mailhost_warning()
    if not mail_settings_correct:
        defaultFields['mail_me'].custom_widget = CantSendMailWidget
    else:
        # Make the password fields optional: either specify a
        # password or mail the user (or both).  The validation
        # will check that at least one of the options is chosen.
        defaultFields['password'].field.required = False
        defaultFields['password_ctl'].field.required = False
        if portal.getProperty('validate_email', True):
            defaultFields['mail_me'].field.default = True
        else:
            defaultFields['mail_me'].field.default = False

    # Append the manager-focused fields
    # patch start
    pprop = getToolByName(self.context, 'portal_properties')
    many_groups = pprop.site_properties.many_groups
    if many_groups:
        allFields = defaultFields + form.Fields(IAddUserSchemaNoGroup)
    else:
        allFields = defaultFields + form.Fields(IAddUserSchema)
    allFields['groups'].custom_widget = MultiCheckBoxVocabularyWidget
    # patch end

    return allFields

patched_form_fields = property(get_patched_form_fields, None)

AddUserForm.form_fields = patched_form_fields
