""" Dummy exporter
"""

class DummyFilesystemExporter(object):
    """ Dummy filesystem exporter
    """

    def __init__(self, context):
        self.context = context

    def export(self, export_context, subdir, root=False):
        """ Export
        """
        return
