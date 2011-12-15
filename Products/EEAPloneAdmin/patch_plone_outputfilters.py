""" Patch due to #4832
"""
from zope.app.component.hooks import getSite
from urlparse import urlsplit
from urllib import unquote
from ZODB.POSException import ConflictError
from Acquisition import aq_base, aq_acquire
from zope.publisher.interfaces import NotFound as ztkNotFound
from zExceptions import NotFound


def patched_resolve_image(self, src):
    """ Patched because of bug in code in plone
    """
    description = ''
    if urlsplit(src)[0]:
        # We have a scheme
        return None, None, src, description

    base = self.context
    subpath = src
    appendix = ''

    def traversal_stack(base, path):
        if path.startswith('/'):
            base = getSite()
            path = path[1:]
        obj = base
        stack = [obj]
        components = path.split('/')
        while components:
            child_id = unquote(components.pop(0))
            try:
                if hasattr(aq_base(obj), 'scale'):
                    if components:
                        child = obj.scale(child_id, components.pop())
                    else:
                        child = obj.field(child_id).get(obj.context)
                else:
                    child = obj.restrictedTraverse(child_id)
            except ConflictError:
                raise
            except (AttributeError, KeyError, NotFound, ztkNotFound):
                return
            obj = child
            stack.append(obj)
        return stack

    def traverse_path(base, path):
        stack = traversal_stack(base, path)
        if stack is None:
            return
        return stack[-1]

    obj, subpath, appendix = self.resolve_link(src)
    if obj is not None:
        # resolved uid
        fullimage = obj
        image = traverse_path(fullimage, subpath)
    elif '/@@' in subpath:
        # split on view
        pos = subpath.find('/@@')
        fullimage = traverse_path(base, subpath[:pos])
        if fullimage is None:
            return None, None, src, description
        image = traverse_path(fullimage, subpath[pos+1:])
    else:
        stack = traversal_stack(base, subpath)
        if stack is None:
            return None, None, src, description
        image = stack.pop()
        # if it's a scale, find the full image by traversing one less
        fullimage = image
        stack.reverse()
        for parent in stack:
            if hasattr(aq_base(parent), 'tag'):
                fullimage = parent
                break

    #PATCH:start of code change
    if image is None:
        return None, None, src, description
    #PATCH: end of code change
    src = image.absolute_url() + appendix
    description = aq_acquire(fullimage, 'Description')()
    return image, fullimage, src, description

