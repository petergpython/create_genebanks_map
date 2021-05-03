#!/usr/bin/env python
# coding: utf-8

######### import libraries
import matplotlib.pyplot as plt
import pandas as pd
import geopandas as gpd
import numpy as np

# load data from FAO-WIEWS fromt the Data folder
institutes = pd.read_csv('../Data/organizations_wiews_21_04_2021.csv')

# small function to correct some coordinate format
def convert_strings_to_coordinates(coord):
    """
    convert geographical coordinates into floats when these are strings
    if it can't convert to float it returns a NaN value
    """
    if type(coord) == str:
        try:
            coord = float(coord)
            return coord
        except:
            return np.nan
    else:
        return coord


### create a binary variable only for genebank
institutes['Genebank'] = institutes['Organization role categories'].str.contains('Genebank', case = False , regex = False)
genebanks = institutes[institutes['Genebank'] == True]
genebanks = genebanks[~ genebanks['Longitude (decimal degrees format)'].isnull()] # drop genebanks without coordinates
genebanks['Latitude (decimal degrees format)'] = genebanks['Latitude (decimal degrees format)'].apply(convert_strings_to_coordinates)
genebanks['Longitude (decimal degrees format)'] = genebanks['Longitude (decimal degrees format)'].apply(convert_strings_to_coordinates)

#### create geodataframe merging insituttes dataframe with world shapefile, world shapefile can be easily found online
world_shapefile = '/GIS_files/ne_50m_admin_0_countries/ne_50m_admin_0_countries.shp'
world = gpd.read_file(world_shapefile)
world.crs = {'init' :'epsg:4326'}   # 4 make sure the crs is right

## ###### 2 trasform dataframe in geoDataFrame by using lat and long as geometry for the GeoDataFrame
points_genebanks = gpd.points_from_xy(genebanks['Longitude (decimal degrees format)'], genebanks['Latitude (decimal degrees format)'])
genebank_gdf = gpd.GeoDataFrame(genebanks , geometry= points_genebanks)
genebanks_on_world = gpd.sjoin(genebank_gdf, world, how='inner',op='within' )
genebanks_on_world.crs = {'init' :'epsg:4326'}  # 4 make sure you specify the CRS before reporjecting to another CRS
genebanks_on_world = genebanks_on_world.to_crs('+proj=wintri')   #### reprojecting to  WINKEL TRIPEL projection
world = world.to_crs('+proj=wintri') #### reprojecting to  WINKEL TRIPEL projection
basemap =world.plot(figsize = (60, 40), color = '#eae0e0', edgecolor = 'grey' )  #color manually specified using hexvalues
basemap.set_facecolor('xkcd:white')
genebanks_on_world.plot(ax = basemap, color = '#d95f02' , markersize = 10)  #color manually specified using hexvalues
plt.axis('off') # switch off axis
plt.savefig('Maps_genebanks.jpg', dpi = 300, pad_inches=0, bbox_inches = 'tight') #save figure in working directory
