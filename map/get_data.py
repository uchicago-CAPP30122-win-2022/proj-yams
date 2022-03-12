##### TEMPORARY FILE
##### This file is compeletely copied from anthony_notes.ipynb
##### map.py will expect a result from this module by calling get_data.return_df()


from http.client import REQUESTED_RANGE_NOT_SATISFIABLE
import pandas as pd
from sodapy import Socrata
import matplotlib.pyplot as plt
pd.set_option('display.max_rows', None)

id_dict = {
    "red light violations": "spqx-js37", "abandoned buildings": "kc9i-wq85",
    "socioeconomic indicators": "kn9c-c2s2", "hardship index": "792q-4jtu",
    "crimes": "ijzp-q8t2", "grocery stores": "4u6w-irs9" }


def pull_data(dataset_id, lim):
    '''
    Given a dataset id, pull out data from Chicago portal API

    Inputs:
      dataset_id: (str) a unique id for one Chicago portal dataset
      limit: (int) number of rows to pull each time, default to None

    Return:
      (Pandas DataFrame) a dataframe pulled from Chicago Portal
    '''
    client = Socrata("data.cityofchicago.org", "goD601SLndI51xcMq1KsnG6np")

    results = client.get(dataset_id, limit = lim)
    return pd.DataFrame.from_records(results)


def gen_tables(id_dictionary, lim):
    dataset_dct = {}
    for dataset_name, url in id_dictionary.items():
        dataset_dct[dataset_name] = pull_data(url, lim)

    return dataset_dct


dct = gen_tables(id_dict, 1000)


def return_df():
    client = Socrata("data.cityofchicago.org", "goD601SLndI51xcMq1KsnG6np")
    results = client.get("ijzp-q8t2", where = f"(primary_type) = 'HOMICIDE'",
                        limit=1000000)

    crime_df = pd.DataFrame.from_records(results)

    crime_year_count = crime_df.groupby(by=['community_area', "year"]).size().unstack()

    crime_year_count = crime_year_count.fillna(0)

    crime_year_count['Average Homicide'] = crime_year_count.mean(axis=1)

    crime_year_count['community area'] = crime_year_count.index

    return crime_year_count.melt('community area')

