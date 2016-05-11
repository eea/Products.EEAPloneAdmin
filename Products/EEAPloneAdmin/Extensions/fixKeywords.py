""" Evolve to version 7.1
"""
import logging
import transaction
from zope.component.hooks import getSite
from Products.CMFCore.utils import getToolByName

allowed = set([
    'sea temperature', 'driving tips', 'forest creation', 'bioplant',
    'land development', 'heavy metal', 'trawling', 'orthophosphate',
    'urban ecosystem', 'electricity', 'ocean sink', 'noise database',
    'compact fluorescent lamp', 'biodiversity loss', 'bike', 'herbicide',
    'point of pollution', 'natural hazards', 'ecosystem services', 'risk',
    'geology', 'freight activity', 'fine dust', 'environmental charges',
    'lignite', 'clc1990', 'alpine', 'nitrates directive', 'energy use', 'crops',
    'natura 2000 sites', 'consumption and production patterns', 'methane',
    'undernourishment', 'bicycle', 'outlook018', 'extreme weather event',
    'guidelines', 'street', 'water use', 'emissions from transport',
    'pan-european environment', 'soer2010', 'settlement', 'term009', 'nec',
    'scp', 'term008', 'air quality zones 2009', 'fossil', 'harmful algal bloom',
    'pentachlorophenol', 'forest connectivity', 'oil discharge', 'vineyard',
    'non-governmental', 'deposition', 'protection', 'cardboard',
    'soil conservation', 'freight transport intensity', 'undp',
    'security of energy supply', 'road safety', 'nitrogen oxide', 'salt-marsh',
    'energy crisis', 'projection', 'classification', 'mobility', 'ippc',
    'threatened species', 'summerhouses', 'landscape', 'ccpm', 'exceedance',
    'eastern europe', 'heat wave', 'risk management', 'coastal ecosystem',
    'coastal waters', 'state and outlook 2005', 'export', 'corrosion',
    'energy efficiency', 'un climate conference', 'material flows', 'eru',
    'flora', 'agricultural ecosystem', 'coast_sea', 'endangered plant species',
    'ener34', 'socio-economy', 'land cover flow', 'household', 'inland water',
    'uaa', 'biological sequences', 'sea catchment', 'nuts', 'natural heritage',
    'the trading system', 'anthropogenic ghg emission', 'forest fires', 'beach',
    'clcchanges', 'offshore', 'clim028', 'abstraction', 'assessment11',
    'assessment10', 'birds directive', 'acidophilous oak forest', 'warm',
    'cardiovascular disease', 'spatial data', 'agriculture bioenergy potential',
    'waste prevention', 'water framework directive article 5', 'sulphate',
    'trading directive', 'water framework directive article 8',
    'natural materials', 'clim020', 'wind', 'wine', 'corinair', 'ener027',
    'soil sealing', 'industrial processes', 'urban structure', 'clc',
    'plantation', 'distribution of waste', 'production', 'environmental law',
    'urban policy', 'coffee', 'diseases', 'emission ceiling',
    'emission reduction unit', 'wec07b', 'hypoxic', 'one', 'tourism', 'unfccc',
    'meat', 'oxygen', 'recreational area', 'river system', 'population density',
    'natura 2000', 'windmill', 'our arctic challenge', 'growing season',
    'atmospheric pollutants', 'acid rain', 'nitrite', 'mothers milk',
    'textile industry', 'network', 'material productivity', 'cdda',
    'water legislation', 'river basin district', 'sheep', 'old-growth forest',
    'ramon', 'standard', 'urban environment', 'formation', 'mammal',
    'publication', 'carbon sink', 'logging', 'refugee',
    'self-sown exotic forest', 'pricing policy', 'baltic',
    'diffuse contamination', 'industrial', 'massif', 'term_f03', 'term_f02',
    'insulation', 'biomes', 'global impacts', 'mercury',
    'bathing water report', 'service', 'bonito', 'csi003', 'ghg2009-2.1',
    'ocean acidification', 'farming', 'future environmental challenges',
    'urban', 'transport infrastructure', 'energy efficient lighting', 'wq002',
    'wq005', 'wq004', 'csi006', 'csi005', 'cereal', 'sulphur', 'csi004',
    'water data centre', 'raw material', 'oxygen depletion', 'target',
    'green pharmacy', 'ener007ener2011', 'wind energy',
    'volatile organic compounds', 'energy certification', 'lba', 'data centre',
    'pandemics', 'increment', 'carbon emission', 'mountain2010', 'biogas',
    'food processing', 'wind energy potential', 'street lamp', 'wells',
    'biodiversity indicators', 'carbon cycle', 'urban beekeeping', 'furan',
    'drought', 'water exploitation index', 'waste2008', 'water management',
    'metal', 'life-cycle thinking', 'motorways',
    'sustainable energy production', 'lpg', 'forest degradation',
    'anthropogenic', 'reserve', 'water engineering project',
    'greenhouse gas inventory', 'arctic region', 'pops',
    'policy effectiveness evaluation', 'weu011', 'artificialisation',
    'weu014', 'apr2007', 'thematic assessment', 'bathing water',
    'exports', 'glaciers', 'asbestos', 'enpi-seis', 'burden-sharing',
    'degradation', 'environmental pressure intensity', 'health impact',
    'emf', 'long-term perspective', 'industrial waste', 'beech forest',
    'greenx', 'protocols', 'farmland biodiversity', 'run-off',
    'united states', 'freshwater', 'tax deduction', 'ecodesign',
    'disaster', 'semi-natural habitat', 'cattle', 'support scheme',
    'fossil fuels', 'killer slug', 'combustion', 'environmental politics',
    'biofules', 'species impoverishment', 'biogeographic', 'phallates',
    'nature', 'baseline2010', 'state and outlook 2005 - part b',
    'state and outlook 2005 - part a', 'astana2011', 'wq',
    'contamination', 'carbon', 'flowering', 'energy demand', 'climate',
    'accident', 'wind speed', 'sanitation', 'ground-level ozone',
    'heating', 'ecosoc', 'life cycle', 'wrapping', 'cod',
    'space heating', 'iczm', 'organophosphate',
    'coral acidification', 'safe biological limits',
    'fluorinated gases', 'arsenic', 'endenism', 'energy price',
    'industrial effluent', 'decoupling', 'tradable permits',
    'sulfur hexafluoride', 'snow cover', 'subsidy', 'extraction', 'paraben',
    'mitigation', 'water temperature', 'onshore wind energy',
    'scenario studies', 'passenger car', 'life', 'resource efficiency roadmap',
    'catchment', 'coastline urbanisation', 'aviation', 'hazardous substance',
    'skin cancer', 'tide', 'administrative', 'technological accidents', 'wfd',
    'air', 'aspen forest', 'flooding', 'term indicators',
    'climate change impacts', 'n2o', 'arctic sea ice', 'ancillary data',
    'natural disasters', 'nature reserve', 'surface water', 'ee_f08',
    'sebi005', 'environmental megatrends', 'patent', 'term014', 'boreal forest',
    'beach water', 'inventory', 'vegetable', 'natlan', 'decision-making',
    'rail', 'term029', 'rain', 'deadwood', 'temperature increase', 'wq01c',
    'tuna', 'cycle', 'designated areas', 'competition for resources',
    'water scarcity', 'ocean', 'chemical concentration model', 'term023',
    'materials', 'pathogenic micro-organism', 'fungicide', 'se_f02',
    'hybrid vehicle', 'term021', 'carbon footprint',
    'water resource management', 'massifs', 'human', 'eu strategy',
    'high nature value', 'biome', 'term018', 'atmospheric nitrogen',
    'production patterns', 'farmland abandonment', 'n', 'term019', 'elevation',
    'municipal', 'cultural landscapes', 'sustainable resource management',
    'shopping journey', 'compaction', 'lca', 'non-riverine alder forest',
    'annual report', 'low-cost flight', 'bathing water directive', 'e-waste',
    'groundwater', 'soil functions', 'security', 'greenland', 'lcep',
    'energy production impact', 'ape3a', 'wwf', 'technological hazards',
    'environmental zone', 'climate change in mountains', 'sprawl', 'rhine',
    'mobility week', 'population exposure', 'water loss', 'ice', 'umz',
    'eco-industry', 'paper recycling', 'nitrate', 'air quality directive',
    'freshwater pollution', 'videoconferencing', 'fish',
    'patent genetic resources', 'urban air quality',
    'natural resource conservation', 'cork', 'fuel consumption', 'rhone',
    'habitat destruction', 'shared environmental information system',
    'windstorms', 'traffic jam', 'ener007', 'local production', 'ener006',
    'lorry load factor', 'war of independence', 'land management',
    'satellite imagery', 'waste disposal', 'dry matter', 'permafrost',
    'outlook05', 'post-socialist transition', 'mbi', 'emissions for industry',
    'whs', 'sebi024', 'sebi025', 'sebi026', 'sebi020', 'governance',
    'environmental policy', 'sebi023', 'sox', 'blue fish', 'outlook052',
    'outlook053', 'green growth', 'outlook051', 'gis', 'mountain area',
    'outlook054', 'outlook055', 'land take', 'sunlight', 'conservation',
    'climate strategy', 'wood supply', 'war', 'synthesis',
    'respiratory diseases', 'management plan', 'landing', 'term2009',
    'hemisphere', 'so2', 'water information system for europe',
    'non-road transport', 'otter', 'sebi16', 'sebi17', 'sebi15',
    'aarhus convention', 'sebi13', 'sebi10', 'sebi11', 'integrated farming',
    'sebi18', 'sebi19', 'phosphate', 'biomass action plan',
    'european neighbourhood project', 'floating house', 'baltic sea ecosystem',
    'manure', 'sulphur oxides', 'forward-looking information and services',
    'carbon capture', 'glacier', 'environmental model inventory',
    'non-hazardous waste', 'environmental modelling technique', 'flood',
    'transboundary waste shipment', 'protected area', 'erosion', 'energy audit',
    'marine resources conservation', 'diet', 'ammonium', 'discharge',
    'land monitoring', 'early warning', 'health effects', 'radioactivity',
    'potato', 'development of gdp', 'urban morphological zones', 'ozone hole',
    'air pollutant emissions', 'irrigation', 'coach', 'cost-benefit analysis',
    'chemical policy', 'global', 'organic micro-pollutant', 'central park',
    'avalanche', 'energy consumption', 'term003', 'heath and scrub', 'milk',
    'paper waste', 'sustainable forestry',
    'european free trade association (efta)', 'zone', 'safe water',
    'certification', 'kyoto gases', 'environment', 'eea strategy', 'biotope',
    'wise state of the environment(soe)', 'term002', 'intelligent irrigation',
    'inventory guidebook', 'financial crisis', 'gua', 'wq02a',
    'urban population', 'sand extraction', 'carbon uptake', 'baltic sea',
    'nuclear accident', 'decomposition analysis', 'invasive species',
    'environmentally-compatible bioenergy', 'pork', 'nemoral coniferous forest',
    'trend', 'annual fellings', 'clean water', 'steppic',
    'landscape protection area', 'policy measures', 'marine trophic index',
    'nature and biodiversity', 'plastic waste', 'landslides', 'coastal water',
    'energy efficient bulb', 'kyoto protocol', 'rocky habitats', 'no3-n',
    '10 messages for 2010', 'genes', 'storm overflow', 'water',
    'emissions reduction', 'kyoto mechanism', 'earthquake', 'change',
    'recycled material', 'alternative fuel', 'eionet waterbase',
    'stratified catchment assessment', 'ener2009', 'decouple', 'anoxia',
    'neigbourhood', 'anoxic', 'bog', 'car industry', 'ecosystem accounting',
    'sand erosion', 'dioxin', 'regeneration', 'natural park', 'etc/acc',
    'water pollution', 'eea product', 'mackeral', 'biodegradable waste',
    'scenarios', 'wood', 'data management', 'raster data', 'sustainableuse2005',
    'wildlife', 'sebi011', 'sebi010', 'sebi013', 'sebi012', 'sebi015',
    'road density', 'sebi016', 'sebi019', 'green week', 'air conditioning',
    'outlook041', 'outlook043', 'outlook042',
    'eu marine strategy framework directive', 'outlook046', 'outlook049', 'car',
    'cap', 'radon', 'the risk of carbon leakage', 'mesophytic deciduous forest',
    'landscape management', 'lubricant', 'biogeographical region',
    'costs of adaptation', 'forestry bioenergy potential', 'social megatrends',
    'subsidies', 'spa', 'term2011', 'term2010', 'sebi05', 'sebi04', 'sebi07',
    'sebi06', 'sebi01', 'sebi03', 'sebi02', 'aquatic habitats', 'sebi08',
    'chemical', 'risk reduction', 'combustion plant',
    'broadleaved evergreen forest', 'economy', 'csi032', 'csi033', 'csi030',
    'csi031', 'csi036', 'csi037', 'air pollutant emissions data viewer',
    'csi035', 'low emitting households', 'deforestation', 'sustainability',
    'water abstraction', 'bear', 'pasture', 'natural', 'sectors', 'gisco',
    'offshore wind energy', 'necd', 'hexachlorocyclohexane', 'ghg',
    'key pollutants', 'soil moisture', 'cap and trade', 'estuary', 'nitrogen',
    'irena', 'boreal', 'birds', 'no2', 'caucasus', 'wq03b', 'unece', 'monitor',
    'sebi2010', 'economic damage costs', 'marine water', 'gravel extraction',
    'non-renewable energy', 'policy', 'winter sport', 'toxin', 'bunker fuels',
    'green job', 'environmental trends', 'habitats directive',
    'kitchen and garden waste', 'toxic', 'nox', 'carbon monoxide', 'term',
    'endocrine disruption', 'bio-geographical regions',
    'certified emission reduction', 'rock', 'developing countries',
    'nuclear safety', 'bdiv07d', 'turtle', 'material footprint', 'coastal',
    'median', 'state of the environment report 1-2007', 'brackish water',
    'road capacity', 'obsolete chemical', 'eu', 'neighbourhood', 'container',
    'hcb', 'scp2007', 'tire pressure', 'car sales', 'reforestation', 'hch',
    'automobile manufacturer', 'term040', 'cars', 'phthalates',
    'european adaptation strategy', 'systemic risks', 'outlook056', 'marine',
    'lme', 'sea level rise', 'natural resources', 'sustainable development',
    'nao index', 'oi055', 'marine strategy framework directive',
    'coastal areas', 'particle emissions', 'genetic diversity',
    'climatic change', 'pm2.5', 'circles of discovery', 'natura2000',
    'conifer', 'in-shore', 'lutra lutra', 'legal instruments',
    'endemic species', 'city', 'eetap', 'plastic', 'ener2011', 'ener2010',
    'cooling', 'human health', 'citl', 'nitrogen balance', 'streetlight',
    'mining', 'releases', 'transboundary issues', 'white goods',
    'co2 transferral', 'lung disease', 'product groups', 'food transport',
    'policy instruments', 'population', 'television', 'pannonian',
    'household waste', 'intensity', 'policy integration',
    'ecosystems perspective', 'landuse', 'water pollution from agriculture',
    'mountainous beech forest', 'rapeseed oil',
    'global monitoring for environment and security',
    'water framework directive', 'sebi008', 'sebi009', 'sebi006', 'sebi007',
    'sebi004', 'eoid', 'sebi002', 'emep', 'sebi001', 'conversion', 'term028',
    'landscape planning', 'term022', 'national emission ceilings directive',
    'term020', 'term027', 'term026', 'term025', 'term024',
    'environmental footprint', 'nitrogen oxides', 'energy intensity',
    'butterfly', 'annual management plan', 'quality of life', 'price',
    'passenger transport', 'sebi021', 'invertebrate', 'modal split', 'lulucf',
    'ener005', 'aquatic life', 'ener009', 'ener008', 'tropospheric ozone',
    'north sea', 'gothenburg protocol', 'heat', 'grassland', 'csi021', 'csi020',
    'csi023', 'csi022', 'csi025', 'csi024', 'csi027', 'csi026', 'csi029',
    'csi028', 'central heating', 'air pollution control', 'consumption trend',
    'chemical elements', 'domestic appliance', 'european union (eu)',
    'car sharing', 'carsharing', 'health target value',
    'emissions trading directive', 'storms', 'eu coverage', 'inventions',
    'ecological network', 'public space', 'carbon storage', 'outlook050',
    'eu policies', 'water-borne diseases', 'biodiesel', 'sebi2009',
    'carbon capture technology', 'sebi12', 'resource', 'floods', 'green area',
    'energy mix', 'climate change adaptation', 'bison', 'land cover change',
    'seal', 'compounds', 'noise reduction', 'household consumption', 'import',
    'forest type', 'street increment', 'infrastructure', 'sea surface',
    'land use trends', 'oil exploitation', 'construction mineral', 'cities',
    'water security', 'eu emission inventory', 'water consumption',
    'sulfur dioxide', 'genetic pollution', 'nomenclature',
    'technological change', 'kulturnat', 'aot40', 'iron and steel waste',
    'cancer', 'passenger', 'agri-environment', 'middle-class',
    'economic downturn', 'forest conservation', 'alps2009',
    'ecological footprint', 'rio conference', 'odex', 'territorial',
    'ice extend', 'term04', 'landscape changes', 'corine land cover',
    'ski resort', 'diesel', 'sewage treatment', 'alien species', 'pesticide',
    'adaptation strategy', 'air pollution from energy', 'marine pollution',
    'term036', 'gas exploitation', 'felling', 'hemiboreal forest',
    'biocapacity', 'sewerage', 'environmental statement', 'policies',
    'landslide', 'aluminium', 'assessment of assessments', 'population trend',
    'soil', 'web tool', 'eye on earth', 'nutrient enrichment',
    'national strategies', 'csi0xx', 'demolition', 'fame', 'green urban areas',
    'glass waste', 'term26', 'term27', 'enquiries', 'term25', 'term22',
    'landfill directive', 'term20', 'term21', 'pah',
    'conservation of biodiversity', 'use patterns', 'term29', 'oil', 'arctic',
    'waste bioenergy potential', 'life cycle approach', 'nature capital',
    'earth summit', 'railway', 'renewable', 'term038', 'seagrass',
    'surface temperature', 'term031', 'term032', 'term033', 'term034',
    'term010', 'ccs', 'consumer behaviour', 'ghg inventory reporting',
    'polychlorinated biphenyls', 'term011', 'term016', 'model',
    'spatial planning', 'overcrowding', 'gdp', 'summer', 'livestock',
    'protected species', 'ener014', 'ener015', 'ener016', 'ener017',
    'ener010', 'ener011', 'ener012', 'ener013', 'oi023', 'ener018',
    'ener019', 'consumption pattern', 'drivers of change', 'death',
    'asthma', 'hydroelectric dam', 'sebi26', 'sebi25', 'sebi24', 'sebi23',
    'sebi22', 'sebi20', 'bioenergy', 'invasive', 'potash', 'consumer prices',
    'sea', 'anchovy', 'csi018', 'csi019', 'direct and indirect pressures',
    'csi014', 'csi015', 'csi016', 'csi017', 'csi010', 'fridge', 'csi012',
    'csi013', 'traffic', 'grid', 'water flow', 'social equity', 'world',
    'urban sprawl', 'windbreak', 'nutrients', 'demography',
    'integrated assessment', 'urban traffic', 'lobster', 'eu 2020', 'danube',
    'public service', 'low-carbon economy', 'ddt', 'decomposition', 'o3',
    'kyoto', 'airbase', 'eu cohesion policy', 'mandrake', 'car occupancy',
    'clim2008', 'oi', 'industry', 'violence', 'clim017', 'shrimp', 'wolf',
    'aquaculture', 'our natural europe', 'motorisation', 'road',
    'technological progress', 'outlook', 'ice melting',
    'integrated coastal management', 'uv rays', 'corilis', 'fertility',
    'lrtap', 'log', 'ozone depleting substance', 'hazards', 'clim018', 'whs011',
    'raw materials', 'industrial production', 'land conservation',
    'burning waste', 'whs012', 'oxidised', 'raw material consumption',
    'intensive farming', 'technologies', 'eea environment policy', 'renewables',
    'food production', 'emissions', 'clim08', 'cba', 'energy efficiency label',
    'transport demand', 'domestic animals', 'oi045', 'oi047', 'economic growth',
    'absorption capacity', 'oi042', 'swimming water', 'hazardous chemical',
    'environmental assets', 'washing machine', 'waste water',
    'emissions from agriculture', 'lrtap convention', 'civitas',
    'sustainable tourism', 'notified waste', 'belgrade07', 'eu-15',
    'pan-european', 'pollutants', 'net annual increment', 'marine oil field',
    'dominant landscapes types', 'electromagnetic field', 'freight transport',
    'greenhouse gases', 'nmvoc', 'shipping', 'sustainable food consumption',
    'air pollution', 'somo35', 'ultrafine particle', 'landfill', 'green tip',
    'term30', 'term32', 'illegal waste shipment', 'wastewater', 'ghg inventory',
    'non-renewable resource', 'transport price', 'loggerhead turtle', 'allergy',
    'term004', 'term007', 'term006', 'term001', 'candidate countries',
    'outlook019', 'outlook017', 'outlook014', 'research', 'ape2009',
    'outlook013', 'outlook010', 'outlook011', 'hunting',
    'environmental assessment report no 10', 'agri-environment indicators',
    'diffuse', 'national park', 'ozone station', 'country policy',
    'annual average', 'import dependency', 'whs008', 'whs009', 'whs002',
    'whs003', 'whs007', 'ener021', 'ener020', 'ener023', 'ener022', 'ener025',
    'ener024', 'abouteea', 'ener026', 'ener029', 'ener028', 'anatolian',
    'over-abstraction', 'sulphur dioxide', 'ghg2009', 'ghg2008',
    'information technologies', 'sand', 'eea report no 2/2004', 'pbc',
    'public awareness', 'ghg emission', 'national adaptation strategy',
    'csi009', 'csi008', 'antibiotic', 'climate change consequences', 'csi002',
    'csi001', 'economic competitiveness', 'csi007', 'forward-looking indicator',
    'forest monitoring', 'ener32', 'residue', 'water assessment',
    'greenhouse gas emissions', 'rockfalls', 'malaria', 'water transport',
    'liability and  compensation schemes', 'coastal management',
    'ozone depletion', 'indigenous people', 'seed bank', 'advertising',
    'eionet', 'strategy analysis', 'biowaste', 'ocean temperature',
    'electronic waste', 'energy consumtion', 'appliances', 'extinction',
    'emission trends and projections',
    'biodiversity information system for europe', 'clim042', 'clim040',
    'clim041', 'oecd', 'precautionary principle', 'teleconference',
    'eu legislation', 'urban transport', 'contaminated land',
    'land use planning', 'jacqueline mcglade', 'emission',
    'passenger transport intensity', 'life cycle assessment', 'dem',
    'nomenclature server', 'hydrological cycle',
    'sustainable consumption and production', 'first environmental policies',
    'impacts', 'pond', 'species', 'weu004', 'terrestrial', 'clc2006', 'csi',
    'clc2000', 'land cover', 'eea role', 'developed countries', 'maps',
    'public opinion', 'air quality data', 'nitrous oxide', 'dust mites',
    'land sink', 'extensive farming', 'low-input farming', 'plant',
    'transitional water', 'oi054', 'cadmium', 'lighting',
    'habitat fragmentation', 'image2000', 'response', 'alps',
    'welfare change', 'coal', 'urban design', 'marine transport', 'hfc',
    'geographic', 'wb2009', 'fuel switch', 'help', 'water services', 'trade',
    'paper', 'electronic equipment', 'alternative water supplies',
    'emission reduction', 'organic food', 'volcanic eruptions',
    'cardiovascular', 'growth rates', 'black triangle', 'dismed', 'fuel cell',
    'pcp', 'term24', 'urbanization', 'term01', 'term02', 'term03',
    'resource efficiency', 'pcb', 'term09', 'environmentally-oriented farming',
    'oil spills', 'hidden costs of production', 'gmos', 'habitat directive',
    'afforestation', 'international statistical classifications', 'food',
    'alkalinity', 'education based travel', 'wq02e', 'term012', 'term013',
    'ape2010', 'ape2011', 'outlook009', 'outlook008', 'ecodriving', 'term015',
    'outlook005', 'outlook004', 'outlook007', 'outlook006', 'fact sheets',
    'outlook003', 'outlook002', 'capacity building', 'high ozone concentration',
    'community farm', 'land conversion', 'crysopteris montana',
    'waste recovery', 'eu objective', 'corine', 'industrial combustion',
    'air pollutant inventory', 'carbon dioxide', 'energy',
    'conservation of species', 'central asia', 'ener034', 'ener035', 'ener032',
    'ener030', 'ener031', 'water shortage', 'alcohol', 'ghg2010', 'ghg2011',
    'waste incineration', 'health', 'shipment', 'soil protection',
    'reporting', 'solvent', 'material resources', 'wastewater treatment',
    'recycling of car', 'rock extraction', 'emission monitoring', 'whs01a',
    'congestion charge', 'algae', 'sbl', 'finland', 'climate change mitigation',
    'millenium seed bank', 'near real-time data', 'rainforest', 'copper',
    'noise exposure', 'emission trading scheme', 'etc/npb', 'river',
    'emission inventory', 'temperature', 'blossom', 'coasts', 'station',
    'storm', 'endangered species', 'threats to biodiversity', 'water quantity',
    'leafing', 'contributing factors', 'fossil fuel', 'mediterranean',
    'mudflat', 'pcdd/f', 'plane', 'biomass', 'crop', 'air transport emissions',
    'ecotourism', 'sebiassessment09', 'inland', 'financing', 'clim038',
    'clim033', 'natural compost', 'clim031', 'clim030', 'clim037', 'clim036',
    'clim035', 'clim034', 'term030', 'beach pollution', 'video', 'gps',
    'imports', 'chemical industry', 'term035', 'tipping element',
    'eco-technology', 'guidelines on monitoring and reporting',
    'reporting obligations', 'cepa', 'concentration', 'term037',
    'mountain', 'air quality', 'green space', 'vulnerabilities', 'labour',
    'wec04e', 'agro-ecosystems', 'black sea', 'nh4-n', 'speed limits',
    'bottled water', 'rain water', 'bdiv', 'resource use', 'green technology',
    'measures', 'reach', 'etc/wtr', 'moss', 'wq006', 'caspian sea', 'eurosion',
    'water account', 'marine litter', 'mineral', 'cover', 'coral reefs',
    'municipal waste generation', 'high-input farming', 'amphibian',
    'working remit', 'living area', 'sector', 'nh3', 'evaporation',
    'mountain flower', 'freight', 'impact', 'indicator', 'aquatic ecosystems',
    'saline intrusion', 'fruit', 'signals2011', 'rural', 'ied',
    'food consumption', 'toxic spills', 'template', 'solar energy',
    'waste policy', 'clim039', 'maritime economy', 'passive house',
    'welfare', 'sources', 'natural capital', 'powerplant', 'term19',
    'clim032', 'sustainable', 'externalities', 'belgrade conference',
    'an assessment of assessments', 'altimetry', 'emas', 'ecosystem integrity',
    'tree', 'vertebrates', 'carpool', 'outlook030',
    'environmental model characterisation', 'outlook032', 'migration',
    'mixtures and alloys.', 'outlook037', 'eea general brochure 2009 (bg)',
    'outlook039', 'dpsir', 'threats', 'road freight', 'particulate matter',
    'coastal city', 'soil organic matter', 'europe', 'assessmentv2', 'europa',
    'drinking water', 'protected areas', 'biodiversity components',
    'water quality', 'packaging waste', 'alpine rivers', 'prelude', 'sprat',
    'alpine coniferous forest', 'emission trends', 'urbanisation',
    'manufactured chemicals', 'satellite observations', 'eco-village', 'wei',
    'load', 'air quality forecasting', 'sustainable transport',
    'coastal sediment balance', 'composting', 'recycling', 'dietary',
    'adaptation', 'landscape fragmentation', 'fine particles', 'seabed mining',
    'urban waste water', 'cardboard recycling', 'pb', 'suburbs',
    'environment for europe', 'chlorophyll-a', 'electricity consumption',
    'ph', 'territory', 'po', 'pm', 'chemical density', 'fire', 'gas',
    'waste import', 'land change', 'ener16', 'marine and coastal', 'demand',
    'data flow', 'deepwater', 'grains', 'avalanches', 'budget',
    'eea signals 2010 - biodiversity', 'technological innovation',
    'special protection area', 'industrial emissions directive',
    'sectoral integration', 'dioxins and furans', 'less favoured areas',
    'clim029', 'indoor pollution', 'italy', 'baseline', 'global megatrends',
    'clim021', 'clim022', 'clim023', 'clim024', 'clim025', 'clim026', 'clim027',
    'aggregate extraction', 'sustainable farming', 'products',
    'forest stewardship council', 'development', 'ice road', 'forestry model',
    'global warming', 'csi011', 'citybees', 'salinisation',
    'sustainable living', 'who we are', 'bod', 'food consumption patterns',
    'water protection', 'public outreach', 'chemical product labelling',
    'pollen', 'weu013', 'weu010', 'urban forest', 'weu016', 'population change',
    'weu015', 'domestic material consumption', 'political megatrends',
    'economic unequality', 'ozone layer', 'eunis',
    'sustainable forest management', 'bicycle lane',
    'bathing water quality', 'global resource exploitation', 'euroharp',
    'environmental pressure', 'ecosystems', 'eu air emission policies',
    'precipitation', 'eco-label', 'eu-27',
    'soil country profiles - population density', 'polymers',
    'national emissions ceilings', 'labour productivity', 'air pollution costs',
    'eea', 'signals2009', 'ecology', 'environmental accounts', 'economic',
    'rumex nivalis', 'natural parc', 'economic megatrends', 'tropical night',
    'environmental management system', 'ener06', 'ener07', 'ener05', 'ener02',
    'ener01', 'groundwater quality', 'ener08', 'ener09', 'innovation', 'ape',
    'country codes', 'water demand', 'noise indicators', 'common bird',
    'social media', 'salmon', 'lakes', 'greenhouse gas', 'outlook027',
    'outlook026', 'outlook025', 'outlook024', 'outlook023', 'outlook021',
    'outlook020', 'eea owned data sets', 'land use change', 'low level ozone',
    'outlook028', 'pipeline', 'usa', 'chemicals information system',
    'land prices', 'electric car', 'bise', 'pollution', 'garbage',
    'car ownership', 'tofp', 'energy efficient buildings', 'insecticide',
    'inventories', 'resilience', 'fish catch', 'global governance',
    'statistics', 'coastal bathing waters', 'energy production', 'hydropower',
    'pharmaceuticals', "europe's environment", 'mountains',
    'eea member countries', 'frost', 'immigration', 'fisheries', 'atlantic',
    'chemical pollution', 'statistical regions', 'electricity generation',
    'uv', 'price of water', 'utm', 'un', 'desalination',
    'white-backed woodpecker', 'units', 'biodynamic agriculture', 'overfishing',
    'metals', 'organic agriculture', 'cafe', 'yearbook', 'urban lifestyle',
    'environmental change model', 'uranium', 'precious metal', 'income',
    'fuel efficiency', 'pesticides', 'ranunculus montanus', 'power shifts',
    'state of the environment', 'combined heat and power', 'clim015', 'clim014',
    'insect', 'clim016', 'clim011', 'clim010', 'clim013', 'clim012',
    'transport subsidies', 'clim019', 'desert', 'tradable carbon unit',
    'waterbase', 'land', 'pm10', 'nature conservation', 'age', 'youtube',
    'common agricultural policy', 'corporate communication', 'water footprint',
    'sebi017', 'natural gas', 'water supply', 'case studies', 'sebi018',
    'petrol emission', 'ammonia', 'long-range transboundary air pollution',
    'flood management', 'disposal', 'triazine pesticides',
    'municipal solid waste', 'gravel', 'resources', 'energy productivity',
    'weu001', 'weu003', 'weu002', 'weu005', 'soer', 'weu007',
    'sustainable industrial policy', 'weu009', 'weu008', 'ozone precursors',
    'non-methane volatile organic compounds', 'facebook', 'minerals',
    'outlook047', 'iberian lynx', 'gender', 'wec2d', 'high emitting households',
    'outlook048', 'sewage', 'cfl', 'quarrrying', 'trawl', 'bod5', 'cfc',
    'bod7', 'rivers', 'oi009', 'oi008', 'energy-related emission',
    'baltic sea ice', 'oi001', 'oi003', 'acid', 'oi005', 'oi004', 'cfp',
    'oi006', 'fish stock', 'regeneration of industrial area', 'directive',
    'biomass energy', 'august2009delivery', 'environmental agreements',
    'technology', 'bird', 'product use', 'fertilization', 'poverty',
    'expansion', 'marine management', 'ener15', 'ghg emissions', 'ener17',
    'biodiversity', 'ener11', 'ener13', 'ener12', 'ener19', 'ener18',
    'artificial sprawl', 'organic farming', 'volga', 'mussel', 'namea',
    'clrtap', 'redd', 'eu ets', 'global trade',
    'multinational emissions trading scheme', 'consumption', 'halocarbons',
    'fragmentation report 2011', 'illegal', 'consumer good', 'oil processing',
    'chp', 'red list', 'vehicle', 'working area', 'public water supply',
    'eutrophication', 'pfc', 'organic soils', 'negative impacts of bioenergy',
    'what we do', 'sewerage network', 'rubbish', 'pollutant',
    'emep model scenarios', 'montreal protocol', 'antifouling paint',
    'recession', 'road traffic', 'ee-aoa', 'water protection directive', 'ch4',
    'nitrogen dioxide', 'waterway', 'posidonia oceanica', 'road transport',
    'tax', 'outlook indicator', 'birch forest', 'energy production emissions',
    'understanding climate change', 'biofuel directive', 'native species',
    'sip', 'polycyclic aromatic hydrocarbons', 'regions', 'forest', 'animal',
    'river navigation', 'buildings', 'water towers', 'farm',
    'nocturnal species', 'coast', 'green wall', 'emission trading',
    'fairmode', 'lindane', 'exhaust gas', 'world health organisation', 'ener',
    'sebi09', 'cropland', 'second generation biofuels', 'clim002', 'clim003',
    'clim001', 'clim006', 'clim007', 'clim004', 'clim005', 'clim008',
    'clim009', 'geophysical hazards', 'ocean acidity',
    'biodiversity monitoring', 'specific regions', 'cabon binding',
    'childhood cancer', 'non-motorised transport', 'tsp',
    'biodiversity conservation', 'waste policies', 'dam', 'swordfish', 'dike',
    'inland bathing water', 'green budget', 'lucas data quality',
    'fatty acid methyl ether', 'status and trends', 'literacy',
    'non-state actors', 'greens', 'spatial analysis', 'bicycle traffic',
    'tram', 'incineration', 'displacements', 'mode', 'e-prtr', 'oi0xx',
    'neurodevelopmental disorder', 'global consumption',
    'household energy consumption', 'qol2009', 'water watch', 'lfa',
    'flood defence', 'mollusc', 'common transport policy', 'agriculture',
    'anoxic area', 'csi034', 'ghg retrospective', 'loss of land', 'smog',
    'extreme temperatures', 'oxy-fuel combustion', 'term18', 'switzerland',
    'oi018', 'oi019', 'forest biodiversity', 'oi011', 'oi016', 'farmland',
    'organic', 'sorting waste', 'fiscal reform', 'pan-europe', 'whs6_whs7',
    'air transport', 'ozone air pollution', 'forest disturbance',
    'desertification', 'fertiliser', 'crop yield', 'fuel price',
    'ozone vegetation impacts', 'simulation-based model', 'sebi', 'ener20',
    'ener21', 'ener22', 'ener23', 'ener24', 'ener25', 'ener26', 'ener27',
    'ener28', 'ener29', 'temperature-sensitive species', 'youth audience',
    'uwwt directive', 'tourists', 'environmental information system',
    'fish005', 'fish004', 'fish003', 'environmental', 'chemicals',
    'environmental taxes', 'ice cover', 'steel', 'bioethanol', 'outlook031',
    'pvc', 'veterinary medicines', 'janez potocnik', 'outlook035', 'outlook036',
    'sf6', 'territorial cohesion', 'stavros dimas', 'annual accounts',
    'tender', 'clim', 'trade flows',
    'integrated pollution prevention and control', 'water level',
    'water resources', 'vegetation', 'petrol', 'agriculture policy', 'who',
    'future priorities', 'co2', 'off-shore structure', 'sea ice', 'macaronesia',
    'disease', 'capita', 'phenology', 'energy2008', 'atmosphere',
    'ecosystem resilience', 'benzo(a)pyrene', 'well-being', 'urban atlas',
    'industrial accident', 'tire', 'ngo', 'european neighbourhood',
    'broadleaved-coniferous forest', 'fuel', 'mortality', 'black-tailed godwit',
    'seis', 'public health', 'polar bears', 'maritime', 'ape001', 'wise',
    'eu ghg inventory', 'sustainable consumption', 'tobacco', 'defoliation',
    'megatrends', 'invasive alien species', 'taxes', 'mountain ecosystem',
    'ener001', 'amphibia', 'species richness', 'sediment', 'hydrocarbons',
    'ecological diversity', 'cryosphere', 'climate change and you (en)',
    'climate change', 'metal production', 'wetland', 'land use changes',
    'nuclear plant', 'conductivity', 'coniferous forest',
    'emissions trading scheme', 'biofuel', 'nuclear', 'droughts',
    'river basin management', 'state and outlook 2005 - part c', 'state',
    'climate change and health', 'vector data', 'point data', 'globalisation',
    'ozone health impacts', 'local emissions', 'forest thinning',
    'exotic species', 'kyoto targets', 'caretta caretta turtle', 'efficiency',
    'etr', 'ets', 'eea target audience', 'forest management', 'wir3',
    'plankton', 'oi025', 'green tax', 'co', 'oi022', 'material flow analysis',
    'environmental tax reform', 'forest ecosystem', 'biomass combustion', 'cd',
    'bioenergy crops', 'fishery', 'whs010', 'ecodrive',
    'climate action network', 'reindeer', 'development of prices',
    'western balkans', 'waste', 'consumption patterns', 'waste generation',
    'nickel', 'emission offsetting', 'natural areas protection',
    'genetically modified organism', 'determinand', 'expenditure', 'smoking',
    'common fisheries policy', 'ener35', 'integrated urban management',
    'air quality monitoring', 'ener31', 'ener30', 'urban growth',
    'seabed habitat', 'transport noise', 'rbd', 'urban area', 'carbon stock',
    'baltic sea salinity', 'fish011', 'marine ecosystems', 'site',
    'bactericide', 'citizen science', 'industrialisation', 'productivity',
    'freshwater abstraction', 'mire and swamp forest', 'radiation',
    'ee_f11', 'ee_f12', 'ee_f13', 'urban planning', 'distribution of species',
    'life expectancy', 'habitats', 'freshwater ecosystems',
    'thermophilous deciduous forest', '2010 biodiversity target',
    'eu waste types', 'power plant', 'sebi022',
    'emissions trends and projections', 'fish01b', 'fish01a', 'waste export',
    'signals 2010', 'cross-sectoral adaptation', 'rare metal', 'green economy',
    'tipping elements', 'carbon efficiency', 'enteric fermentation',
    'heating degree', 'muscle', 'ghg emission trend', 'hexachlorobenzene',
    'freshwater quality', 'costs of inaction', 'social inequalities', 'tcm',
    'fishing', 'economic policy instruments', 'wec', 'gmes', 'density',
    'residential', 'market-based instrument', 'lake', 'marine gas field',
    'flame-retardant', 'weu', 'transport emissions', 'saturation', 'msfd',
    'co2 leakage', 'sea surface temperature', 'dmc per capita',
    'nanotechnology', 'municipal waste', 'energy policy',
    'exchange of information decision', 'industrial facility', 'ozone',
    'summer ozone episode', 'terrestrial ecosystem', 'eionet-water',
    'benzene', 'habitat', 'emission unit', 'twitter', 'geospatial data',
    'employment', 'organic substances', 'transport', 'leac', 'lead',
    'public transport', 'floodplain forest', 'diffuse sources', 'summer ice',
    'solid fuels', 'food production and consumption', 'noise',
    'economic assessment', 'mobile sources', 'pressure', 'air traffic',
    'eurowaternet', 'persistent organic pollutants', 'pm10 health impacts',
    'european environment', 'sea level', 'snowline', 'ramsar', 'extreme events',
    'coastal erosion', 'reptile', 'landfilling', 'wilderness', 'mobile phone',
    'registration', 'clc technical guidelines', 'parking space',
    'begining of environmental policy', 'housing', 'heavy metals', 'reduction',
    'continental', 'greenhouse gas emission', 'bees', 'renewable energy',
    'phosphorus', 'co2 credit', 'cop15', 'bus', 'oil spill', 'construction',
    'code list', 'climate change adaption', 'hg', 'hydrometeorological hazards',
    'ape002', 'ape003', 'fragmentation', 'dmc', 'ape006', 'ape004', 'ape005',
    'ecosystem', 'flis', 'distribution', 'ecolabel', 'display', 'assessment08',
    'assessment09', 'contaminated soil', 'assessment06', 'assessment07',
    'assessment04', 'assessment05', 'ozone peak', 'air emissions', 'education',
    'nec directive', 'eper', 'oil price', 'land use',
    'emissions trading system', 'green purchasing', 'forests', 'forestry',
    'co2 emissions', 'sewer', 'policy-making', 'acidification', 'wec005',
    'marshland', 'environmental technology industry', 'waste management',
    'sustainable housing', 'sebi003', 'nutrient', 'seismic', 'forest2008',
    'exposure', 'ipcc', 'ee_f09', 'national focal point', 'eof', 'ee_f02',
    'ee_f01', 'ee_f07', 'ee_f06', 'ee_f05', 'ee_f04', 'hnv',
    'green architecture', 'biotechnology', 'hazardous waste'])

