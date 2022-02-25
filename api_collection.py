import pandas as pd
from sodapy import Socrata

id_dict = {"red_light_violations": "spqx-js37", "abandoned_buildings": "kc9i-wq85", \
    "socioeconomic_indicators": "kn9c-c2s2", "hardship_index": "792q-4jtu", \
        "crimes": "ijzp-q8t2", "grocery_stores": "4u6w-irs9", }

# Unauthenticated client only works with public data sets. Note 'None'
# in place of application token, and no username or password:

def create_dataframes: 
    for key, value in id_dict.items():
        key = chicago_open_api(value):