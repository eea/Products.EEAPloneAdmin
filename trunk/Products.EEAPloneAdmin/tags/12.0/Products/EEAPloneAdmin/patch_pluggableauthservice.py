""" Patching Products.PluggableAuthService not to stuck when listing local
    groups and local roles in ZMI
"""

from Products.PageTemplates.PageTemplateFile import PageTemplateFile


patched_manage_groups = PageTemplateFile('www/zgGroups'
                                        , globals()
                                        , __name__='manage_groups'
                                        )

patched_manage_roles = PageTemplateFile('www/zrRoles'
                                       , globals()
                                       , __name__='manage_roles'
                                       )
