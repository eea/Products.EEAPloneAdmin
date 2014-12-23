## Script (Python) "register_newsletter"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=nlpath=None, email=None, format=None, REQUEST=None
##title=Due #5220, fixed in Products.PloneGazette ver 4.5
##
# ******************************************************************
# ** Transmit the subscribe request to selected NewsletterTheme **
# ******************************************************************
#
# Handles the subscription form from newsletter_slot
#
# $Id: register_newsletter.py 19042 2010-12-08 10:41:19Z tiberich $
#
from Products.PythonScripts.standard import url_quote

if REQUEST is None:
    REQUEST = context.REQUEST
    
nlcentral = context.restrictedTraverse(nlpath, None)

# Case of wrong parameters
if nlcentral is None:
    REQUEST.RESPONSE.redirect(context.portal_url())
    return

# Case of wrong parameters
if nlcentral.portal_type != 'NewsletterTheme':
    REQUEST.RESPONSE.redirect(context.portal_url())
    return

# Subscribe action
if format is None:
    format = nlcentral.default_format
    
actions = context.portal_actions.listFilteredActionsFor(object=nlcentral)
url = [action['url'] for action in actions['object']
       if action['id'] == 'subscribe'][0]
query = '?email=%s&format=%s' % (url_quote(email), format)

REQUEST.RESPONSE.redirect(url + query)
return
