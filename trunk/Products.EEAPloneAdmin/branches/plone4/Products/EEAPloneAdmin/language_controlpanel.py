from zope.component import adapts

from plone.app.controlpanel.language import LanguageControlPanelAdapter
from Products.ATContentTypes.content.folder import ATFolder

from Products.LinguaPlone.browser.controlpanel import MultiLanguageControlPanelAdapter

class EEALanguageControlPanelAdapter(LanguageControlPanelAdapter):

    adapts(ATFolder)

class EEAMultiLanguageControlPanelAdapter(MultiLanguageControlPanelAdapter):

    adapts(ATFolder)

    def __init__(self, context):
        context = context.aq_inner.aq_parent
        super(MultiLanguageControlPanelAdapter, self).__init__(context)
