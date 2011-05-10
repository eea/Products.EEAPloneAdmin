""" hachoir-core related patches

    Right now the patch is commented in patched.zcml as we cannot duplicate
    anymore.

    The patch is fixed in hachoir-core version 1.3.3

    This patch fixes below error while running tests:
    AttributeError: UnicodeStdout instance has no attribute 'writelines'
"""

def writelines(self, lines):
    """ Add writelines() method to UnicodeStdout
    """
    for text in lines:
        self.write(text)
