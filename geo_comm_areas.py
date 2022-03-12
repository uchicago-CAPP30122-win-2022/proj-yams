import geopandas as gpd
import pandas as pd


# reading in community areas
def get_geo_comm_areas():
    """
    Retrieves a geojson file of Chicago's 77 community areas

    Returns a geodataframe, with a community area as each row
    
    """

    ca_url = "https://data.cityofchicago.org/api/geospatial/cauq-8yn6?method=export&format=GeoJSON"
    comm_areas = gpd.read_file(ca_url)
    comm_areas = comm_areas.filter(
        ["community", "area_num_1", "geometry"]).rename(
            columns={"area_num_1": "area_num"}).astype({"area_num": 'int16'})

    return comm_areas

def geojoin_permits(comm_areas, perm_df):
    """
    Uses a geospatial join to assign community area numbers to
    building permits missing that data

    Inputs:
        comm_areas (geodataframe, multipolygon): Chicago's 77 community areas
            crs: EPSG:4326
        perm_df (geodataframe, point): ~44,500 building permits
            previously geocoded to fill in missing lat, lon data, but
            with some still missing community are number
            crs: EPSG:4326

    Returns:
        demo_perm_df (geodataframe): geojoined permits for "WRECKING/DEMOLITION"
        build_perm_df (geodataframe): geojoined permits for "NEW CONSTRUCTION"
    
    """

    # splitting date column
    perm_df[["year", "month", "day"]] = perm_df.app_date.str.split("-", expand=True)
    perm_df.day = perm_df.day.str.strip("T00:00:00")

    perm_df_wca = perm_df[perm_df["comm_area"].notna()]
    # len 35075

    # permits that are missing community area number, need to be joined
    perm_df_noca = perm_df[perm_df["comm_area"].isna()]
    # len 8969
    
    # spatial join to find comm area for permits missing it
    perm_df_noca = gpd.sjoin(perm_df_noca, comm_areas, how="inner", op="within")

    # brings in an "index right" column that I am confused about
    perm_df_noca = perm_df_noca.drop(columns=["comm_area", "index_right"])
    perm_df_noca = perm_df_noca.rename(columns={
        "area_num": "comm_area", "community": "ca_name"})

    perm_df_coded = pd.concat([perm_df_wca, perm_df_noca], axis=0)
    perm_df_coded = perm_df_coded.astype({"comm_area": 'int16', 
                                            "work_cost": 'float'})
    # len 44024
    perm_df_coded = perm_df_coded[perm_df_coded.comm_area != 0]

    demo_perm_df = perm_df_coded[
        perm_df_coded.perm_type == "PERMIT - WRECKING/DEMOLITION"]
        # len 18821
    build_perm_df = perm_df_coded[
        perm_df_coded.perm_type == "PERMIT - NEW CONSTRUCTION"]
        # len 25201

    return (demo_perm_df, build_perm_df)


def merge_permits_ca(comm_areas, demo_perm_df, build_perm_df):

    """
    Finds the total number of new buildings ("builds") and 
    total number of new demolutions ("demos") and calculates
    the cumulative built value ("tot_build_value") for each 
    community area from the permit dataframes. Joins these 
    summary statistics onto the existing comm_areas dataframe

    Inputs:
        comm_areas (geodataframe, multipolygon): Chicago's 77 community areas
        demo_perm_df (geodataframe): geojoined permits for "WRECKING/DEMOLITION"
        build_perm_df (geodataframe): geojoined permits for "NEW CONSTRUCTION"

    Returns:
        comm_areas, with additional columns for "builds", "demos" and
        "tot_build_value"
    
    """

    # merging count of demos and builds per community area into comm area
    demo_count = demo_perm_df.groupby(by=["comm_area"]).size().reset_index()
    demo_count = demo_count.rename(columns={0: "demos"})
    comm_areas = comm_areas.merge(demo_count,
                            left_on='area_num', right_on='comm_area')

    build_count = build_perm_df.groupby(by=["comm_area"]).size().reset_index()
    build_count = build_count.rename(columns={0: "builds"})
    comm_areas = comm_areas.merge(build_count,
                            left_on='area_num', right_on='comm_area')

    # total value of new construction
    build_total_value = build_perm_df.groupby(by=["comm_area"])["work_cost"].sum().reset_index()
    build_total_value = build_total_value.rename(columns={"work_cost": "tot_build_value"})
    comm_areas = comm_areas.merge(build_total_value,
                            left_on='area_num', right_on='comm_area')

    comm_areas = comm_areas.drop(columns=["comm_area_x", "comm_area_y", "comm_area"])

    return comm_areas


