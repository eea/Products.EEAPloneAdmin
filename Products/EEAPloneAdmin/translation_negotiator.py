""" Override user interface language setting and setting it to english.
    See #14087 for details
    This code is derived from Silvuple
    https://github.com/miohtama/silvuple.git
"""
import logging

from Products.CMFCore.interfaces import IContentish, IFolderish
from zope.component import getMultiAdapter
from zope.i18n.translationdomain import TranslationDomain

# W0703:105,11:_patched_translate: Catching too general exception Exception
# pylint: disable=W0703

logger = logging.getLogger("Products.EEAPloneAdmin.negotiation")


def find_context(request):
    """ Find the context from the request
    """
    published = request.get('PUBLISHED', None)
    context = getattr(published, '__parent__', None)
    if context is None:
        # tests lack parents attribute a lot of times
        if not request.get('PARENTS'):
            return None
        context = request.PARENTS[0]
    return context


def get_editor_language(request):
    """ Get editor language override
    """

    cached = getattr(request, "_cached_admin_language", None)
    if cached:
        return cached

    alwaysTranslate = getattr(request, "alwaysTranslate", None)
    if alwaysTranslate:
        return None

    context = find_context(request)

    # Filter out CSS and other non-sense
    # IFolderish check includes site root
    if not (IContentish.providedBy(context) or IFolderish.providedBy(context)):
        # Early terminate
        return None

    # Check if we are the editor
    portal_state = getMultiAdapter((context, request),
                                                    name="plone_portal_state")
    if portal_state.anonymous():
        # Anon visitor, normal language ->
        request.alwaysTranslate = True
        return None

    language = 'en'

    # english for all authenticated users
    request._cached_admin_language = language
    return language


_unpatched_translate = None


def _patched_translate(self, msgid, mapping=None, context=None,
                  target_language=None, default=None):
    """ TranslatioDomain.translate() patched for editor language support

    :param context: HTTPRequest object
    """
    # return unpatched translation if no context is present ( happened with
    # comments )

    alwaysTranslate = mapping.pop('alwaysTranslate', None) if mapping else None
    if not context or alwaysTranslate:
        return _unpatched_translate(self, msgid, mapping, context,
                                    target_language, default)
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

_unpatched_translate = TranslationDomain.translate
TranslationDomain.translate = _patched_translate
