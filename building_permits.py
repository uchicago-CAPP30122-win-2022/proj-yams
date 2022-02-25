import requests
import json
import pandas as pd
import geopandas as gpd
from sodapy import Socrata
import geopy
from geopy.extra.rate_limiter import RateLimiter
from geopy.geocoders import Nominatim
from geopy.geocoders import GoogleV3
import matplotlib

permit_types = ("PERMIT - WRECKING/DEMOLITION", "PERMIT - NEW CONSTRUCTION")
cols = """ID, PERMIT_, PERMIT_TYPE, REVIEW_TYPE, APPLICATION_START_DATE, 
ISSUE_DATE, PROCESSING_TIME, STREET_NUMBER, STREET_DIRECTION, STREET_NAME, 
SUFFIX, WORK_DESCRIPTION, REPORTED_COST, SUBTOTAL_PAID, COMMUNITY_AREA, 
CENSUS_TRACT, WARD, XCOORDINATE, YCOORDINATE, LATITUDE, LONGITUDE, LOCATION"""


client = Socrata("data.cityofchicago.org", "goD601SLndI51xcMq1KsnG6np", username = "marcdloeb@gmail.com", password = "2522-Haphazard")
permit_results = client.get("ydr8-5enu", where = f'PERMIT_TYPE in {permit_types}', 
                    select = cols, limit=500)
permit_df = pd.DataFrame.from_records(permit_results)
# don't worry Marc you get the demolitions too, they just appear later
# 44343 total

demo_results = client.get("ydr8-5enu", where = 'permit_type = "PERMIT - WRECKING/DEMOLITION"', 
                    select = cols, limit=20000)
demo_df = pd.DataFrame.from_records(demo_results)
# total 18929

build_results = client.get("ydr8-5enu", where = 'permit_type = "PERMIT - NEW CONSTRUCTION"', 
                    select = cols, limit=30000)
build_df = pd.DataFrame.from_records(build_results)
# total 25414





col_names = {"id": "id", "permit_": "num", "permit_type": "type", 
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


# reading in community areas
ca_url = "https://data.cityofchicago.org/api/geospatial/cauq-8yn6?method=export&format=GeoJSON"
comm_areas = gpd.read_file(ca_url)


# Spatial join