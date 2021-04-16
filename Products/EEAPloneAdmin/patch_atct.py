""" Monkey patches for ATCT
"""
# pylint: disable=W1401

from Acquisition import aq_parent
from Acquisition import aq_inner
from eea.reports.interfaces import IReportContainerEnhanced


# we actually need to replace commas with escaped output without regex
def vformat(s):
    """ Patch ATContentTypes calendarsuport vformat to accept location as tuple
    """
    # return string with escaped commas, colons and semicolons
    # #5284 patch to convert tuple location to string
    if isinstance(s, tuple):
        s = ", ".join(s)

    return s.strip().replace(',', '\,').replace(':', '\:').replace(';', '\;')

def foldLine(s):
    """ Patch ATContentTypes calendarsuport fldLine to accept location as tuple
    """
    # returns string folded per RFC2445 (each line must be less than 75 octets)
    # This code is a minor modification of MakeICS.py, available at:
    # http://www.zope.org/Members/Feneric/MakeICS/
    lineLen = 70
    # #5284 patch to convert tuple location to string
    if isinstance(s, tuple):
        s = ", ".join(s)

    workStr = s.strip().replace('\r\n', '\n').replace('\r', '\n').replace('\n',
                                                                        '\\n')
    numLinesToBeProcessed = len(workStr) / lineLen
    startingChar = 0
    res = ''
    while numLinesToBeProcessed >= 1:
        res = '%s%s\n ' % (res, workStr[startingChar:startingChar + lineLen])
        startingChar += lineLen
        numLinesToBeProcessed -= 1
    return '%s%s\n' % (res, workStr[startingChar:])


def copyLayoutFromParent(self):
    # Copies the layout from the parent object if it's of the same type.
    parent = aq_parent(aq_inner(self))
    if parent is not None:
        # Only set the layout if we are the same type as out parent object
        if parent.meta_type == self.meta_type:
            # If the parent is the same type as us it should implement
            # BrowserDefaultMixin
            parent_layout = parent.getLayout()

            # #127437 dont set layout for Reports, since they both have the
            # same meta_type and portal_type we differentiate them using
            # the report interface
            if IReportContainerEnhanced.providedBy(self) and not \
               IReportContainerEnhanced.providedBy(parent):
                pass
            else:
                # Just in case we should make sure that the layout is
                # available to the new object
                if parent_layout in [l[0] for l in self.getAvailableLayouts()]:
                    self.setLayout(parent_layout)