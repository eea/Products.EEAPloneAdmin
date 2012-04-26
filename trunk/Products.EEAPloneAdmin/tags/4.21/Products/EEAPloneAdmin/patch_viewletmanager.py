""" Pathed to save viewlet order for both skins,
    EEADesignCMS and EEADesign2006, due to #4939
"""
from zope.component import getUtility
from plone.app.viewletmanager.interfaces import IViewletSettingsStorage

def show(self, manager, viewlet):
    """ Pathed to save viewlet order for both skins
    """
    storage = getUtility(IViewletSettingsStorage)
    skinname = self.context.getCurrentSkinName()
    hidden = storage.getHidden(manager, skinname)
    if viewlet in hidden:
        hidden = tuple(x for x in hidden if x != viewlet)
        storage.setHidden(manager, skinname, hidden)

        # The patch is below
        if skinname == 'EEADesignCMS':
            skinname = 'EEADesign2006'
            storage.setHidden(manager, skinname, hidden)

def hide(self, manager, viewlet):
    """ Pathed to save viewlet order for both skins
    """
    storage = getUtility(IViewletSettingsStorage)
    skinname = self.context.getCurrentSkinName()
    hidden = storage.getHidden(manager, skinname)
    if viewlet not in hidden:
        hidden = hidden + (viewlet,)
        storage.setHidden(manager, skinname, hidden)

        # The patch is below
        if skinname == 'EEADesignCMS':
            skinname = 'EEADesign2006'
            storage.setHidden(manager, skinname, hidden)

def moveAbove(self, manager, viewlet, dest):
    """ Pathed to save viewlet order for both skins
    """
    storage = getUtility(IViewletSettingsStorage)
    skinname = self.context.getCurrentSkinName()
    order = self._getOrder(manager)
    viewlet_index = order.index(viewlet)
    del order[viewlet_index]
    dest_index = order.index(dest)
    order.insert(dest_index, viewlet)
    storage.setOrder(manager, skinname, order)

    # The patch is below
    if skinname == 'EEADesignCMS':
        skinname = 'EEADesign2006'
        storage.setOrder(manager, skinname, order)

def moveBelow(self, manager, viewlet, dest):
    """ Pathed to save viewlet order for both skins
    """
    storage = getUtility(IViewletSettingsStorage)
    skinname = self.context.getCurrentSkinName()
    order = self._getOrder(manager)
    viewlet_index = order.index(viewlet)
    del order[viewlet_index]
    dest_index = order.index(dest)
    order.insert(dest_index+1, viewlet)
    storage.setOrder(manager, skinname, order)

    # The patch is below
    if skinname == 'EEADesignCMS':
        skinname = 'EEADesign2006'
        storage.setOrder(manager, skinname, order)
