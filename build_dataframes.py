import geopandas as gpd
import pandas as pd
import geo_comm_areas as gca

comm_areas = gca.get_geo_comm_areas()
# comm area max of 77, min of 1, len of 77

perm_df = gpd.read_file("data/permits.geojson")
# reading in geocoded building permits
# permits have community area numbers, but no names

demo_perm_df, build_perm_df = gca.geojoin_permits(comm_areas, perm_df)

comm_areas = gca.merge_permits_ca(comm_areas, demo_perm_df, build_perm_df)

census_ca = gca.get_ca_census()

comm_areas = gca.normalize_permit_counts(comm_areas, census_ca)

build_year_count, demo_year_count = gca.permits_per_year(comm_areas, census_ca)