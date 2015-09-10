""" Script to replace smart_view with uberlisting_view
"""
import logging

logger = logging.getLogger("Replaced smart_view for: ")
info = logger.info
info_exception = logger.exception

def clean_smart_view(self):
    """ Replace smart_view with uberlisting for predefined folders
    """
    info("Starting smart_view replacement")
    context = self
    items = ['/www/SITE/atlas/teeb', '/www/SITE/code/gis/esri-api-examples',
    '/www/SITE/themes/biodiversity/document-library/natura-2000',
    '/www/SITE/themes/biodiversity/document-library',
    '/www/SITE/themes/water/interactive/soe-wfd',
    '/www/SITE/atlas/eea/eco-tourism/photos',
    '/www/SITE/soer/synthesis/synthesis/key-messages',
    '/www/SITE/soer/europe/understanding-climate-change/key-facts',
    '/www/SITE/soer/europe/understanding-climate-change/key-messages',
    '/www/SITE/soer/europe/mitigating-climate-change/key-facts',
    '/www/SITE/soer/europe/mitigating-climate-change/key-messages',
    '/www/SITE/soer/europe/adapting-to-climate-change/key-facts',
    '/www/SITE/soer/europe/adapting-to-climate-change/key-messages',
    '/www/SITE/soer/europe/biodiversity/key-facts',
    '/www/SITE/soer/europe/biodiversity/key-messages',
    '/www/SITE/soer/europe/land-use/key-facts',
    '/www/SITE/soer/europe/land-use/key-messages',
    '/www/SITE/soer/europe/marine-and-coastal-environment/key-messages',
    '/www/SITE/soer/europe/marine-and-coastal-environment/key-facts',
    '/www/SITE/soer/europe/consumption-and-environment/key-facts',
    '/www/SITE/soer/europe/consumption-and-environment/key-messages',
    '/www/SITE/soer/europe/material-resources-and-waste/key-facts',
    '/www/SITE/soer/europe/material-resources-and-waste/key-messages',
    '/www/SITE/soer/europe/water-resources-quantity-and-flows/key-facts',
    '/www/SITE/soer/europe/water-resources-quantity-and-flows/key-messages',
    '/www/SITE/soer/europe/freshwater-quality/key-facts',
    '/www/SITE/soer/europe/freshwater-quality/key-messages',
    '/www/SITE/soer/europe/air-pollution/key-facts',
    '/www/SITE/soer/europe/air-pollution/key-messages',
    '/www/SITE/soer/europe/urban-environment/key-messages',
    '/www/SITE/soer/europe/urban-environment/key-facts',
    '/www/SITE/code/gis/mapfish-api-examples',
    '/www/SITE/code/gis/google-maps-api',
    '/www/SITE/atlas/eea',
    '/www/SITE/cooperations',
    '/www/SITE/about-us/governance/scientific-committee/sc-opinions/opinions'\
                                                    '-on-scientific-issues',
    '/www/SITE/code/gis/microsoft-bing-map-examples',
    '/www/SITE/themes/biodiversity/document-library/natura-2000/reporting'\
                                                '-guidelines-for-natura-2000']
    for item in items:
        found = context.unrestrictedTraverse(item)
        found.setLayout('uberlisting_view')
        info("%s", item)
    info("Done")
