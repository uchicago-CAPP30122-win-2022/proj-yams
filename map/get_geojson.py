#!/usr/bin/env python

import pandas as pd
from sodapy import Socrata

def get_comm_areas():
    client = Socrata("data.cityofchicago.org", None)
    results = client.get("igwz-8jzy")

    # Right now I only have a list of 77 community areas
    # Please change this to Geojson:
    comm_areas = pd.DataFrame.from_records(results)
    return comm_areas