logger = logging.getLogger('Products.EEAPloneAdmin')


def _fixUnicodeKeywords(brain, catalog):
    """ Fix unicode keywords
    """
    try:
        doc = brain.getObject()
    except AttributeError:
        logger.warn('Uncatalog broken brain %s', brain.getURL())
        catalog.uncatalog_object(catalog.getpath(brain.data_record_id_))
        return
    else:
        doc.reindexObject(idxs=['Subject'])
        return doc


def fixUnicodeKeywords(self):
    """ Fix unicode keywords
    """
    site = getSite()
    catalog = getToolByName(site, 'portal_catalog')

    tags = catalog.Indexes.get('Subject').uniqueValues()
    tags = [tag for tag in tags if isinstance(tag, unicode)]

    brains = catalog(Subject={'query': tags, 'operator': 'or'},
                     Language='all', showInactive=True)
    total = len(brains)

    logger.info('Fixing unicode keywords for %s documents...', total)

    step = 1
    for index, brain in enumerate(brains):
        try:
            fixed = _fixUnicodeKeywords(brain, catalog)
        except Exception as err:
            logger.warn("ERROR: %s", brain.getURL())
            logger.exception(err)
            continue

        if not fixed:
            continue

        step += 1
        if step % 100 == 0:
            logger.info('Fixing keywords...%s/%s', index, total)
            transaction.commit()

    msg = "Fixing unicode keywords for %s documents... DONE" % total
    logger.info(msg)
    return msg

