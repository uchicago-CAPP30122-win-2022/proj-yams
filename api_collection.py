import pandas as pd
from sodapy import Socrata

id_dict = {"red_light_violations": "spqx-js37"}

# Unauthenticated client only works with public data sets. Note 'None'
# in place of application token, and no username or password:

def pull_data(dataset_id, limit=None):
    client = Socrata("data.cityofchicago.org", None)

    #enter dataset identifier and limit for number of rows.
    results = client.get(dataset_identifier, limit)
    return pd.DataFrame.from_records(results)