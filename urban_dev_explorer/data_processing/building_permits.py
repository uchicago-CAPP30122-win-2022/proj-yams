#import requests
#import json
import pandas as pd
import geopandas as gpd
from sodapy import Socrata
import geopy
from geopy.extra.rate_limiter import RateLimiter
from geopy.geocoders import Nominatim

def get_pemits(testing=False, save_name="permits_new.geojson", rec_limit=45000):
    """
    Uses the Socrata API to access the Chciago Open Data Portal's database
    of building permits from 2006 to the present.
    
    Returns:
        perm_df: A Pandas dataframe with 
    """

    permit_types = ("PERMIT - WRECKING/DEMOLITION", "PERMIT - NEW CONSTRUCTION")
    cols = """ID, PERMIT_, PERMIT_TYPE, APPLICATION_START_DATE,
    STREET_NUMBER, STREET_DIRECTION, STREET_NAME, SUFFIX, WORK_DESCRIPTION,
    REPORTED_COST, COMMUNITY_AREA, CENSUS_TRACT, XCOORDINATE, YCOORDINATE,
    LATITUDE, LONGITUDE, LOCATION"""

    client = Socrata("data.cityofchicago.org", "goD601SLndI51xcMq1KsnG6np")

    permit_results = client.get("ydr8-5enu",
                                where=f'PERMIT_TYPE in {permit_types}',
                                select=cols, limit=rec_limit)
    perm_df = pd.DataFrame.from_records(permit_results)

    col_names = {"ID": "id", "PERMIT_": "perm_num", "PERMIT_TYPE": "perm_type",
            "APPLICATION_START_DATE": "app_date", "STREET_NUMBER": "st_num",
            "STREET_DIRECTION": "st_dir", "STREET_NAME": "st_name",
            "SUFFIX": "st_suffix", "WORK_DESCRIPTION": "work_desc",
            "REPORTED_COST": "work_cost", "COMMUNITY_AREA": "comm_area",
            "CENSUS_TRACT": "tract", "XCOORDINATE": "xcoord",
            "YCOORDINATE": "ycoord", "LATITUDE": "lat", "LONGITUDE": "lon",
            "LOCATION": "location"}
    perm_df = perm_df.rename(columns=col_names)

    # checking street address columns for na
    street_cols = ["st_num", "st_dir", "st_name", "st_suffix"]
    for col in street_cols: 
        perm_df = perm_df[perm_df[col].notna()]

    # creating single street address column
    perm_df['st_addr'] = perm_df[street_cols].astype(str).agg(
                                        ' '.join, axis=1) + " Chicago IL"

    perm_df_nogeo = perm_df[perm_df["location"].isna()]
    perm_df_geo = perm_df[perm_df["location"].notna()]

    if testing:
        print(f"There are {len(perm_df_nogeo)} records without coordinates")

    # geocoding
    locator = Nominatim(user_agent="marc_cs_proj")
    geocode = RateLimiter(locator.geocode, min_delay_seconds=1)

    for i, entry in perm_df_nogeo.iterrows():
        if testing:
            print(f"\nentry number: {i}, permit number: {entry.perm_num}")
            print(f"street address: {entry.st_addr}")
        gcode = geocode(entry.st_addr)

        if gcode:
            perm_df_nogeo.loc[i, "lat"] = gcode.latitude
            perm_df_nogeo.loc[i, "lon"] = gcode.longitude
            if testing:
                print(f"lat: {gcode.latitude}, lon: {gcode.longitude}")

        elif testing:
            print("not a valid address")

    perm_df_nogeo = perm_df_nogeo[perm_df_nogeo.lat.notna()]
    perm_df_coded = pd.concat([perm_df_nogeo, perm_df_geo], axis=0)

    # creating a geodataframe, converting lat and lon into coords
    geo_perm_df = gpd.GeoDataFrame(
        perm_df_coded, geometry=gpd.points_from_xy(
            perm_df_coded.lon, perm_df_coded.lat))

    geo_perm_df.to_file(save_name, driver='GeoJSON')
