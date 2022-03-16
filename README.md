Anthony Hakim, Marc Loeb, Sasha Filippova, Yifu Hou

Welcome to Urban Development Explorer, by Project YAMS!

Project Descripion:
Our application is an interactive map displaying urban development indicators
along with varios socioeconomic indicators, intedned for exploratoty data 
analysis purposes. Intended users are esearchers, professionals, 
and students, who are interested in developing an intuition for the varios
factors that may affect urban growth and decay.

STEPS TO RUN THE APPLICATION:


Creating a Virtual Environment with Dependencies

In the terminal, first run the following command:
bash install.sh

Now that the virtual environment is created, enter the 
virtual environment run the command:
source env/bin/activate


Running the Apllication

To run urban_dev_explorer, execute the following code:

    python3 urban_dev_explorer

This executes our dash map with a shell script.
A popup will direct you to the online Dash map


To verify the functionality of the geocoding process, we have added testing
a testing parameter to the get_permits() function, housed in the
building_permits.py file, in the dataprocessing directory


Testing Geocoding

To test the geocoding process, simply run the following code:

    python3 urban_dev_explorer --test_geocode

This version of the code is verbose, with a signifigant number of print 
statements to allow you to see the progress of the geocoding process. A limit of 500 has been added, instead of the full ~44,500 entries. If allowed to run to completion, a file named "perm_new.geojson" will be added to our data directory


Testing Merging

In order to test the merging and data collection process that produces
the csv mapped by Dash, run the following code:

    python3 urban_dev_explorer --test_merge

If allowed to run to completion, a file named "new_map_data.csv"
will be added to our data directory



Context on why GeoCoding was done in advance:

Geocoding is a highly time consuming process in the absence of a paid service.
In order to ensure that this project can be run "on the fly" geocoding was 
done in advance. The file build_dataframes.py accesses a geoJSON saved in 
our data folder "permits.geojson,"which contains ~44,500 geocoded building 
permits.
