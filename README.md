lProject Yams
Anthony Hakim, Marc Loeb, Sasha Filippova, Yifu Hou

Running The Application

To run urban_dev_explorer, execute the following code.
A popup will direct you to the online Dash map

python urban_dev_explorer



Testing Geocoding

As discussed during the quarter, geocoding is a highly time 
consuming process in the absence of a paid service.

In order to ensure that this project can be run "on the fly" geocoding was done in advance.
The file build_dataframes.py accesses a geoJSON saved in our data folder "permits.geojson,"
which contains ~44,500 geocoded building permits.

To verify the functionality of the geocoding process, we have provided test code in the 
"testing_code" directory.

Simply run the following code:

python urban_dev_explorer --test_geocode

This version of the code is verbose, with a signifigant number of print statements
to allow you to see the progress of the geocoding process. 



Testing Merging

In order to test the merging and data collection process that produces
the csv mapped by Dash, run the following code:

python urban_dev_explorer --test_merge
