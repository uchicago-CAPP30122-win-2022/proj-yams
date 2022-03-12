from http.client import REQUESTED_RANGE_NOT_SATISFIABLE
import pandas as pd
from sodapy import Socrata


id_dict = {
    "red light violations": "spqx-js37", "abandoned buildings": "kc9i-wq85",
    "socioeconomic indicators": "kn9c-c2s2", "hardship index": "792q-4jtu",
    "crimes": "ijzp-q8t2", "grocery stores": "4u6w-irs9"}


def generate_final_df():
    '''
    Pull all data sets from the City of Chicago portal using API and merge in one file.

    Inputs:
      id_dict: (dict) a dictionary mapping names of datasets to its unique ids
    
    Return:
      merged pandas dataframe containing all the data from the dict 
    '''
    for data_name, data_id in id_dict.items():
        if data_name == "crimes":
            #call helper function which returns clean socioeconomic df
            #merge with Marc's df
            pass  

        elif data_name == "socioeconomic indicators":
            #call helper function which returns clean socioeconomic df
            #merge with Marc's df
            pass 

        elif data_name == "grocery stores":
            #my function
            pass



def pull_data(dataset_id, limit):
    '''
    Given a dataset id, pull out data from Chicago portal API

    Inputs:
      dataset_id: (str) a unique id for one Chicago portal dataset
      limit: (int) number of rows to pull each time, default to None

    Return:
      (Pandas DataFrame) a dataframe pulled from Chicago Portal
    '''
    client = Socrata("data.cityofchicago.org", "goD601SLndI51xcMq1KsnG6np")

    results = client.get(dataset_id, limit)
    return pd.DataFrame.from_records(results)


"""
def assert_valid_input(d):
    '''
    Verify the input is from one of the designated datasets, and the
    values conform to the standards for the regression model.

    Input: d (dictionary) expected dictionary called from ui
    '''

    assert isinstance(d, dict)
    acceptable_keys = set(["red light violations", "abandoned buildings",
    "socioeconomic indicators", "hardship index", "crimes", "grocery stores"])
    assert set(d.keys()).issubset(acceptable_keys)

    for value in d.values():
        assert isinstance(value, pd.DataFrame)
"""


"""
def collect_data(regressors, limit=None):
    '''
    Given the regressors, call function pull_data()
    and join a Pandas DataFrame

    Inputs:
      regressors: (dictionary) a dictionary matching dataframes
      with a list of independent variables from each dataframe.
      Dataframe with an empty list will has its count aggregated
      by community area.
      e.g. regressors = {
          "red light violations": ["VIOLATIONS"],
          "abandoned buildings": [],
          "hardship index": ["PERCENT HOUSEHOLDS BELOW POVERTY", "PER CAPITA INCOME"]
          }
      limit:  (int) number of rows to pull each time, default to None

    Return:
      reg_table: (Pandas DataFrame) a dataframe merging all the
      regressors as columns, aggregated by community areas.
    '''
    assert_valid_input(regressors)

    for table, values in regressors.items():
        dataset_id = id_dict[table]
        df = pull_data(dataset_id, limit)
        # Check if dataframe has column "Community Area Name"
        # If not, geo-join

        # Check if the values list is empty. If empty, by
        # default, count number of rows and aggregate count
        # in joint dataframe

        # If not empty, aggregate the values requested by
        # each community area
        if values:
            for var in values:

        # Join Pandas DataFrames by "Community Area Name"
    
    return reg_table
"""

