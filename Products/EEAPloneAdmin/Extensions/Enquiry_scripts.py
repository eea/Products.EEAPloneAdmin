""" Workflow Scripts for: Enquiry
"""
import quopri
from plone import api
import transaction
import logging

enquiryTemplate = """From: %s
To: %s
Errors-to: %s
Subject: %s
Content-Type: text/plain; charset=utf-8
Content-Transfer-Encoding: 8bit

%s

<Type of requester: %s>
<Purpose: %s>"""

def sendToIC(self, state_change, **kw):
    """ Send to IC
    """
    enq = state_change.object
    portal = enq.portal_url.getPortalObject()
    question = enq.Description().replace('\r', '')
    subject = "=?%s?q?%s?=" % ('utf-8', quopri.encodestring(enq.Title()))

    content = enquiryTemplate % (enq.getEmail(),
                                 portal.enquiry_email,
                                 portal.enquiry_email,
                                 subject,
                                 question,
                                 enq.getOccupation(),
                                 enq.getPurpuse())
    host = portal.MailHost
    host.send(content)
    print content

def deleteEnquiryDatabase(self):
    """ delete all enquiry and requestor objects
    """
    logger = logging.getLogger("EEAPloneAdmin.enquiry_scripts")
    portal = api.portal.get()
    enquiries = portal['SITE']['help']['infocentre']['enquiries']
    requestors = portal['SITE']['help']['infocentre']['enquiries']['requestors']
    requestors2 = portal['SITE']['help']['infocentre']['enquiries']['enquiry-requestor-folder']

    enquiries_total = len(enquiries.keys())
    logger.info("%s enquiries found.", enquiries_total)
    requestors_total = len(requestors.keys())
    logger.info("%s requestors found.", requestors_total)
    requestors_total2 = len(requestors2.keys())
    logger.info("%s requestors2 found.", requestors_total2)
    total_count = 0
    total_count_break = 1000000

    # delete requestors
    logger.info("Starting to delete requestors!")
    count = 0
    count_to_commit = 20
    to_delete = [ x for x in requestors.keys()]
    for k in to_delete:
        requestors.manage_delObjects(ids=[k])
        count += 1
        logger.info("Deleted: %s / %s", count, count_to_commit)
        total_count += 1
        if total_count == total_count_break:
            break
        if count % count_to_commit == 0:
            logger.info("Requestors deleted: %s / %s", count, requestors_total)
            transaction.commit()

    # delete requestors2
    logger.info("Starting to delete requestors2!")
    count = 0
    count_to_commit = 20
    to_delete = [ x for x in requestors2.keys()]
    for k in to_delete:
        requestors2.manage_delObjects(ids=[k])
        count += 1
        logger.info("Deleted: %s / %s", count, count_to_commit)
        total_count += 1
        if total_count == total_count_break:
            break
        if count % count_to_commit == 0:
            logger.info("Requestors deleted: %s / %s", count, requestors_total2)
            transaction.commit()

    # delete enquiries
    logger.info("Starting to delete enquiries!")
    count = 0
    to_delete = [x for x in enquiries.keys()]
    for k in to_delete:
        enquiries.manage_delObjects(ids=[k])
        count += 1
        logger.info("Deleted: %s / %s", count, count_to_commit)
        total_count += 1
        if total_count == total_count_break:
            break
        if count % count_to_commit == 0:
            logger.info("Enquiries deleted: %s / %s", count, enquiries_total)
            transaction.commit()

    logger.info("Cleanup finished.")
    return "Cleanup finished."
