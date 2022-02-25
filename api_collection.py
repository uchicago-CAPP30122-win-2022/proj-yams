from http.client import REQUESTED_RANGE_NOT_SATISFIABLE
import pandas as pd
from sodapy import Socrata

##### This file replaces chicago_open_api.py


id_dict = {
    "red light violations": "spqx-js37", "abandoned buildings": "kc9i-wq85",
    "socioeconomic indicators": "kn9c-c2s2", "hardship index": "792q-4jtu",
    "crimes": "ijzp-q8t2", "grocery stores": "4u6w-irs9", }


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
