import geopandas as gpd


# reading in community areas
def get_geo_comm_areas():

    ca_url = "https://data.cityofchicago.org/api/geospatial/cauq-8yn6?method=export&format=GeoJSON"
    comm_areas = gpd.read_file(ca_url)
    comm_areas = comm_areas.filter(
        ["community", "area_num_1", "geometry"]).rename(
            columns={"area_num_1": "area_num"}).astype({"area_num": 'int16'})

    return comm_areas

def geojoin_permits(comm_areas, perm_df):

    #comm_areas.crs # EPSG:4326
    #perm_df.crs #EPSG:4326

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
    # two permits mysteriously have been assigned a community area of 0
    # even though community area numbers run from 1 to 77
    perm_df_coded = perm_df_coded[perm_df_coded.comm_area != 0]

    demo_perm_df = perm_df_coded[
        perm_df_coded.perm_type == "PERMIT - WRECKING/DEMOLITION"]
        # len 18821
    build_perm_df = perm_df_coded[
        perm_df_coded.perm_type == "PERMIT - NEW CONSTRUCTION"]
        # len 25201

    return (demo_perm_df, build_perm_df)


def merge_permits_ca(comm_areas, demo_perm_df, build_perm_df):

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

    # reading in comm area census data, calculating race percent and vacancy rate
    census_url = "https://datahub.cmap.illinois.gov/dataset/1d2dd970-f0a6-4736-96a1-3caeb431f5e4/resource/0916f1de-ae37-4476-bf4e-6485ba08c975/download/Census2020SupplementCCA.csv"
    census_ca = pd.read_csv(census_url)
    census_ca = census_ca.rename(columns=str.lower).rename(columns={
                    "geog": "community", "geoid": "area_num", 
                    "hu_tot": "total_homes", "vac_hu": "vac_homes"})
    census_ca["vac_rate"] = 100 * census_ca.vac_homes / census_ca.total_homes
    census_ca["hisp_per"] = 100 * census_ca.hisp / census_ca.tot_pop
    census_ca["white_per"] = 100 * census_ca.white / census_ca.tot_pop
    census_ca["black_per"] = 100 * census_ca.black / census_ca.tot_pop
    census_ca["asian_per"] = 100 * census_ca.asian / census_ca.tot_pop

    return census_ca


def normalize_permit_counts(comm_areas, census_ca):

    comm_areas = comm_areas.merge(census_ca, on="area_num")
    #comm_areas = comm_areas.drop(columns="geog")

    # building and demolition rate
    comm_areas["demo_rate"] = comm_areas.demos / comm_areas.tot_pop
    comm_areas["build_rate"] = comm_areas.builds / comm_areas.tot_pop
    comm_areas["build_val_per_cap"] = comm_areas.tot_build_value / comm_areas.tot_pop
    comm_areas["ave_build_val"] = comm_areas.tot_build_value / comm_areas.builds
    comm_areas["build_per_demo"] = comm_areas.builds/comm_areas.demos
    comm_areas["change_rate"] = comm_areas.build_rate - comm_areas.demo_rate

    return comm_areas


def permits_per_year(comm_areas, build_perm_df, demo_perm_df):

    pop = comm_areas[['community', 'area_num', 'geometry', 'tot_pop']]

    # new construction per year per 1000 people
    build_year_count = build_perm_df.groupby(by=["comm_area", "year"]).size().unstack()
    build_year_count = per_capita(build_year_count, pop)

    # demolition per year per 1000 people
    demo_year_count = demo_perm_df.groupby(by=["comm_area", "year"]).size().unstack()
    demo_year_count = per_capita(demo_year_count, pop)

    # new construction value per year per 1000 people
    build_year_val = build_perm_df.groupby(by=["comm_area", "year"])["work_cost"].sum().unstack()
    build_year_val = per_capita(build_year_val, pop)

    return build_year_count, demo_year_count, build_year_val


def per_capita(df, pop):

    years_lst = ['2006', '2007', '2008', '2009', '2010', '2011', '2012', 
    '2013', '2014', '2015', '2016', '2017', '2018', '2019', '2020', '2021']

    df = df.drop(columns=["2004", "2005", "2022"], errors='ignore')
    df = df.merge(pop, left_on='comm_area', right_on='area_num')
    df[years_lst] = df[years_lst].div(df.tot_pop, axis=0).mul(1000)

    return df