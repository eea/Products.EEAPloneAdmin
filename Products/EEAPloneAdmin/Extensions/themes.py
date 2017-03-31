""" Roll-back themes sync
"""
import os
import csv
import json
from DateTime import DateTime
from zope.component.hooks import getSite
from eea.themecentre.interfaces import IThemeTagging
import logging
logger = logging.getLogger("Products.EEAPloneAdmin")

def rollback(self):
    """ Rollback themes
    """
    site = getSite()
    path = os.environ.get('EEACONVERTER_TEMP')
    path = os.path.join(path, 'roll-back.tsv')
    wf = site.portal_workflow

    res = {}
    with open(path, 'r') as ofile:
        reader = csv.reader(ofile, delimiter='\t')
        for row in reader:
            ptype = row[0]
            if ptype == 'Type':
                continue
            link = row[1]
            old_themes = json.loads(row[2])
            new_themes = json.loads(row[3])
            res[link] = (ptype, old_themes, new_themes)

    count = 0
    ret = []
    for link, val in res.items():
        if val[0] in ['Assessment', 'ExternalDataSpec']:
            continue
        obj = site.unrestrictedTraverse(link)
        old_themes = val[1]
        new_themes = val[2]
        tags = IThemeTagging(obj).tags

        if tags != new_themes:
            logger.warn("SKIP Themes manually changed for %s to %s", link, tags)
            continue

        if tags == old_themes:
            logger.warn("SKIP: Themes manually fixed for %s to %s", link, tags)
            continue

        IThemeTagging(obj).tags = old_themes
        obj.reindexObject(idxs=['getThemes'])
        count += 1

        # Log change to object history
        history = obj.workflow_history
        review_state = wf.getInfoFor(obj, 'review_state', 'None')
        for key in history:
            if 'linguaflow' in key:
                continue
            if 'BKUP' in key:
                continue
            history[key] += ({
                'action': 'Roll-back',
                'actor': 'voineali',
                'comments': (
                    'Rollback themes to "{themes}" from "{new_themes}"'.format(
                        themes=', '.join(old_themes),
                        new_themes=', '.join(new_themes))),
                'review_state': review_state,
                'time': DateTime()
                },)

    for link, val in res.items():
        if val[0] not in ['Assessment', 'ExternalDataSpec']:
            continue
        obj = site.unrestrictedTraverse(link)
        obj.reindexObject(idxs=['getThemes'])
        count += 1

    ret.append(str(count))
    return "\n".join(ret)
