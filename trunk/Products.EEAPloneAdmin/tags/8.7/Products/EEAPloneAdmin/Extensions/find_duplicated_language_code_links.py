""" Find Duplicated Language Code links
"""

# DO NOT RUN THIS IN PRODUCTION

from pprint import pprint
from lxml import html
from Products.CMFCore.utils import getToolByName


def find(self):
    """ find portal_types that have a given field and return objects which have
        duplicated language code inside links
    """
    types = getToolByName(self, 'portal_types')
    ctool = getToolByName(self, 'portal_catalog')
    text_objects = set()
    field = self.REQUEST.get('field') or 'text'
    for portal_type in types.objectIds():
        brain = ctool(portal_type=portal_type, sort_limit=1)
        if not brain:
            continue
        obj = brain[0].getObject()
        getField = getattr(obj, 'getField', None)
        if not getField:
            continue
        if obj.getField(field):
            text_objects.add(obj.portal_type)
    pprint(text_objects)

    docs = ctool.searchResults({'portal_type':
     ['Article',
     'CallForInterest',
     'CallForTender',
     'CloudVideo',
     'Collection',
     'CommonalityReport',
     'DiversityReport',
     'Document',
     'EEAVacancy',
     'EcoTip',
     'Event',
     'FlexibilityReport',
     'HelpCenterFAQ',
     'HelpCenterHowTo',
     'Highlight',
     'News Item',
     'PressRelease',
     'Promotion',
     'SOERKeyFact',
     'SOERMessage',
     'Speech',
     'Topic'],
     'Language': 'all'})
    docs = [doc.getObject() for doc in docs]

    queries = ['/da/', '/no/', '/sv/', '/de/', '/lt/', '/cs/', '/nl/',
             '/sl/', '/it/', '/bg/', '/mt/', '/ro/', '/sk/', '/is/', '/hu/',
             '/fi/', '/fr/', '/et/', '/pt/', '/es/', '/pl/', '/tr/', '/el/',
             '/lv/']

    shallow_results = {}

    # get results for object that have language links withing the text field
    for doc in docs:
        raw = doc.getField('text').getRaw(doc)
        for query in queries:
            if query in raw:
                if query not in shallow_results:
                    shallow_results[query] = []
                shallow_results[query].append(doc.absolute_url(1))

    # return objects which have links with repeating language codes
    duplicated_languages = {}
    for query in shallow_results.keys():
        items = shallow_results[query]
        for item in items:
            item = self.restrictedTraverse(item)
            text = item.getText()
            tree = html.fromstring(text)
            links = tree.getiterator('a')
            url = item.absolute_url(1)
            for link in links:
                href = link.attrib.get('href')
                if href:
                    for query in queries:
                        if href.count(query) > 1:
                            if query not in duplicated_languages:
                                duplicated_languages[query] = []
                            if url not in duplicated_languages[query]:
                                duplicated_languages[query].append(url)

    return pprint(duplicated_languages)
