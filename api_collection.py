import pandas as pd
from sodapy import Socrata

id_dict = {"red light violations": "spqx-js37", "abandoned buildings": "kc9i-wq85", \
    "socioeconomic indicators": "kn9c-c2s2", "hardship index": "792q-4jtu", \
        "crimes": "ijzp-q8t2", "grocery stores": "4u6w-irs9", }

# Unauthenticated client only works with public data sets. Note 'None'
# in place of application token, and no username or password:

def pull_data(dataset_id, limit=None):
    client = Socrata("data.cityofchicago.org", None)

    #enter dataset identifier and limit for number of rows.
    results = client.get(dataset_identifier, limit)
    return pd.DataFrame.from_records(results)