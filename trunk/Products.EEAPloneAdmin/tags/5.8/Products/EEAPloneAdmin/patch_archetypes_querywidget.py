""" Archetypes.querywidget patches
"""
from archetypes.querywidget.views import WidgetTraverse


class MultiSelectWidget(WidgetTraverse):
    """ MultiSelectWidget class
    """

    def getValues(self, index=None):
        """ Retrieve values
        """
        config = self.getConfig()
        if not index:
            index = self.request.form.get('index')
        values = None
        if index is not None:
            values = config['indexes'][index]['values']
        return values

    def getSortedValuesKeys(self, values):
        """ patch method which sorts the values keys
        """
        # do a lowercase sort of the keys
        return sorted(values.iterkeys(), key = lambda x : x.lower())
