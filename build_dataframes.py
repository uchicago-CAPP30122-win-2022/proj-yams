import geopandas as gpd
import pandas as pd
import geo_comm_areas as gca

comm_areas = gca.get_geo_comm_areas()
# comm area max of 77, min of 1, len of 77

perm_df = gpd.read_file("data/permits.geojson")
# reading in geocoded building permits
# permits have community area numbers, but no names

# working on the the comm_areas 
demo_perm_df, build_perm_df = gca.geojoin_permits(comm_areas, perm_df)
comm_areas = gca.merge_permits_ca(comm_areas, demo_perm_df, build_perm_df)
census_ca = gca.get_ca_census()
comm_areas = gca.normalize_permit_counts(comm_areas, census_ca)

"""
    finished datasets from the above functions

    demo_perm_df:
        A geopandas dataframe of length 18821
        Contains the geocoded permits for "WRECKING/DEMOLITION" with filled
        in community area numbers for permits originally missing it


    build_perm_df:
        A geopandas dataframe of length 25201
        Contains the geocoded permits for "NEW CONSTRUCTION" with filled
        in community area numbers for permits originally missing it


    census_ca
        A pandas dataframe, with census data on population, race and
        housing for each of Chicago's 77 community areas


    comm_areas:
        A pandas dataframe, with rows for each of Chicago's 77 community areas

        Columns of note:
            'vac_rate': vacant homes divided by total housing units
            'demo_rate': number of demolitions per capita, whole time period
            'build_rate': number of new builds per capita, whole time period
            'build_per_demo': ratio of new buildings to demos
            'ave_build_val': average value of new construction
            'change_rate': difference in build_rate and demo_rate

"""

build_year_count, demo_year_count, build_year_val = gca.permits_per_year(
    comm_areas, build_perm_df, 10000, demo_perm_df, 10000)

"""

    build_year_count

        A pandas dataframe, with rows for each of Chicago's 77 community areas
        with new builds per 10,000 people, per year
    
    demo_year_count

        A pandas dataframe, with rows for each of Chicago's 77 community areas
        with demos per 10,000 people, per year

    build_year_val

        A pandas dataframe, with rows for each of Chicago's 77 community areas
        with built value per capita, per year

"""