""" Moneky patch for PloneLanguageTool available languages
"""

from Products.PloneLanguageTool import availablelanguages

additional_languages = availablelanguages.languages
additional_languages['me'] = {'native' : 'Crnogorski jezik', u'english' : 'Montenegrin'}

availablelanguages.languages = additional_languages

