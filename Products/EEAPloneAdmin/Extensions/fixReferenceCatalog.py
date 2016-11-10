""" Fix broken brains within reference_catalog
"""
import logging
logger = logging.getLogger('EEAPloneAdmin')


PATHS = [
    "SITE/help/infocentre/enquiries/requestors/fdb06e80ffb131628aedf0d5774a6c6b/at_references/19ffcf40135b1c0b710cab5240f860d4",
    "SITE/help/infocentre/enquiries/fdb06e80ffb131628aedf0d5774a6c6b/at_references/ff7be27758ec906d544ed2d6e7e6869d",
    "SITE/data-and-maps/figures/projected-ocean-acidification-by-2100/at_references/dc436b6f037fdae33fc37bf70428601b",
    "SITE/data-and-maps/figures/emissions-of-selected-air-pollutants/at_references/6ab9723c2ce108dcc6f60b194a4f2d8a",
    "SITE/data-and-maps/figures/methane-emissions-as-a-result/at_references/8ecbace4b04aa9db0a2cb875f72ce249",
    "SITE/data-and-maps/figures/environmental-agreements-since-1900/at_references/f1cd101f1548d4284cb5c7920c2d61d8",
    "SITE/data-and-maps/figures/land-cover-classes-in-the-1/at_references/faf774959bea78f7d81ca3fa0271a924",
    "SITE/data-and-maps/indicators/transport-emissions-of-greenhouse-gases/at_references/48d2d0f590745961736f6a1b605b84ca",
    "SITE/data-and-maps/indicators/transport-emissions-of-greenhouse-gases/at_references/f6de92a3bd47518bddbe553a8401b839",
    "SITE/data-and-maps/indicators/transport-emissions-of-greenhouse-gases/at_references/e98a3f3b9f2dc99d19452a74d910685c",
    "SITE/data-and-maps/figures/annex-i-habitat-distribution-across-massifs/at_references/641074fcd236cee1d271d66e2d710630",
    "SITE/data-and-maps/figures/annex-i-habitat-distribution-across-massifs/at_references/2b286ab88cb4fbcd111bfad71daf365f",
    "SITE/data-and-maps/figures/proportion-of-area-of-classes/at_references/e71234f2bb94ac34e1ebe0dc67398892",
    "SITE/data-and-maps/figures/contributions-to-eu-emissions-from-1/at_references/c3ced0fe7fad4c8dbb692d7f4f89f983",
    "es/senales/senales-2013/articulos/calidad-del-aire-en-lugares-cerrados/at_references/4032eca699f84016a0f76e1187ab6e10",
    "es/senales/senales-2013/articulos/cada-vez-que-respiramos/at_references/3e5090717b1f49a1819e7230e3864c17",
    "hr/signals/signals-2013/zatvoriti/prikaz-kolicina-aerosola-u-svijetu-1/at_references/cf9a1448b2ab4a1cbdf6b087d936bc55",
    "hr/signals/signals-2013/razgovor/stvar-kemije/at_references/d64e87db31904440840d9d94e35b8933",
    "SITE/themes/biodiversity/biodiversity-monitoring-through-citizen-science/how-is-it-being-used/how-is-it-being-used/at_references/2d72a39d48b149d58594fc4c57e84b8f",
    "SITE/themes/biodiversity/biodiversity-monitoring-through-citizen-science/how-is-it-being-used/how-is-it-being-used/at_references/a866db44b2c14b4daff5d0a19f4b6ea5",
    "SITE/themes/biodiversity/biodiversity-monitoring-through-citizen-science/how-is-it-being-used/how-is-it-being-used/at_references/7b163c18dce7490da52fb4e0693714c0",
]


def reindex(self):
    """ Reindex
    """
    catalog = self.reference_catalog
    site = catalog.portal_url.getPortalObject()

    for path in PATHS:
        try:
            catalog.uncatalog_object(path)
        except Exception, err:
            logger.warn(path)
            logger.exception(err)

        try:
            obj = site.restrictedTraverse('/www/' + path)
        except Exception, err:
            logger.warn(path)
            logger.exception(err)
            continue

        try:
            catalog.catalog_object(obj, uid=path)
        except Exception, err:
            logger.warn(path)
            logger.exception(err)

    return 'Done'
