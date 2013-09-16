from eea.versions.versions import assign_new_version_id
import transaction

def fix_versionids(context):
    catalog = context.portal_catalog
    brains = catalog.searchResults(missing=True, Language="all")

    i = 0
    for brain in brains:
        if not brain.getVersionId:
            obj = brain.getObject()
            assign_new_version_id(obj, event=None)
            obj.reindexObject(idxs=['getVersionId'])

        i += 1
        if i % 100 == 0:
            transaction.savepoint()

    return "Done"

