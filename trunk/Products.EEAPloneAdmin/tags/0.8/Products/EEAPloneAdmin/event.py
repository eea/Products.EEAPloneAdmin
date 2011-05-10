from Products.EEAPloneAdmin.browser.admin import save_resources_on_disk

def handle_resourceregistry_change(obj, event):
    save_resources_on_disk(obj)
