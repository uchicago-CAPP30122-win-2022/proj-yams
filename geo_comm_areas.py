import geopandas as gpd
import pygeos
import pandas as pd

# reading in community areas
ca_url = "https://data.cityofchicago.org/api/geospatial/cauq-8yn6?method=export&format=GeoJSON"
comm_areas = gpd.read_file(ca_url)

# reading in geocoded building permits
perm_df = gpd.read_file("permits.geojson")

# Spatial join
#comm_areas.crs
    # EPSG:4326
#perm_df.crs
    #EPSG:4326

comm_areas = comm_areas.filter(["community", "area_num_1", 'geometry'])
perm_df_noca = perm_df[perm_df["comm_area"].isna()]
# len 8969
perm_df_wca = perm_df[perm_df["comm_area"].notna()]
# len 35075

# spatial join to find comm area for permits missing it
perm_df_noca = gpd.sjoin(perm_df_noca, comm_areas, how="inner", op="within")
perm_df_noca = perm_df_noca.drop(columns=["comm_area"])
perm_df_noca = perm_df_noca.rename(columns={
    "area_num_1": "comm_area", "community": "ca_name"})

perm_df_coded = pd.concat([perm_df_wca, perm_df_noca], axis=0)
# len 44024
# perm_df_coded[perm_df_coded.comm_area.isna()]

demo_perm_df = perm_df_coded[
    perm_df_coded.perm_type == "PERMIT - WRECKING/DEMOLITION"]
build_perm_df = perm_df_coded[
    perm_df_coded.perm_type == "PERMIT - NEW CONSTRUCTION"]

demo_perm_df.to_file("demo_perm.geojson", driver='GeoJSON')
build_perm_df.to_file("build_perm.geojson", driver='GeoJSON')

# merging count of demos and builds per community area into comm area
comm_areas = comm_areas.rename(columns = {"area_num_1": "comm_area"})

demo_count = demo_perm_df.groupby(by=["comm_area"]).size().reset_index()
demo_count = demo_count.rename(columns = {0: "demos"})
build_count = build_perm_df.groupby(by=["comm_area"]).size().reset_index()
build_count = build_count.rename(columns = {0: "builds"})

comm_areas = comm_areas.merge(demo_count, on='comm_area')