import csv
import logging
from StringIO import StringIO
from eea.app.visualization.converter.csvutils import UnicodeWriter
logger = logging.getLogger("climate")
from pprint import pprint

def no_topic(self):
  brains = self(Language='all')
  no_topic = {}
  ofile = StringIO()

#  self.REQUEST.RESPONSE.setHeader('Content-Type', 'application/tsv')
#  self.REQUEST.RESPONSE.setHeader('Content-Disposition', 'attachment; filename="no_topics.tsv')

  cfile = open('/tmp/no_topics3.tsv', 'w')
  writer = csv.writer(cfile, delimiter='\t')
  writer.writerow(["Content Type", "URL", "Title", "Current Topics", "Publishing date", 'State', 'Language'])
  total = len(brains)
  for idx, brain in enumerate(brains):
    if brain.getThemes:
      continue

    if brain.portal_type in ['Discussion Item', 'File', 'Image', 'Term', 'Folder', 'TreeVocabularyTerm', 'SimpleVocabularyTerm', 'SimpleVocabulary', 'Topic']:
      continue

    if idx % 10000 == 0:
      print "Progress: %s/%s" % (idx, total)

    title = brain.Title
    try:
      writer.writerow([
        brain.portal_type,
        brain.getURL(),
        title,
        brain.getThemes,
        brain.effective.asdatetime().isoformat(),
        brain.review_state,
        brain.Language
      ])
    except Exception as err:
      writer.writerow([
        brain.portal_type,
        brain.getURL(),
        '',
        brain.getThemes,
        brain.effective.asdatetime().isoformat(),
        brain.review_state,
        brain.Language
      ])
  return 'Done. See /tmp/no_topics.tsv'

def climate(self):
  brains = self(Language='all', show_inactive=False)

  versions = {}
  errors = {}

  total = len(brains)
  for idx, brain in enumerate(brains):
    if idx % 10000 == 0:
      logger.info("Extracting progress: %s/%s", idx, total)

    if brain.review_state != 'published':
      continue

    themes = brain.getThemes
    found = False
    try:
      if 'climate' in themes:
        found = True

      if 'climate-change-adaptation' in themes:
        found = True
    except Exception as err:
        if 'Missing.Value' in repr(err):
          continue
        errors[brain.getURL()] = err
        continue

    if not found:
      continue

    vid = brain.getVersionId
    if vid not in versions:
      versions[vid] = brain
      continue

    existing = versions[vid]
    try:
      e_date = max(existing.effective.asdatetime(), existing.created.asdatetime())
    except Exception as err:
      errors[existing.getURL()] = err
      continue

    try:
      b_date = max(brain.effective.asdatetime(), brain.created.asdatetime())
    except Exception as err:
      errors[brain.getURL()] = err
      continue

    if b_date > e_date:
      versions[vid] = brain

  cfile = StringIO()
  writer = csv.writer(cfile, delimiter='\t')
  writer.writerow(["Content Type", "URL", "Title", "Current Topics", "Publishing date", 'State', 'Language'])
  for vid, brain in versions.items():
    writer.writerow([
      brain.portal_type,
      brain.getURL(),
      brain.Title,
      brain.getThemes,
      brain.effective.asdatetime().isoformat(),
      brain.review_state,
      brain.Language
    ])

  print "ERRORS"
  pprint(errors)

  self.REQUEST.RESPONSE.setHeader('Content-Type', 'application/tsv')
  self.REQUEST.RESPONSE.setHeader('Content-Disposition', 'attachment; filename="climate.tsv')

  cfile.seek(0)
  return cfile.read()
