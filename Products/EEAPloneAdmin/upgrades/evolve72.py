""" Upgrade steps for 7.2
"""


def cleanupBrokenP4AObjects(self):
    """ uncatalog broken p4a objects
    """
    catalog = self.context.portal_catalog
    objs = ['/www/portal_factory/HelpCenter/rdfstype/faq',
            '/www/portal_factory/HelpCenter/rdfstype/how-to',
            '/www/portal_factory/HelpCenter/rdfstype/tutorial',
            '/www/portal_factory/HelpCenter/rdfstype/manual',
            '/www/portal_factory/HelpCenter/rdfstype/error',
            '/www/portal_factory/HelpCenter/rdfstype/link',
            '/www/portal_factory/HelpCenter/rdfstype/glossary']
    for obj in objs:
        catalog.uncatalog_object(obj)
    return "DONE with removal of %s" % objs

