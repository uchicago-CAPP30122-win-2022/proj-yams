import os
from data_processing.building_permits import get_pemits
from  data_processing.build_dataframes import run_merge
import argparse


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="Test or run main?")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--test_geocode", action="store_true")
    group.add_argument("--test_merge", action="store_true")

    args = parser.parse_args()


    if args.test_geocode:
        print("testing_geocode")
        get_pemits(testing=True, 
            save_name="urban_dev_explorer/data/perm_new.geojson", rec_limit=500)
    elif args.test_merge:
        print("testing_merge")
        run_merge("urban_dev_explorer/data/new_map_data.csv", testing=True)

    # no test, so just run it
    else:
        print("running_map")
        os.system("sh ../proj-yams/urban_dev_explorer/run.sh")