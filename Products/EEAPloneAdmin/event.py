""" Event
"""
import logging
from lxml.etree import ParserError
from Products.CMFCore.utils import getToolByName
from Products.EEAPloneAdmin.browser.admin import save_resources_on_disk
from DateTime import DateTime
from Products.EEAPloneAdmin.browser.textstatistics import TextStatistics

log = logging.getLogger()

try:
    from eea.versions.utils import object_provides as obj_provides
    has_versions = True
except ImportError:
    has_versions = False

try:
    import lxml
    has_lxml = True
except ImportError:
    has_lxml = False


def handle_resourceregistry_change(obj, event):
    """ Handle resource registry modification
    """
    portal_properties = getToolByName(obj, 'portal_properties')

    site_properties = portal_properties.get('site_properties')
    if not site_properties:
        if getattr(event, 'force', False):
            save_resources_on_disk(obj)
        return

    if not site_properties.getProperty('disableResourceDiskSaving'):
        if getattr(event, 'force', False):
            save_resources_on_disk(obj)


def handle_object_copied(obj, event):
    """ Handle object copy/paste
    """
    obj.creation_date = DateTime()


def handle_object_cloned(obj, event):
    """ Handle object pasted within the final destination
    """
    ptype = obj.portal_type
    # skip changes for CallForInterest since the open and close
    # date properties of the object is populating the expiration
    # and publishing date
    if ptype == "CallForInterest" or ptype == "CallForTender":
        return
    if obj.effective_date:
        obj.setEffectiveDate('None')


def handle_workflow_change(obj, event):
    """ Handle object workflow change and remove effectiveDate
        if the review_state is no longer published
    """
    # 20827 remove effective date from object if review_state is
    # no longer published.
    # This event is triggered also when there is an object clone
    # after the object copied event and before the object is cloned
    # skip changes for CallForInterest since the open and close
    # date properties of the object is populating the expiration
    # and publishing date
    ptype = obj.portal_type
    if ptype == "CallForInterest" or ptype == "CallForTender":
        return
    review_state = event.status['review_state']
    # set effectiveDate to that of the EEAFigure for all EEAFigureFiles
    # when EEAFigure is published 20827
    if review_state == "published":
        parent_date = obj.effective_date
        if ptype == "EEAFigure":
            query = {'portal_type': 'EEAFigureFile'}
            cur_path = '/'.join(obj.getPhysicalPath())
            query['path'] = {'query': cur_path, 'depth': 1}
            figbrains = obj.portal_catalog(query)
            for brain in figbrains:
                figure = brain.getObject()
                figure.setEffectiveDate(parent_date)
    else:
        # 106898 remove effective date only if there is no action set
        # which happens when we create a new version. This way we keep
        # the effective date when setting an effective date in the future
        # and we change to publish at a later time
        if obj.effective_date and not event.status['action']:
            obj.setEffectiveDate('None')


def text_contents(obj):
    """ text content from object's template parsed by lxml """
    try:
        content_core = obj()
    except Exception:
        log.exception('cannot call template for readability on %s',
                      obj.absolute_url(1))
        return ""
    if has_lxml:
        try:
            lcore = lxml.html.fromstring(content_core)
        except ParserError, err:
            log.info("%s %s" % (err, obj.absolute_url()))
            return ""
        scripts = lcore.cssselect('script')
        for script in scripts:
            script.drop_tree()
        content_core = lcore.text_content()
        return content_core
    return ""


def handle_object_modified_for_reading_time(obj, event):
    """ Set reading time statistics after modifying object
    """
    request = getattr(obj, 'REQUEST', [])
    if not request:
        return
    url = obj.absolute_url(1)
    request_url = request.URL0
    if 'portal_factory' in request_url and url in request_url:
        return
    anno = getattr(obj, '__annotations__', {})
    if not anno:
        return
    if not has_versions:
        return
    ptype = obj.portal_type
    if obj_provides(obj,
                    'Products.EEAContentTypes.interfaces.IEEAPossibleContent'):
        if not obj_provides(obj,
                            'Products.EEAContentTypes.interfaces.IEEAContent'):
            if ptype not in ['Document', 'Event', 'Assessment']:
                return
    request['content_core_only'] = True
    content_core = text_contents(obj)
    request['content_core_only'] = False
    if not content_core:
        return
    stats = TextStatistics(content_core)
    score = anno.setdefault('readability_scores', {})
    score['text'] = {
        u'character_count': len(stats.text),
        u'readability_level': stats.flesch_kincaid_grade_level(),
        u'readability_value': stats.flesch_kincaid_reading_ease(),
        u'sentence_count': stats.sentence_count(),
        u'word_count': stats.word_count()
    }
