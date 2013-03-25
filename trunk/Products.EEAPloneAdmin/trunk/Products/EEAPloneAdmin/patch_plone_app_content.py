""" plone.app.content patches
"""
from Acquisition import  aq_inner

def contentsMethod(self):
    """ #5533 backported contentMethod from plone.app.content 2.1a1 to display
        results in folder_contents for new style collections
        old code
        context = aq_inner(self.context)
        if IATTopic.providedBy(context):
            contentsMethod = context.queryCatalog
        else:
            contentsMethod = context.getFolderContents
        return contentsMethod
    """
    context = aq_inner(self.context)
    if hasattr(context.__class__, 'queryCatalog'):
        contentMethod = context.queryCatalog
    else:
        contentMethod = context.getFolderContents
    return contentMethod
