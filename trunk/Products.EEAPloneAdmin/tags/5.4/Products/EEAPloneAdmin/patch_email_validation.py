""" Monkeypatch to check if the result of the address check is not empty
"""
from Products.CMFPlone.PloneTool import EMAIL_CUTOFF_RE
from email.Utils import getaddresses


def validateSingleEmailAddress(self, address):
    """Validate a single email address, see also validateEmailAddresses."""
    if not isinstance(address, basestring):
        return False
    sub = EMAIL_CUTOFF_RE.match(address)
    if sub != None:
        # Address contains two newlines (spammer attack using
        # "address\n\nSpam message")
        return False
    email = getaddresses([address])
    # #5353 check if the tuple has any entries for the address, with a bad
    # email adress it returned a list with this format [("", "")]
    # first entry should have been full name and second if email is correct
    if len(email) != 1 or email[0][1] == "":
        # none or more than one address
        return False

    # Validate the address
    for _, addr in getaddresses([address]):
        if not self.validateSingleNormalizedEmailAddress(addr):
            return False
    return True
