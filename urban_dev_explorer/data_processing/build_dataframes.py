import geopandas as gpd
import pandas as pd
import data_processing.geo_comm_areas as gca # this is correct, ignore pylance
import data_processing.util as util         # this is correct, ignore pylance


def run_merge(csv_name, testing=False):
    '''
    Merges all available pandas data sets into one and saves the result
      into a csv file.

    Inputs: 
      csv_name: name of csv file that will contain merged dataset.
      testing: (bool) if the value is True, progress statements will be printed.
    '''

    build_year_count, demo_year_count, census, crime, grocery, socio = load_data(testing)

    if testing:
        print('The following datasets are about to be merged:')
        print('buildings built \nbuildings demolished')
        print('census demographics data \ncrimes per year \ngrocery stores')
        print('socio-conomic indicators')

    #merge building permits data
    build_demo = build_year_count.merge(demo_year_count[\
        ['Number demolished per 10,000 people']], how = 'left', on =['area_num', 'year'])
    build_demo['Number demolished per 10,000 people'] = \
        build_demo['Number demolished per 10,000 people'].replace(0, 1)
    build_demo['build ratio'] = build_demo['Number built per 10,000 people']/\
        build_demo['Number demolished per 10,000 people']

    #merge building permits data with census data
    build_demo = build_demo.merge(census, how= 'left', on = ['area_num', 'year'])
    build_demo = build_demo.reset_index()
    build_demo['area_num'] = build_demo['area_num'].astype(str)

    #merge the three dataframes for crime, grocery stores, and socio-economic indicators    
    cgs_data = crime.merge(grocery, how= 'left', on = ['area_num', 'year']).\
        merge(socio, how= "left", on = ['area_num', 'year'])

    merged_df = build_demo.merge(cgs_data, how= 'left', on = ['area_num', 'year'])
    
    if testing:
        print(f'Merge successful: saving the merged dataset into a csv file named "{csv_name}"')

    #create csv file containing merged data
    merged_df.to_csv(csv_name) 


def load_data(testing=False):
    '''
    Loads datasets. 

    Inputs: 
      testing: (bool) if True, progress statements will be printed while loading data.

    Returns (tuple): pandas data frames
    '''

    # reading in precreated geocoded building permits
    perm_df = gpd.read_file("urban_dev_explorer/data/permits.geojson")

    # loading community areas geodataframe from API
    comm_areas = gca.get_geo_comm_areas()

    # loading community areas census data from API
    census_ca = gca.get_ca_census()

    demo_perm_df, build_perm_df = gca.geojoin_permits(comm_areas, perm_df)
    comm_areas = gca.merge_permits_ca(comm_areas, demo_perm_df, build_perm_df)
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

    build_year_count, demo_year_count, _ = gca.permits_per_year(
        comm_areas, build_perm_df, 10000, demo_perm_df, 10000)

    if testing:
        print('Reading in buildings built data now...')
        print(f'buildings built data shape: {build_year_count.shape}\n')

        print('Reading in buildings demolished data now...')
        print(f'buildings demolished data shape: {demo_year_count.shape}\n')

        print('Reading in census demographics data now...')
        print(f'census demographics data shape: {census_ca.shape}\n')

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

    #transpose building permit data, remove 'geometry' col, rename 'value' col
    build_year_count = util.melt_permit_data(build_year_count).drop(['geometry'], axis=1)
    build_year_count = build_year_count.rename(columns= \
        {'value': 'Number built per 10,000 people'})

    demo_year_count = util.melt_permit_data(demo_year_count)
    demo_year_count = demo_year_count.rename(columns= \
        {'value': 'Number demolished per 10,000 people'})

    #modify census data to merge with other datasets 
    census = census_ca[['area_num', 'vac_rate', 'hisp_per', 'white_per', \
        'black_per', 'asian_per']]
    census['year'] = '2010'
    census = census.set_index(['area_num', 'year'])

    #import 3 processed pandas data frames
    crime, grocery, socio = util.generate_crime_grocery_socio_dfs(testing)

    return build_year_count, demo_year_count, census, crime, grocery, socio
