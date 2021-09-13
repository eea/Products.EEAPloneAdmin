""" plone.restapi relationfield patches
"""
from zope.component import queryUtility
from Products.CMFCore.utils import getToolByName
import six
from zope.intid.interfaces import IIntIds

from zope.component import getMultiAdapter


def patched_call(self, value):
    obj = None

    if isinstance(value, dict):
        # We are trying to deserialize the output of a serialization
        # which is enhanced, extract it and put it on the loop again
        value = value["@id"]

    if isinstance(value, int):
        # Resolve by intid
        intids = queryUtility(IIntIds)
        obj = intids.queryObject(value)
        resolved_by = "intid"
    elif isinstance(value, six.string_types):
        if six.PY2 and isinstance(value, six.text_type):
            value = value.encode("utf8")
        portal = getMultiAdapter(
            (self.context, self.request), name="plone_portal_state"
        ).portal()

        portal_url = portal.absolute_url()
        if value.startswith(portal_url):
            # Resolve by URL
            obj = portal.restrictedTraverse(value[len(portal_url) + 1:], None)
            resolved_by = "URL"
        elif value.startswith("/"):
            # Resolve by path
            # #134485 patch restricted by path to search from /SITE
            value = '/SITE' + value
            # end patch
            obj = portal.restrictedTraverse(value.lstrip("/"), None)
            resolved_by = "path"
        else:
            # Resolve by UID
            catalog = getToolByName(self.context, "portal_catalog")
            brain = catalog(UID=value)
            if brain:
                obj = brain[0].getObject()
            resolved_by = "UID"

    if obj is None:
        self.request.response.setStatus(400)
        raise ValueError(
            u"Could not resolve object for {}={}".format(resolved_by, value)
        )

    self.field.validate(obj)
    return obj
