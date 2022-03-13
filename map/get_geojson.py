#!/usr/bin/env python

import json
import pandas as pd
from sodapy import Socrata
from urllib.request import urlopen

comm_areas_url = "https://data.cityofchicago.org/api/geospatial/cauq-8yn6?method=export&format=GeoJSON"
with urlopen(comm_areas_url) as response:
    comm_areas = json.load(response)



