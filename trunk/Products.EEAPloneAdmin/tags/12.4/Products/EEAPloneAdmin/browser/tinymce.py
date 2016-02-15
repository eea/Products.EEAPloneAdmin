""" Tiny MCE
"""
from Products.Five import BrowserView

class TinyMCEPatch(BrowserView):
    """ Patch
    """
    def __call__(self):
        self.request.response.setHeader(
            'Content-Type', 'application/x-javascript;charset=utf-8')

        return """
        window.tinyMCEPreInit = {
         base:'%s',
         suffix:'',
         query:''
        };

        """ % self.context.portal_url()

