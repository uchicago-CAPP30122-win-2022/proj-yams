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
#build_year_count, demo_year_count, build_year_val = gca.permits_per_year(
#                                    comm_areas, build_perm_df, demo_perm_df)

pop = comm_areas[['community', 'area_num', 'geometry', 'tot_pop']]

# new construction per year per 1000 people
build_year_count = build_perm_df.groupby(by=["comm_area", "year"]).size().unstack()
build_year_count = gca.per_capita(build_year_count, pop, 1000)

# demolition per year per 1000 people
demo_year_count = demo_perm_df.groupby(by=["comm_area", "year"]).size().unstack()
demo_year_count = gca.per_capita(demo_year_count, pop, 1000)

# new construction value per year
build_year_val = build_perm_df.groupby(by=["comm_area", "year"])["work_cost"].sum().unstack()
build_year_val = gca.per_capita(build_year_val, pop, 1)

"""
    finished datasets from the above functions

    demo_perm_df

        A geopandas dataframe of length 18821
        Contains the geocoded permits for "WRECKING/DEMOLITION" with filled
        in community area numbers for permits originally missing it


    build_perm_df

        A geopandas dataframe of length 25201
        Contains the geocoded permits for "NEW CONSTRUCTION" with filled
        in community area numbers for permits originally missing it


    census_ca

        A pandas dataframe, with census data on population, race and
        housing for each of Chicago's 77 community areas


    comm_areas

        A pandas dataframe, with rows for each of Chicago's 77 community areas

        Columns of note:
            'demo_rate'
            'build_rate'
            'build_per_demo'
            'ave_build_val'
            'change_rate'

    build_year_count, demo_year_count, 




"""