from old_dump import old
from DateTime import DateTime

dtmls = []

print "Starting\n"

for key in old.keys():

	type = old[key]['type']

	if type == 'DTML Method':
		dtmls.append(key)

dtmls.sort()
for dtml in dtmls:
	print dtml

print "\nDone!"