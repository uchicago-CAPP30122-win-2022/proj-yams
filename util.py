from http.client import REQUESTED_RANGE_NOT_SATISFIABLE
import pandas as pd
from sodapy import Socrata


id_dict = {
    "socioeconomic indicators": "kn9c-c2s2",
    "crimes": "ijzp-q8t2", "grocery stores": "4u6w-irs9"}


def generate_crime_grocery_socio_dfs():
    '''
    Pull all data sets from the City of Chicago portal using API and returned cleaned datasets.
    
    Return:
      merged pandas dataframe containing all the data from the dict 
    '''

    return process_crime(id_dict['crimes']), \
            process_grocery_stores(id_dict['grocery stores']), \
            process_socio_indicators(id_dict['socioeconomic indicators'])


def pull_data(dataset_id, lim):
    '''
    Given a dataset id, pull out data from Chicago portal API

    Inputs:
      dataset_id: (str) a unique id for one Chicago portal dataset
      lim: (int) number of rows to pull each time, default to None

    Return:
      (Pandas DataFrame) a dataframe pulled from Chicago Portal
    '''

    client = Socrata("data.cityofchicago.org", "goD601SLndI51xcMq1KsnG6np")

    #special case to pull crimes data: filtering for homocide crimes
    if dataset_id == id_dict["crimes"]:
        results = client.get(id_dict["crimes"], where = f"(primary_type) = 'HOMICIDE'",
                    limit=1000000)        
    else:
        results = client.get(dataset_id, limit= lim)
    
    return pd.DataFrame.from_records(results)


def process_crime(dataset_id):
    '''
    Helper function to clean crime dataset

    Returns pandas df
    '''
    crime_df = pull_data(dataset_id, None)

    #summarize data by community area and year & replace NA values
    crime_year_count = crime_df.groupby(by=['community_area', \
        'year']).size().unstack().fillna(0)
    crime_year_count['Average Homicide'] = crime_year_count.mean(axis=1)
    crime_year_count['area_num'] = crime_year_count.index
    crime_year_count = crime_year_count.melt(id_vars = ['area_num', 'Average Homicide'])
    crime_year_count = crime_year_count.rename(columns={'value': 'Number of Homicides'})

    return crime_year_count.set_index(['area_num', 'year'])
      

def process_grocery_stores(dataset_id):
    '''
    Helper function to clean grocery stores dataset

    Returns pandas df
    '''
    grocery_stores = pull_data(dataset_id, 10000)

    grocery_stores = grocery_stores.rename(columns={'community_area': 'area_num'})
    groc_count = grocery_stores.groupby(by=['area_num'])\
        .size().to_frame(name='grocery stores count')

    #filter liquor stores only
    liquor_stores = grocery_stores[grocery_stores['store_name']\
        .str.contains('LIQUOR')]
    liquor_count = liquor_stores.groupby(by=['area_num']).size().\
        to_frame(name='liquor stores count')

    groceries_df = groc_count.merge(liquor_count, how = 'left', on = 'area_num').fillna(0)

    groceries_df['liquor stores percent'] = groceries_df['liquor stores count']\
        /groceries_df['grocery stores count'] * 100

    groceries_df['year'] = '2011'

    return groceries_df.reset_index().set_index(['area_num', 'year'])
    
    
def process_socio_indicators(dataset_id):
    '''
    Helper function to clean socio-economic indicators dataset

    Returns pandas df
    '''
    socio = pull_data(dataset_id, 1000)

    socio = socio.filter(items=['ca', 'percent_of_housing_crowded', 'hardship_index'])
    socio['year'] = '2010' 
    socio = socio.rename(columns={"ca": "area_num"}).dropna()

    return socio.set_index(['area_num', 'year'])
    

def melt_permit_data(df):
    '''
    Transpose building data 
    '''
    df = df.melt(id_vars = ['area_num', 'community', 'geometry', 'tot_pop'])
    df = df.rename(columns={'variable': 'year'}).set_index(['area_num', 'year']).fillna(0)

    return df


def write_csv(df):
    '''
    Writes csv from a pandas data frame.

    Input: (pd dataframe) df
    '''
    df.to_csv('merged_data.csv')

