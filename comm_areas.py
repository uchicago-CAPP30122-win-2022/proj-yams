import pandas as pd
from sodapy import Socrata

client = Socrata("data.cityofchicago.org", "goD601SLndI51xcMq1KsnG6np", username = "marcdloeb@gmail.com", password = "2522-Haphazard")
ca_results = client.get("igwz-8jzy")
comm_area = pd.DataFrame.from_records(ca_results)