"""CDN Enhancements

We want to be able to output merged resources based on URL parameters
"""

from Products.ResourceRegistries.browser.kss import KSSView as BaseKSSView
from Products.ResourceRegistries.browser.scripts import ScriptsView as BaseScriptsView
from Products.ResourceRegistries.browser.styles import StylesView as BaseStylesView
from collective.cdn.core.browser.base import BaseRegistryView
from Products.Five import BrowserView
from StringIO import StringIO
import logging

logger = logging.getLogger("Products.EEAPloneAdmin")


def chunks(l, n):
    """ Yield successive n-sized chunks from l.
    """
    for i in xrange(0, len(l), n):
        yield l[i:i+n]

def getDevelMode():
    """Are we running in development mode?"""
    import Globals 
    return bool(Globals.DevelopmentMode)


# Adapted from collective.cdn.multiplehostnames/provider.py
def process_url(url, hosts, index):
    '''Given a base url we return an url pointing to 
       the hostname and path informed
    '''
    # splits url parts
    if index >= len(hosts):  #this is the spillover from chunking
        index = 0
    protocol, path = url.split('://')
    slash = path.find('/')
    original_host, path = path[:slash], path[slash:]

    if not getDevelMode():
        host = hosts[index]
    else:
        host = original_host
    
    # join everything
    url = '%s://%s/%s' % (protocol, host, path)
    return url


def process(resources, hosts, marker):
    # We try to fit all the files into exactly one per cdn host
    split_size = len(hosts)
    chunk_size = int(len(resources)/split_size)

    #result is a list like this:
     #[{'conditionalcomment': 'IE 9',
      #'media': 'screen',
      #'rel': 'stylesheet',
      #'rendering': 'link',
      #'src': u'http://static2/localhost/www/portal_css/
      #                               EEADesign2006/IE9Fixes.css',
      #'title': None}]
    out = []
    batches = chunks(resources, chunk_size)   #concatenate 6 files

    for index, batch in enumerate(batches):
        first = batch[0].copy()
        start = first['src'].find(marker)
        base_url = first['src'][:start] + marker + "@@merge"
        s = []
        for l in batch:
            res_id = l['src'][start+len(marker):]
            s.append(res_id)    #strip slashes
        url = base_url + "?r=" + s[0]
        if len(s) > 1:
         url += "&r=" + "&r=".join(s[1:])
        first['src'] = process_url(url, hosts, index)
        out.append(first)

    return out


class ScriptsView(BaseScriptsView, BaseRegistryView):
    """Override css view to merge results """

    registry_id = 'portal_javascripts'
    cdn_enable_prop = 'enable_cdn_js'

    def scripts(self):
        """scripts
        """
        result = BaseScriptsView.scripts(self)

        if not self.use_cdn:
            return result

        cdn   = self.cdn_provider()
        hosts = cdn.hostname

        return process(result, hosts, marker=self.registry_id + "/")


class StylesView(BaseStylesView, BaseRegistryView):
    """Override css view to merge results """

    registry_id = 'portal_css'
    cdn_enable_prop = 'enable_cdn_css'

    def styles(self):
        """styles
        """
        result = BaseStylesView.styles(self)

        if not self.use_cdn:
            return result

        cdn   = self.cdn_provider()
        hosts = cdn.hostname

        return process(result, hosts, marker=self.registry_id + "/")


class KSSView(BaseKSSView, BaseRegistryView):
    """Override kss view to merge results """

    registry_id = 'portal_kss'
    cdn_enable_prop = 'enable_cdn_kss'

    def kineticstylesheets(self):
        """kss
        """
        result = BaseKSSView.kineticstylesheets(self)

        if not self.use_cdn:
            return result

        cdn   = self.cdn_provider()
        hosts = cdn.hostname

        return process(result, hosts, marker=self.registry_id+'/')


class MergeResources(BrowserView):
    def __call__(self):
        ids = self.request.form.get('r')
        registry = self.context
    
        out = StringIO()
        for id in ids:
            skin, name = id[:id.find('/')], id[id.find('/')+1:]
            name = name.replace(' ', '+')
            try:    #this is the same code used to save resources on disk
                content = registry.getResourceContent(name, 
                                            context=registry, theme=skin)
                out.write(content)
            except TypeError:
                continue    #old merged resource
            except (KeyError, AttributeError, AssertionError), e:
                if not str(e).strip():   #on empty error, content is saved
                    continue
                #this is for DTML base_properties problem
                logger.warning("Could not generate content "
                                "for %s in skin %s because: %s" % 
                                    (name, skin, e))

        out.seek(0)
        return out.read()
