import requests
import json
import pandas as pd
import geopandas as gpd
from sodapy import Socrata
import geopy
from geopy.extra.rate_limiter import RateLimiter
from geopy.geocoders import Nominatim
from geopy.geocoders import GoogleV3
import shapely
from shapely.geometry import shape

permit_types = ("PERMIT - WRECKING/DEMOLITION", "PERMIT - NEW CONSTRUCTION")
cols = '''"ID", "PERMIT#", "PERMIT_TYPE", "REVIEW_TYPE", "APPLICATION_START_DATE", 
    "ISSUE_DATE", "PROCESSING_TIME", "STREET_NUMBER", "STREET_DIRECTION", 
    "STREET_NAME", "SUFFIX", "WORK_DESCRIPTION", "REPORTED_COST", 
    "SUBTOTAL_PAID", "COMMUNITY_AREA", "CENSUS_TRACT", "WARD", 
    "XCOORDINATE", "YCOORDINATE", "LATITUDE", "LONGITUDE", "LOCATION"'''


client = Socrata("data.cityofchicago.org", "goD601SLndI51xcMq1KsnG6np", username = "marcdloeb@gmail.com", password = "2522-Haphazard")
#results = client.get("ydr8-5enu", where = f'permit_type in {permit_types}', 
#                    select = 'ID, PERMIT#', limit=500)
permit_results = client.get("ydr8-5enu", where = f'permit_type in {permit_types}', limit=500)
perm_df = pd.DataFrame.from_records(permit_results)

#response = requests.get("https://data.cityofchicago.org/resource/ydr8-5enu.json")
#permits = response.json()       #seemingly isn't json data????
#perm_df = pd.DataFrame(permits)

cols_list = ["id", "permit#", "permit_type", "review_type", "application_start_date", 
    "issue_date", "processing_time", "street_number", "street_direction", 
    "street_name", "suffix", "work_description", "reported_cost", 
    "subtotal_paid", "community_area", "census_tract",  "ward", 
    "xcoordinate", "ycoordinate", "latitude", "longitude", "location"]
col_names = {"id": "id", "permit#": "num", "permit_type": "type", 
    "review_type": "review", "application_start_date": "app_date", 
    "issue_date": "issue_date", "processing_time": "proc_time", 
    "street_number": "st_num", "street_direction": "st_dir", 
    "street_name": "st_name", "suffix": "st_suffix", 
    "work_description": "work_desc", "reported_cost": "work_cost", 
    "subtotal_paid": "permit_fees", "community_area": "comm_area", 
    "census_tract": "tract", "ward": "ward", "xcoordinate": "xcoord", 
    "ycoordinate": "ycoord", "latitude": "lat", "longitude": "lon", 
    "location": "location"}
perm_df = perm_df.filter(cols_list).rename(columns = col_names)

#checking street address columns for na
street_cols = ["st_num", "st_dir", "st_name", "st_suffix"]
for col in street_cols: 
    perm_df = perm_df[perm_df[col].notna()]

# creating single street address column
perm_df['st_addr'] = perm_df[street_cols].astype(str).agg(' '.join, axis=1) + " Chicago IL"

perm_df_nogeo = perm_df[perm_df["loc"].isna()]
perm_df_geo = perm_df[perm_df["loc"].notna()]

# geocoding
#test_addr = "2946 N HOYNE AVE Chicago IL"
#test_code = Nominatim(user_agent = "marc_cs_proj").geocode(test_addr)

locator = Nominatim(user_agent="marc_cs_proj")
geocode = RateLimiter(locator.geocode, min_delay_seconds=1)

for i, vals in perm_df_nogeo.iterrows():
    print(i)
    gcode = geocode(vals.st_addr)

    if gcode:
        perm_df_nogeo.loc[i, "lat"] = gcode.latitude
        perm_df_nogeo.loc[i, "lon"] = gcode.longitude
        # changed it to :, (i, "lon"), but that made it even worse
        print(gcode.latitude, gcode.longitude)

perm_df_coded = pd.concat([perm_df_nogeo, perm_df_geo], axis=0)

geo_perm_df = gpd.GeoDataFrame(
    perm_df_coded, geometry=gpd.points_from_xy(perm_df_coded.lon, perm_df_coded.lat))








# spatial joint to community area level
ca_results = client.get("igwz-8jzy")

comm_area = gpd.GeoDataFrame.from_records(ca_results)

gpd.read_file(ca_results)


# get a "Must have equal len keys and value when setting with an iterable" error on 75
# but it runs straight through when I run it a second time
for i, vals in comm_area.iterrows():
    print(i)
    #print(vals.the_geom)
    comm_area.loc[i, "new_geom"] = shape(vals.the_geom)

comm_area = gpd.GeoDataFrame(comm_area, geometry = "new_geom")


ct_results = 


"""

Depreciated

perm_df_nogeo["geocode"] = perm_df_nogeo['st_addr'].apply(geocode)

perm_df_nogeo = perm_df_nogeo[perm_df_nogeo["geocode"].notna()]

# getting a weird warning from this
perm_df_nogeo['lat'] = perm_df_nogeo['geocode'].apply(
    lambda code: code.latitude if code else None)
perm_df_nogeo['lon'] = perm_df_nogeo['geocode'].apply(
    lambda code: code.longitude if code else None)

comm_area = gpd.GeoDataFrame(pd.DataFrame.from_records(ca_results), geometry = "the_geom")
comm_area = gpd.GeoDataFrame.from_records(ca_results).set_geometry(col = "the_geom")
#"Input must be valid geometry objects" error (for both of the above)
comm_area = pd.DataFrame.from_records(ca_results)
comm_area = gpd.GeoDataFrame.from_records(ca_results, geometry = "the_geom")
comm_area = gpd.read_file("https://data.cityofchicago.org/resource/igwz-8jzy.json")
#None of these work


"""