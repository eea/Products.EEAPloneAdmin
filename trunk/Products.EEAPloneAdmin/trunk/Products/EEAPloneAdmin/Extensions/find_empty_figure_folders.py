"""the problem with the emtpy folders inside figures
is that they are not finished, their _at_creation_flag
is set to True
"""

import transaction

def find(self):
    """find folders that are empty inside EEAFigure objects
    """
    cat = self.portal_catalog
    figures = cat.searchResults({'meta_type': ['EEAFigure']})

    empty = []
    filled = []
    for brain in figures:
        fig = brain.getObject()
        for brain in fig.getFolderContents({'portal_type':'Folder'}):
            folder = brain.getObject()
            empty.append(folder)

            #has_content = len(list(folder.getFolderContents()))
            #if not has_content:
                #empty.append(folder)
            #else:
                #filled.append(folder)

    return empty, filled


def show(self):
    """Run in browser to see problematic folders
    """

    empty = find(self)
    return "\n".join([ "Folder that are empty inside EEAFigures"] + 
                        [o.absolute_url() for o in empty[0]] + 
                     ['Folders that are filled inside eeafigures'] + 
                        [o.absolute_url() for o in empty[1]] 
    )


def fix_1(self):
    """Fix empty folders by properly setting their creation flag
    """

    fix = []
    i = 0
    all = find(self)
    to_fix = all[0] + all[1]

    for o in to_fix:
        fix.append(o.absolute_url())
        o._at_creation_flag = False

        i += 1
        if i % 10 == 0:
            transaction.savepoint()

    return "\n".join(['Fixed creation flag for the following folders'] + fix)
        

def fix_2(self):
    """Fix empty folders by deleting them
    """

    dels = []

    i = 0
    for o in find(self)[0]:
        dels.append(o.absolute_url())
        parent = o.aq_parent
        parent.manage_delObjects(ids=[o.getId()])
        i += 1
        if i % 10 == 0:
            transaction.savepoint()

    return "\n".join(['Deleted the following folders'] + dels)
