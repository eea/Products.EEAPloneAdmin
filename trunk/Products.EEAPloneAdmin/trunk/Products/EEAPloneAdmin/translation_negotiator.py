""" Override user interface language setting and setting it to english.
    See #14087 for details
"""

# W0703:105,11:_patched_translate: Catching too general exception Exception
# pylint: disable-msg=W0703

import logging

from AccessControl import getSecurityManager
from Products.CMFCore import permissions
from Products.CMFCore.interfaces import IContentish, IFolderish


logger = logging.getLogger("Products.EEAPloneAdmin.negotiation")


def find_context(request):
    """ Find the context from the request
    """
    published = request.get('PUBLISHED', None)
    context = getattr(published, '__parent__', None)
    if context is None:
        context = request.PARENTS[0]
    return context


def get_editor_language(request):
    """ Get editor language override
    """

    cached = getattr(request, "_cached_admin_language", None)
    if cached:
        return cached

    context = find_context(request)

    # Filter out CSS and other non-sense
    # IFolderish check includes site root
    if not (IContentish.providedBy(context) or IFolderish.providedBy(context)):
        # Early terminate
        return None

    # Check if we are the editor
    if not getSecurityManager().checkPermission(permissions.ModifyPortalContent,
                                                                    context):
        # Anon visitor, normal language ->
        return None

    language = 'en'

    # Fake new language for all authenticated users
    request._cached_admin_language = language
    return language


_unpatched_translate = None


def _patched_translate(self, msgid, mapping=None, context=None,
                  target_language=None, default=None):
    """ TranslatioDomain.translate() patched for editor language support

    :param context: HTTPRequest object
    """
    try:
        language = get_editor_language(context)
        if language:
            target_language = language
    except Exception as e:
        # Some defensive programming here
        logger.error("Admin language force patch failed")
        logger.exception(e)

    return _unpatched_translate(self, msgid, mapping, context, target_language,
                                                                        default)

from zope.i18n.translationdomain import TranslationDomain
_unpatched_translate = TranslationDomain.translate
TranslationDomain.translate = _patched_translate
