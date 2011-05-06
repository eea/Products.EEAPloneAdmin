GLOBALS = globals()
DEPENDENCIES = [
                'LinguaPlone', 'ATVocabularyManager', 'PloneHelpCenter', 
                'ATVocabularyManager', 'XLIFFMarshall'

                'NavigationManager', 
                'EEAContentTypes', 'EEAEnquiry', 

                #plone4 disabled until migrated
                #'PloneGazette', 
                #'PloneCaptcha',        - we need a solution for this
                
                #old packages, not needed anymore
                #'FiveSite', 'CMFonFive', 
                #'CMFSquidTool', 'CacheSetup',    - see plone.app.caching
                #'EEADesign2006',                 - now it's eea.design
                #'RichTopic',                     - builtin now
                #'PloneLanguageTool', 
                #'Marshall', 
                
                ]

#PRODUCT_DEPENDENCIES = ['MimetypesRegistry', 'PortalTransforms']

## CHANGE it to the name of the skin selection that must be set as default in
##  case SELECTSKIN is set to True.
#DEFAULTSKIN = 'EEAPloneAdmin'


## CHANGE it to True if you want users to be able to select the skin to use
##  from their personal preferences management page.
##  In the ZMI, this value is known as 'Skin flexibility'.
#ALLOWSELECTION = False

## CHANGE it to True if you want to make the skin cookie persist indefinitely.
##  In the ZMI, this value is known as 'Skin Cookie persistence'.
#PERSISTENTCOOKIE = False

## CHANGE it to True if you want portal_skins properties to be reset to Plone
##  default values when the product is uninstalled:
##  Default Skin: 'Plone Default', Skin flexibility: False,
##  Skin Cookie persistence: False.
##  If set to False: Default Skin: BASESKIN,
##  Skin flexibility and Skin Cookie persistence left unmolested.
#FULLRESET = False


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

