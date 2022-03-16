Anthony Hakim, Marc Loeb, Sasha Filippova, Yifu Hou

Welcome to Urban Development Explorer, by Project YAMS!


To run urban_dev_explorer, execute the following code:

    python3 urban_dev_explorer


This executes our dash map with a shell script.
A popup will direct you to the online Dash map



Testing Geocoding

As discussed during the quarter, geocoding is a highly time 
consuming process in the absence of a paid service.

In order to ensure that this project can be run "on the fly" geocoding was 
done in advance. The file build_dataframes.py accesses a geoJSON saved in 
our data folder "permits.geojson,"which contains ~44,500 geocoded building 
permits.

To verify the functionality of the geocoding process, we have added testing
a testing parameter to the get_permits() function, housed in the
building_permits.py file, in the dataprocessing directory

To test, simply run the following code:

    python3 urban_dev_explorer --test_geocode


This version of the code is verbose, with a signifigant number of print 
statements to allow you to see the progress of the geocoding process. 

Instead of the full ~44,500 building permits, a limit of 500 has been
added. If allowed to run to completion, a file named 
"perm_new.geojson" will be added to our data directory


Testing Merging

In order to test the merging and data collection process that produces
the csv mapped by Dash, run the following code:

    python3 urban_dev_explorer --test_merge


If allowed to run to completion, a file named "new_map_data.csv"
will be added to our data directory