def _fixKeywords(brain, catalog):
    """ Fix keywords
    """
    try:
        doc = brain.getObject()
    except AttributeError:
        logger.warn('Uncatalog broken brain %s', brain.getURL())
        catalog.uncatalog_object(catalog.getpath(brain.data_record_id_))
        return

    canonical = doc.getCanonical()
    original = canonical.getField('subject').getAccessor(canonical)()
    original = [tag for tag in original if tag.lower() in allowed]

    mine = set(brain.Subject)
    if set(mine).symmetric_difference(original):
        doc.getField('subject').getMutator(doc)(original)
        doc.reindexObject(idxs=['Subject'])
        return doc
    return None


def fixKeywords(self):
    """ Fix language independent keywords
    """
    site = getSite()
    catalog = getToolByName(site, 'portal_catalog')

    tags = catalog.Indexes.get('Subject').uniqueValues()
    tags = [tag for tag in tags if tag.lower() not in allowed]

    brains = catalog(Subject={'query': tags, 'operator': 'or'},
                     Language='all', showInactive=True)
    total = len(brains)

    logger.info('Fixing keywords for %s documents...', total)

    step = 1
    for index, brain in enumerate(brains):
        try:
            fixed = _fixKeywords(brain, catalog)
        except Exception as err:
            logger.warn("ERROR: %s", brain.getURL())
            logger.exception(err)
            continue

        if not fixed:
            continue

        step += 1
        if step % 100 == 0:
            logger.info('Fixing keywords...%s/%s', index, total)
            transaction.commit()

    msg = "Fixing keywords for %s documents... DONE" % total
    logger.info(msg)
    return msg


def fixRussianKeywords(self):
    """ Fix Russian keywords
    """
    site = getSite()
    catalog = getToolByName(site, 'portal_catalog')

    subject = catalog.Indexes.get('Subject')
    tags = subject.uniqueValues()
    tags = [tag for tag in tags if tag.lower() not in allowed]

    brains = catalog(Subject={'query': tags, 'operator': 'or'},
                     Language='all', showInactive=True)
    total = len(brains)

    logger.info('Fixing keywords for %s documents...', total)
    for brain in brains:
        logger.info('Reindex object %s', brain.getURL())
        doc = brain.getObject()
        doc.reindexObject(idxs=['Subject'])

        logger.info('Forcing index cleanup of tags %s', tags)
        subject.unindex_objectKeywords(brain.data_record_id_, tags)

    msg = "Fixing keywords for %s documents... DONE" % total
    logger.info(msg)
    return msg
