#####################################################################
#
# config        Configuration constants for the LDAPUserFolder
#               package unit tests.
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
#
#####################################################################
__version__='$Revision: 1.1.4.1 $'[11:-2]


eionet = { 'title'  : 'EIONET LDAP User Folder'
           , 'server' : 'ldap.eionet.eu.int'
           , 'port' : '389'
           , 'use_ssl' : 0           
           , 'conn_timeout' : 5
           , 'op_timeout' : 5
           , 'login_attr' : 'uid'
           , 'uid_attr': 'uid'
           , 'users_base' : 'ou=Users, o=EIONET, l=Europe'
           , 'users_scope' : 2
           , 'roles' : 'Anonymous'
           , 'groups_base' : 'ou=groups,dc=dataflake,dc=org'
           , 'groups_scope' : 2
           , 'binduid' : 'cn=Manager,dc=dataflake,dc=org'
           , 'bindpwd' : ''
           , 'binduid_usage' : 0
           , 'rdn_attr' : 'uid'
           , 'local_groups' : 0
           , 'use_ssl' : 0
           , 'encryption' : 'SHA'
           , 'read_only' : 1
           
           }



