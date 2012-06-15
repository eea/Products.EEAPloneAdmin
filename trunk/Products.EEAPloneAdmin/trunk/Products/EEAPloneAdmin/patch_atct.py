""" Monkey patches for ATCT
"""

from Products.CMFCore.utils import getToolByName

def listSubtopics(self):
    """Return a list of our subtopics.
    """
    val = self.objectValues(self.meta_type)
    check_p = getToolByName(self, 'portal_membership').checkPermission
    tops = []
    for top in val:
        if check_p('View', top):
            tops.append((top.Title().lower(), top))
    tops.sort()
    tops = [t[1] for t in tops]
    return tops


from OFS.Folder import Folder
from Products.ATContentTypes.content.folder import ATFolder, ATBTreeFolder

ATFolder.manage_options = Folder.manage_options
ATBTreeFolder.manage_options = Folder.manage_options


def vformat(s):
    """ Patch ATContentTypes calendarsuport vformat to accept location as tuple
    """
    # return string with escaped commas, colons and semicolons
    # #5284 patch to convert tuple location to string
    if type(s) == tuple:
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
    if type(s) == tuple:
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
