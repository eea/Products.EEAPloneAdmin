""" Config module
"""

GLOBALS = globals()
DEPENDENCIES = [
                'LinguaPlone',
                'ATVocabularyManager',
                'PloneHelpCenter',
                'XLIFFMarshall'
                'NavigationManager',
                'EEAEnquiry',

                #'EEAContentTypes',

                'PloneGazette',

                ]

# Available languages for EEA content
EEA_LANGUAGES = [
                  'bg','el',
                  'cs','da','nl','en',
                  'et','fi','fr','de',
                  'hu','is',
                  'it','lt',
                  'no','pl','pt','ro',
                  'sk','sl',
                  'es','sv','tr','lv'  ]

DEBUG = False
