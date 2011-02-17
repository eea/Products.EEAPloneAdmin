from old_dump import old
from new_dump import new

missed = {}

ignores = ['test','Trash']
excludes = []

from DateTime import DateTime

print "starting"

for key in old.keys():

	path = key.split('/')
	type = old[key]['type']

	# skip top level folders we didn't export
	if path[1] in ignores:
		continue

	# skip if we don't care
	if old[key]['type'] in excludes:
		continue

	# News were put into highlights
	if path[1] == 'news':
		key = key.replace('/news/','/highlights/')

	# EN news releases were renamed:
	if len(path) >= 3:
		if (path[1] == 'documents' and path[2] == 'newsreleases'):
			if key[-3:] == '-en':
				key = key[:-3]		

	# report if missing
	if not new.has_key(key):
		missed[key] = {'type':type}
		#print "%s of type %s not found in new site" % (key, type)
		continue

keys = missed.keys()
keys.sort()
for key in keys:
	print "%s :: %s" % (key, missed[key]['type'])

print "done!"