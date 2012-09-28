""" plone.app.content patches
"""
from Acquisition import  aq_inner


def contentsMethod(self):
    """ patched contentMethod to display results in folder_contents for 
        new style collections
    """
    context = aq_inner(self.context)
    if hasattr(context.__class__, 'queryCatalog'):
        contentMethod = context.queryCatalog
    else:
        contentMethod = context.getFolderContents
    return contentMethod
