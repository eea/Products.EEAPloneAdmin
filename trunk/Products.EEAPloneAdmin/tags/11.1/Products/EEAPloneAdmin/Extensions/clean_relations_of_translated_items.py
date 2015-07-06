""" Remove all relations of translated objects as they are automaticaly
    managed automaticaly, reflecting the canonical object (EN).
"""
import logging
import transaction

logger = logging.getLogger("Delete relations on translations: ")
info = logger.info
info_exception = logger.exception

def clean_relations(self):
    """ find translated objects that have relations and remove them
        the loop run recursively until all objects are done
    """
    catalog = self.portal_catalog
    total_objects = 0
    total_relations = 0
    transaction_threshold = 20
    message = ""
    languages = ['ar', 'bg', 'bs', 'ca', 'cs', 'cz', 'da', 'de', 'ee', 'el',
                 'es', 'et', 'fi', 'fr', 'ga', 'hr', 'hu', 'is', 'it', 'lt',
                 'lv', 'me', 'mk', 'mt', 'nl', 'no', 'pl', 'pt', 'ro', 'ru',
                 'sk', 'sl', 'sq', 'sr', 'sv', 'tr', 'zh']
    #languages = ['sq']

    # Start information log
    info("START")

    for lang in languages:
        num_objects = 0
        num_relation = 0
        info("language: %s", lang)
        message += "language: %s\n" % lang

        # Get all translated content
        translations = catalog.unrestrictedSearchResults(Language=lang)

        # Take all relations of translations and delete them
        for translation in translations:
            obj = translation._unrestrictedGetObject()
            rel_items = obj.getRelatedItems()

            # No relations, no party!
            if not rel_items:
                continue

            # We don't check these objects
            if translation.Type in ["Daviz Visualization"]:
                continue

            # Check if the relation is equal to canonical, or his translation:
            canonical = obj.getCanonical()
            rels_canon = canonical.getRelatedItems()
            for relation in rel_items:
                if (relation in rels_canon) or (relation.getTranslation("en")
                                                in rels_canon):
                    continue
                else:
                    info("Warning, relation doesn't match canonical object: "
                         "%s for %s", obj.absolute_url(), str(relation))
                    message += ("Warning, relation doesn't match canonical "
                                "object: " + str(obj.absolute_url()) + "\n")
                    message += "for " + str(relation) + "\n"

            #Remove relations
            obj.setRelatedItems([])
            obj.reindexObject()

            #message += str(obj.absolute_url())
            #message += "\n"
            #message +=  str(rel_items)
            #message += "\n"

            num_objects += 1
            total_objects += 1
            num_relation += len(rel_items)
            total_relations += len(rel_items)

            # Commiting transaction
            if total_objects % transaction_threshold == 0:
                info("Commit: %s objects", transaction_threshold)
                transaction.savepoint()

        info("objects %s", num_objects)
        info("relations %s", num_relation)
        message += "objects %s\nrelations %s\n" % (num_objects, num_relation)

    # Commiting transaction for last items
    info("Commit: %s objects", total_objects % transaction_threshold)
    transaction.savepoint()

    # End information log
    info("Objects updated: %s", total_objects)
    info("Relations removed: %s", total_relations)
    message += "Total Objects: %s / Total Relations: %s" % (total_objects,
                                                            total_relations)
    info("COMPLETE")

    return message
