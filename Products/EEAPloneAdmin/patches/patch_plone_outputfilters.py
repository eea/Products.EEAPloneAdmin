""" Patch due to #4832
"""
from inspect import ismethod

def patched_resolve_image(self, src):
    """ Patched because of bug in code in plone
    """
    image, fullimage, src, description = self._old_resolve_image(src)

    #PATCH:start of code change
    # #94537 if the user copies the url from the browser and inserts
    # that in tinymce as 'external', image is at this point a method,
    # so we need to get the real image
    if ismethod(image):
        image = image.__self__

        url = image.absolute_url()
        if isinstance(url, unicode):
            url = url.encode('utf8')

        appendix = self.resolve_link(src)[2]
        if isinstance(appendix, unicode):
            appendix = appendix.encode('utf8')

        src = url + appendix

    # 70194 image scales have unicode names and path should be normal
    # strings otherwise we will get errors when editors use relative
    # path for images
    #PATCH: end of code change
    return image, fullimage, src, description
