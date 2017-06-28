""" Workflow Scripts for: Enquiry
"""
import quopri

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
    from plone import api
    import transaction
    import logging

    logger = logging.getLogger("EEAPloneAdmin.enquiry_scripts")
    portal = api.portal.get()
    enquiries = portal['SITE']['help']['infocentre']['enquiries']
    requestors = portal['SITE']['help']['infocentre']['enquiries']['requestors']

    enquiries_total = len(enquiries.keys())
    logger.info("%s enquiries found.", enquiries_total)
    requestors_total = len(requestors.keys())
    logger.info("%s requestors found.", requestors_total)

    # delete requestors
    logger.info("Starting to delete requestors!")
    count = 0
    for k in requestors.keys():
        requestors.manage_delObjects(ids=[k])
        count += 1
        if count % 100 == 0:
            logger.info("Requestors deleted: %s / %s", count, requestors_total)
            transaction.commit()

    # delete enquiries
    logger.info("Starting to delete enquiries!")
    count = 0
    for k in enquiries.keys():
        enquiries.manage_delObjects(ids=[k])
        count += 1
        if count % 100 == 0:
            logger.info("Enquiries deleted: %s / %s", count, enquiries_total)
            transaction.commit()

    logger.info("Cleanup finished.")
    return "Cleanup finished."