def get_ca_census():
    """
    Retrieves 2020 Census Supplment, with data for population, race, housing
    for each of Chicago's 77 community areas.
    https://datahub.cmap.illinois.gov/dataset/1d2dd970-f0a6-4736-96a1-3caeb431f5e4/resource/0916f1de-ae37-4476-bf4e-6485ba08c975

    Calculates dditional columns for vacancy rate ("vac_rate"),
    and Hispanic, White, Black and Asian pop share
    ("hisp_per", "white_per", "black_per", "asian_per")
    
    Returns:
        census_ca (dataframe): entries for each of Chicago's 77 community areas
    """

    # reading in comm area census data, calculating race percent and vacancy rate
    census_url = "https://datahub.cmap.illinois.gov/dataset/1d2dd970-f0a6-4736-96a1-3caeb431f5e4/resource/0916f1de-ae37-4476-bf4e-6485ba08c975/download/Census2020SupplementCCA.csv"
    census_ca = pd.read_csv(census_url)
    census_ca = census_ca.rename(columns=str.lower).rename(columns={
                    "geog": "comm_name", "geoid": "area_num", 
                    "hu_tot": "total_homes", "vac_hu": "vac_homes"})
    census_ca["vac_rate"] = 100 * census_ca.vac_homes / census_ca.total_homes
    census_ca["hisp_per"] = 100 * census_ca.hisp / census_ca.tot_pop
    census_ca["white_per"] = 100 * census_ca.white / census_ca.tot_pop
    census_ca["black_per"] = 100 * census_ca.black / census_ca.tot_pop
    census_ca["asian_per"] = 100 * census_ca.asian / census_ca.tot_pop

    return census_ca


def normalize_permit_counts(comm_areas, census_ca):

    """
    Joins census data to the multipolygon geodataframe for each of
    Chicago's 77 community areas. Normalizes the counts of new builds,
    demolitions, and total build value by population in each communtiy area
    Calculates additional summary columns for average value of new buildings
    and the number of new buildings per demolition for each community area

    Inputs:
        census_ca (dataframe): census data for 77 community areas
        comm_areas (geodataframe, multipolygon): Chicago's 77 community areas

    Returns:
        comm_areas (geodataframe, multipolygon): Chicago's 77 community areas,
            with additional columns for:
            demolitions per capita ("demo_rate"),
            new buildings per capita ("build_rate"), 
            total built value per capita ("build_val_per_cap"), 
            the average built value per new building ("ave_build_val"), 
            the diff between build rate and the demo rate ("change_rate")
    
    """

    comm_areas = comm_areas.merge(census_ca, on="area_num")

    # building and demolition rate
    comm_areas["demo_rate"] = comm_areas.demos / comm_areas.tot_pop
    comm_areas["build_rate"] = comm_areas.builds / comm_areas.tot_pop
    comm_areas["build_val_per_cap"] = comm_areas.tot_build_value / comm_areas.tot_pop
    comm_areas["ave_build_val"] = comm_areas.tot_build_value / comm_areas.builds
    comm_areas["build_per_demo"] = comm_areas.builds/comm_areas.demos
    comm_areas["change_rate"] = comm_areas.build_rate - comm_areas.demo_rate

    return comm_areas


def per_capita(df, pop, unit_size):

    """
    Helper function for permits_per_year

    Limits the range of the years to 2006-2021, the time period
    for which there is complete permit data. Joins population data
    and multipolygon geometry. Divides value for each year by the
    population of the corresponding community area, multiplies by
    a specified number of persons


    Inputs:
        df (dataframe): a dataframe with a count or sum per community
            area per year
        pop (geodataframe, multipolygon): contains population count
            geometry for each of Chicago's 77 community area
        unit size (int): multiplies per capita rate by this population unit

    Returns:
        geodf (geodataframe, multipolygon): df with population normalized
            counts or sums per community area per year
    
    """

    years_lst = ['2006', '2007', '2008', '2009', '2010', '2011', '2012', 
    '2013', '2014', '2015', '2016', '2017', '2018', '2019', '2020', '2021']

    df = df.drop(columns=["2004", "2005", "2022"], errors='ignore')
    df = df.merge(pop, left_on='comm_area', right_on='area_num')
    df[years_lst] = df[years_lst].div(df.tot_pop, axis=0).mul(unit_size)

    geodf = gpd.GeoDataFrame(df, crs="EPSG:4326", geometry=geometry)

    return geodf


def permits_per_year(comm_areas, build_perm_df, bsize, demo_perm_df, dsize):
    """
    Calculates the number of new buildings, demolitions, and new built
    value per community area per year

    Inputs:
        comm_areas(geodataframe, multipolygon): Chicago's 77 community areas
        build_perm_df(geodataframe): geojoined permits for "NEW CONSTRUCTION"
        bsize(int): population unit size for new buildings count
        demo_perm_df(geodataframe): geojoined permits for "WRECKING/DEMOLITION"
        dsize(int): population unit size for demolitions count

    Returns:
        build_year_count(geodataframe, multipolygon): Chicago's 77 
            community areas with new builds per 10,000 people, per year
        demo_year_count(geodataframe, multipolygon): Chicago's 77 
            community areas with demos per 10,000 people, per year
        build_year_val(geodataframe, multipolygon): Chicago's 77 
            community areas with built value per capita, per year

    """

    pop = comm_areas[['community', 'area_num', 'geometry', 'tot_pop']]

    # new construction per year per 1000 people
    build_year_count = build_perm_df.groupby(
        by=["comm_area", "year"]).size().unstack()
    build_year_count = per_capita(build_year_count, pop, bsize)

    # demolition per year per 1000 people
    demo_year_count = demo_perm_df.groupby(
        by=["comm_area", "year"]).size().unstack()
    demo_year_count = per_capita(demo_year_count, pop, dsize)

    # new construction value per year
    build_year_val = build_perm_df.groupby(
        by=["comm_area", "year"])["work_cost"].sum().unstack()
    build_year_val = per_capita(build_year_val, pop, 1)

    return build_year_count, demo_year_count, build_year_val
