Project Yams
Anthony Hakim, Marc Loeb, Sasha Filippova, Yifu Hou



Testing Geocoding

As discussed during the quarter, geocoding is a highly time 
consuming process in the absence of a paid service.

In order to ensure that this project can be run "on the fly" geocoding was done in advance.
The file build_dataframes.py accesses a geoJSON saved in our data folder "permits.geojson,"
which contains ~44,500 geocoded building permits.

To verify the functionality of the geocoding process, we have provided test code in the 
"testing_code" directory.

Simply run the following python code:

python urban_dev_explorer.py --test_geocode

This version of the code is verbose, with a signifigant number of print statements
to allow you to see the progress of the geocoding process. The name of the output
file and the number of permits to include in your test can be set to your liking
but default to 500 and "test_permits.geojson."


Testing Merging

