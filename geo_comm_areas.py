import geopandas as gpd
import pandas as pd

# reading in community areas
ca_url = "https://data.cityofchicago.org/api/geospatial/cauq-8yn6?method=export&format=GeoJSON"
comm_areas = gpd.read_file(ca_url)
comm_areas = comm_areas.filter(
    ["community", "area_num_1", "geometry"]).rename(
        columns={"area_num_1": "area_num"}).astype({"area_num": 'int16'})
# comm area max of 77, min of 1, len of 77

# reading in geocoded building permits
perm_df = gpd.read_file("permits.geojson")

# Spatial join
#comm_areas.crs
    # EPSG:4326
#perm_df.crs
    #EPSG:4326

perm_df_noca = perm_df[perm_df["comm_area"].isna()]
# len 8969
perm_df_wca = perm_df[perm_df["comm_area"].notna()]
# len 35075

# spatial join to find comm area for permits missing it
perm_df_noca = gpd.sjoin(perm_df_noca, comm_areas, how="inner", op="within")
perm_df_noca = perm_df_noca.drop(columns=["comm_area"])
perm_df_noca = perm_df_noca.rename(columns={
    "area_num": "comm_area", "community": "ca_name"})

perm_df_coded = pd.concat([perm_df_wca, perm_df_noca], axis=0)
perm_df_coded = perm_df_coded.astype({"comm_area": 'int16'})
# len 44024
# still has a max comm area of 77, min of 0
# two records with 0 (see groupby below)
# no 0 in either perm_df_noca or in perm_df_wca. No idea how the 0 go in

demo_perm_df = perm_df_coded[
    perm_df_coded.perm_type == "PERMIT - WRECKING/DEMOLITION"]
build_perm_df = perm_df_coded[
    perm_df_coded.perm_type == "PERMIT - NEW CONSTRUCTION"]

# merging count of demos and builds per community area into comm area
demo_count = demo_perm_df.groupby(by=["comm_area"]).size().reset_index()
demo_count = demo_count.rename(columns={0: "demos"})
build_count = build_perm_df.groupby(by=["comm_area"]).size().reset_index()
build_count = build_count.rename(columns={0: "builds"})
comm_areas = comm_areas.merge(demo_count,
                        left_on='area_num', right_on='comm_area')
comm_areas = comm_areas.merge(build_count,
                        left_on='area_num', right_on='comm_area')
comm_areas = comm_areas.drop(columns=["comm_area_x", "comm_area_y"])

# reading in comm area census data, calculating race percent and vacancy rate
census_url = "https://datahub.cmap.illinois.gov/dataset/1d2dd970-f0a6-4736-96a1-3caeb431f5e4/resource/0916f1de-ae37-4476-bf4e-6485ba08c975/download/Census2020SupplementCCA.csv"
census_ca = pd.read_csv(census_url)
census_ca = census_ca.rename(columns=str.lower).rename(columns={
    "geoid": "area_num", "hu_tot": "total_homes", "vac_hu": "vac_homes"})
census_ca["vac_rate"] = 100 * census_ca.vac_homes / census_ca.total_homes
census_ca["hisp_per"] = 100 * census_ca.hisp / census_ca.tot_pop
census_ca["white_per"] = 100 * census_ca.white / census_ca.tot_pop
census_ca["black_per"] = 100 * census_ca.black / census_ca.tot_pop
census_ca["asian_per"] = 100 * census_ca.asian / census_ca.tot_pop

comm_areas = comm_areas.merge(census_ca, on="area_num")
comm_areas = comm_areas.drop(columns="geog")

# building and demolition rate
comm_areas["demo_rate"] = comm_areas.demos / comm_areas.tot_pop
comm_areas["build_rate"] = comm_areas.builds / comm_areas.tot_pop
comm_areas["build_per_demo"] = comm_areas.builds/comm_areas.demos

comm_areas.sort_values(by = ["demo_rate"], ascending=False)
comm_areas.sort_values(by = ["build_rate"], ascending=False)
comm_areas.sort_values(by = ["build_per_demo"], ascending=False)

comm_areas.to_file("ca_w_perm_count.geojson", driver='GeoJSON')

demo_perm_df.to_file("demo_perm.geojson", driver='GeoJSON')
# 18821
build_perm_df.to_file("new_build_perm.geojson", driver='GeoJSON')
# 25203