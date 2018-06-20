""" Correct all absolute links in the portaltab menu. Change only the first
    level,ie: themenu that we see in the blue bar.
"""

def check_navigation(self):
    """find all link with absolute url and change it in a
       relative address
    """
    catalog = self.portal_catalog
    message = ""

    #get list of navigation items, depth 2 from navigation
    data = catalog.unrestrictedSearchResults(
        portal_type='NavigationItem',
        path={'query': '/www/portal_navigationmanager', 'depth': 2})

    for d in data:
        if d.review_state == 'published':
            obj = d.getObject()
            obj_url = obj.getUrl()
            obj_path = obj.getPhysicalPath()
            if ("default" not in obj.getId()) and \
                   ("http" in obj_url) and ("contacts" not in obj_path) and \
                   ("products" not in obj_path) and ("eeahome" not in obj_path):
                message += str('/'.join(obj_path)) + " " + obj_url + " " \
                           + obj_url.replace('https://www.eea.europa.eu', '') \
                           + "\n"
                obj.setUrl(obj_url.replace('https://www.eea.europa.eu', ''))

    return message
