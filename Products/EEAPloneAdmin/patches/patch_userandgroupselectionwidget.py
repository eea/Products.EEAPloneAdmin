""" A patch for Products.UserAndGroupSelectionWidget
"""
from Products.CMFPlone.utils import getToolByName

def _patched_search_users(self):
    """This patch uses more options when searching for users
    to allow searching for fullname and email, not just username
    """
    st = self.searchabletext
    # BBB: Search is done over all available groups, not only over groups
    # which should be applied. Also see getGroups.
    if len(st) < 3:
        return []
    aclu = getToolByName(self.context, 'acl_users')
    users_dict = (list(aclu.searchUsers(email=st)) +
                  list(aclu.searchUsers(name=st)) +
                  list(aclu.searchUsers(fullname=st)))
    user_ids = [user['id'] for user in users_dict]
    user_ids = set(user_ids)
    return self._getUserDefs(user_ids)
