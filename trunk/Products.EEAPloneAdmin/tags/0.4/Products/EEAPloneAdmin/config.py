GLOBALS = globals()
DEPENDENCIES = ['EEADesign2006', 'NavigationManager', 'PloneRSSPortlet', 'PloneLanguageTool', 'LinguaPlone', 'ATVocabularyManager', 'Marshall','PloneRDFCalendar','CMFonFive','CMFSquidTool','CacheSetup', 'EEAContentTypes','FiveSite', 'PloneGazette', 'PloneCaptcha', 'PloneHelpCenter', 'EEAEnquiry','RichTopic', 'ATVocabularyManager', 'XLIFFMarshall']

PRODUCT_DEPENDENCIES = ['MimetypesRegistry', 'PortalTransforms']

# CHANGE this tuple of python dictionnaries to list the different skin
#  selections and their associated specific layers.
#   'name' (required): the name of the new skin.
#     This will be what the user sees when choosing skins, and will be the
#     name of a property in portal_skins.
#   'base' (required): the name of the skin selection on which the new one
#     is based.
#   'layers' (optional): the name of the specific layers for the skin
#     selection. By default (if the value is empty or if the key is absent
#     from the dictionnary), all the folders in 'skins/' will be listed
#     underneath 'custom' in the new skin selection layers.
SKINSELECTIONS = (
    )

# CHANGE it to False if you don't want the new skin selection to be selected
#  at installation.
SELECTSKIN = True

# CHANGE it to the name of the skin selection that must be set as default in
#  case SELECTSKIN is set to True.
DEFAULTSKIN = 'EEAPloneAdmin'

# CHANGE this tuple of python dictionnaries to list the stylesheets that
#  will be registered with the portal_css tool.
#  'id' (required):
#    it must respect the name of the css or DTML file (case sensitive).
#    '.dtml' suffixes must be ignored.
#  'expression' (optional - default: ''): a tal condition.
#  'media' (optional - default: ''): possible values: 'screen', 'print',
#    'projection', 'handheld'...
#  'rel' (optional - default: 'stylesheet')
#  'title' (optional - default: '')
#  'rendering' (optional - default: 'import'): 'import', 'link' or 'inline'.
#  'enabled' (optional - default: 1): boolean
#  'cookable' (optional - default: True): boolean (aka 'merging allowed')
#  See registerStylesheet() arguments in
#  ResourceRegistries/tools/CSSRegistry.py
#  for the latest list of all available keys and default values.
STYLESHEETS = (
        )

# CHANGE this tuple of python dictionnaries to list the javascripts that
#  will be registered with the portal_javascripts tool.
#  'id' (required): same rules as for stylesheets.
#  'expression' (optional - default: ''): a tal condition.
#  'inline' (optional - default: False): boolean
#  'enabled' (optional - default: True): boolean
#  'cookable' (optional - default: True): boolean (aka 'merging allowed')
#  See registerScript() arguments in ResourceRegistries/tools/JSRegistry.py
#  for the latest list of all available keys and default values.
JAVASCRIPTS = (
#    {'id': 'myjavascript.js.dtml',},
        )

# CHANGE it to True if you want users to be able to select the skin to use
#  from their personal preferences management page.
#  In the ZMI, this value is known as 'Skin flexibility'.
ALLOWSELECTION = False

# CHANGE it to True if you want to make the skin cookie persist indefinitely.
#  In the ZMI, this value is known as 'Skin Cookie persistence'.
PERSISTENTCOOKIE = False

# CHANGE it to True if you want portal_skins properties to be reset to Plone
#  default values when the product is uninstalled:
#  Default Skin: 'Plone Default', Skin flexibility: False,
#  Skin Cookie persistence: False.
#  If set to False: Default Skin: BASESKIN,
#  Skin flexibility and Skin Cookie persistence left unmolested.
FULLRESET = False


# Available languages for EEA content
EEA_LANGUAGES = [  'bg','el',
                  'cs','da','nl','en',
                  'et','fi','fr','de',
                  'hu','is',
                  'it','lt',
                  'no','pl','pt','ro',
                  'sk','sl',
                  'es','sv','tr','lv'  ]

