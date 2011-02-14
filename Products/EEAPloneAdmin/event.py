from App.config import getConfiguration
import os


def handle_resourceregistry_change(obj, event):
    conf = getConfiguration()
    dest = conf.environment['saved_resources']
    if not os.path.exists(dest):
        os.mkdir(dest)
    portal = obj.aq_parent
    for name in obj.concatenatedresources:
        try:
            content = obj.getInlineResource(name, portal)
        except:
            pass

        try:
            f = open(os.path.join(dest, name), "w+")
            f.write(content)
            f.close()
        except IOError:
            pass
