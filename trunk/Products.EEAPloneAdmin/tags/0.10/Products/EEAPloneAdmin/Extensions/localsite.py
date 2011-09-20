# High priority content for translations
forTranslation = ('/www/SITE/signals/galleries', '/www/SITE/signals/galleries/climate-refugees', 
'/www/SITE/signals/galleries/climate-refugees/living-on-the-edge', 
'/www/SITE/signals/galleries/climate-refugees/the-coastline-is-disappearing', 
'/www/SITE/signals/galleries/climate-refugees/protecting-the-coastline', 
'/www/SITE/signals/galleries/climate-refugees/eyewitness-ruhul-khan', 
'/www/SITE/signals/galleries/climate-refugees/climate-refugee-basand-jana', 
'/www/SITE/signals/galleries/climate-refugees/embankments-on-sagar-island', 
'/www/SITE/signals/galleries/climate-refugees/fish-breeding', '/www/SITE/signals/galleries/climate-refugees/water-scarcity', 
'/www/SITE/signals/galleries/climate-refugees/children-on-mousini-island', 
'/www/SITE/signals/galleries/climate-refugees/destructive-climate', '/www/SITE/signals/galleries/climate-refugees/loss-of-land', 
'/www/SITE/signals/galleries/farming-with-nature', '/www/SITE/signals/galleries/farming-with-nature/harvesting', 
'/www/SITE/signals/galleries/farming-with-nature/la-vialla', '/www/SITE/signals/galleries/farming-with-nature/brothers', 
'/www/SITE/signals/galleries/farming-with-nature/shot-of-compost-being-spread', 
'/www/SITE/signals/galleries/farming-with-nature/green-manure', '/www/SITE/signals/galleries/farming-with-nature/composting', 
'/www/SITE/signals/galleries/farming-with-nature/town_signs', '/www/SITE/signals/galleries/farming-with-nature/their-own-plot', 
'/www/SITE/signals/galleries/farming-with-nature/mouu', '/www/SITE/signals/galleries/farming-with-nature/sheep', 
'/www/SITE/signals/galleries/farming-with-nature/cloughjordan-community-farm', '/www/SITE/signals/galleries/the-arctic', 
'/www/SITE/signals/galleries/the-arctic/arctic', '/www/SITE/signals/galleries/the-arctic/dripping-iceberg', 
'/www/SITE/signals/galleries/the-arctic/aerial-view', '/www/SITE/signals/galleries/the-arctic/dines-and-dogs', 
'/www/SITE/signals/galleries/the-arctic/long-shot-of-dines-on-ice', 
'/www/SITE/signals/galleries/the-arctic/dines-and-close-up-of-dog', 
'/www/SITE/signals/galleries/the-arctic/dines-with-tourist-boat', '/www/SITE/signals/galleries/the-arctic/dines-pointing-a-gun', 
'/www/SITE/signals/galleries/the-arctic/seal-pelts', '/www/SITE/signals/galleries/the-arctic/dines-and-tourists-eating-outside', 
'/www/SITE/signals/galleries/the-arctic/dsitant-fishing-boat', '/www/SITE/signals/galleries/the-arctic/dines-smiling', 
'/www/SITE/signals/galleries/designing-the-future', '/www/SITE/signals/galleries/designing-the-future/green-houseboat', 
'/www/SITE/signals/galleries/designing-the-future/houseboats', '/www/SITE/signals/galleries/designing-the-future/fishing-rods', 
'/www/SITE/signals/galleries/designing-the-future/greenhouse', '/www/SITE/signals/galleries/designing-the-future/role-of-water', 
'/www/SITE/signals/galleries/designing-the-future/amphibious-houses', 
'/www/SITE/signals/galleries/designing-the-future/the-levy',)

from Products.XLIFFMarshall.Extensions.export import exportPaths2SingleFile

def exportForTranslation(context, **kwargs):
    return exportPaths2SingleFile(context,forTranslation, context.REQUEST, **kwargs)

    
