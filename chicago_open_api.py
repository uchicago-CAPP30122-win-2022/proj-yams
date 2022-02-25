import pandas as pd
from sodapy import Socrata

def get_data(code):

    client = Socrata("data.cityofchicago.org", "goD601SLndI51xcMq1KsnG6np")
    ca_results = client.get(code)
    pandas_df = pd.DataFrame.from_records(ca_results)

    return pandas_df