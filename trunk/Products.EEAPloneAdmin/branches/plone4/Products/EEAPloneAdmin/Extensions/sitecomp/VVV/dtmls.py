""" DTMLs
"""
from Products.EEAPloneAdmin.Extensions.sitecomp.VVV.old_dump import old

dtmls = []

print "Starting\n"

for key in old.keys():
    mytype = old[key]['type']
    if mytype == 'DTML Method':
        dtmls.append(key)

dtmls.sort()
for dtml in dtmls:
    print dtml

print "\nDone!"
