""" Remove all relations of translated objects as they are automaticaly 
managed automaticaly, reflecting the canonical object (EN).
"""
import logging
from plone.app.linkintegrity.exceptions import \
    LinkIntegrityNotificationException
from plone.app.linkintegrity.interfaces import ILinkIntegrityInfo
from StringIO import StringIO

# Log info 
logger = logging.getLogger("Delete relations on translations: ")
info = logger.info
info_exception = logger.exception


def clean_relations(self):
    """find translated objects that have relations and remove them
       the loop run recursively until all objects are done
    """

    catalog = self.portal_catalog
    total_objects = 0
    total_relations = 0
    message = ""
    #languages = ['ar','bg','bs','ca','cs','cz','da','de','ee','el',
                 #'es','et','fi','fr','ga','hr','hu','is','it','lt',
                 #'lv','me','mk','mt','nl','no','pl','pt','ro','ru',
                 #'sk','sl','sq','sr','sv','tr','zh']
    languages = ['it']
    
    # Start information log
    info("START")

    for lang in languages:
        num_objects = 0
        num_relation = 0        
        info ("%s" % lang)
        message += "%s\n" % lang
        
        # Get all translated content
        translations = catalog.unrestrictedSearchResults(Language = lang)

        # Take all relations of translations and delete them
        for translation in translations:
            obj = translation._unrestrictedGetObject()
            rel_items = obj.getRelatedItems()
              
            if not rel_items:
                continue

            # Do something:
            obj.setRelatedItems([])
            obj.reindexObject()
        
            message += str(obj.absolute_url())
            message += "\n"
            message +=  str(rel_items)
            message += "\n" 
    
            num_objects += 1
            total_objects += 1
            num_relation += len(rel_items)
            total_relations += len(rel_items)
               
        info("objects %s" % num_objects)
        info("relations %s" % num_relation)
        message += "objects %s\nrelations %s\n" % (num_objects, num_relation)
            
            
    # End information log
    info("Objects updated: %s" % total_objects)  
    info("Relations removed: %s" % total_relations)
    message += "Total Objects: %s / Total Relations: %s" % (total_objects, total_relations)
    info("COMPLETE")

    return message


