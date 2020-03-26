""" Patch Products.ZCTextIndex ver >= 2.13.5:
        - unindex doc;
"""
import logging
from BTrees.Length import Length
from Products.ZCTextIndex.BaseIndex import unique

logger = logging.getLogger('Prodcuts.EEAPloneAdmin')

def unindex_doc(self, docid):
    for wid in unique(self.get_words(docid)):
        try:
            self._del_wordinfo(wid, docid)
        except:
            logger.error("Failed to delete index entry with wid: %s and docid: %s" % (wid, docid))
            continue
    del self._docwords[docid]
    del self._docweight[docid]
    try:
        self.document_count.change(-1)
    except AttributeError:
        # Upgrade document_count to Length object
        self.document_count = Length(self.document_count())