import geopandas as gpd
import pygeos

# reading in community areas
ca_url = "https://data.cityofchicago.org/api/geospatial/cauq-8yn6?method=export&format=GeoJSON"
comm_areas = gpd.read_file(ca_url)

# reading in geocoded building permits

perm_df = gpd.read_file("permits_1000.geojson")

# Spatial join
comm_areas.crs
    # EPSG:4326

perm_df.crs
    #EPSG:4326


perm_df_w_ca = gpd.sjoin(perm_df, comm_areas, how = "inner", op = "within")

"Spatial indexes require either `rtree` or `pygeos`. See installation instructions at https://geopandas.org/install.html"

# have already installed!!!