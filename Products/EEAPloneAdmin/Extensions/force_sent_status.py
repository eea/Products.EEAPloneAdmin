""" Force sent status for newsletters """

def force_sent_status(self):
    """ Force sent status for newsletters """
    newsletters_to_mark = [
    'subscription/eea_main_subscription/water-for-agriculture',
    'subscription/eea_main_subscription/eionet-priority-data-flows-2012',
    'subscription/eea_main_subscription/sahara-dust-sea-spray-and',
    'subscription/eea_main_subscription/ecrins-map-project-pinpoints-water',
    'subscription/eea_main_subscription/noise-handbook',
    'subscription/eea_main_subscription/nitrogen-oxide-emissions-still-a',
    'subscription/eea_main_subscription/reporting-and-exchanging-air-quality',
    'subscription/eea_main_subscription/european-demand-for-goods-and-1'
    ]
    from Products.CMFCore.utils import getToolByName
    cat = getToolByName(self, 'portal_catalog', None)

    res = []

    query = {'path': '/www/SITE/subscription/eea_main_subscription'}

    brains = cat(**query)
    res = [(x.getPath(), x.getObject()) for x in brains]

    for nl in res:
        for ntm in newsletters_to_mark:
            if ntm in nl[0]:
                nl[1].sent_status = True
                nl[1].dateEmitted = nl[1].modification_date

    return "done"

