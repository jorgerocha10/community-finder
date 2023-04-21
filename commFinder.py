import os
import pandas as pd
from sodapy import Socrata
import geopandas as gpd
from shapely.geometry import shape
import matplotlib.pyplot as plt
import creds

socrata_domain = "data.calgary.ca"

property_dataset_identifier = "6zp6-pxei"  # PROPERTY ASSESSMENT VALUE DATASET
crime_dataset_identifier = "78gh-n26t"  # CRIMINALITY DATASET
serv_dataset_identifier = "x34e-bcjz"  # COMMUNITY SERVICES DATASET
parks_dataset_identifier = "kami-qbfh"  # PARKS DATASET
schools_dataset_identifier = "fd9t-tdn2"  # SCHOOLS DATASET
comm_dataset_identifier = "surr-xmvs"  # COMMUNITIES INFORMATION DATASET
lrt_dataset_identifier = "2axz-xm4q"  # LRT DATASET
cei_dataset_identifier = "6bev-z2q5"  # CEI RESULTS DATASET

socrata_token = os.environ.get(creds.api_token)

client = Socrata(socrata_domain, socrata_token)

# PROPERTY ASSESSMENT VALUE DATASET
prop_results = client.get(property_dataset_identifier, limit=2000000, select="COMM_NAME, COMM_CODE,ASSESSED_VALUE",
                          where="ASSESSMENT_CLASS == 'RE' and PROPERTY_TYPE == 'LI' and ROLL_YEAR >= '2017'")

prop_df = pd.DataFrame.from_records(prop_results)
prop_df = prop_df.groupby(['COMM_NAME', 'COMM_CODE']).median()
prop_df = prop_df.reset_index(level='COMM_CODE')

# CRIMINALITY DATASET
# results_df relates to the resident_count
results = client.get(crime_dataset_identifier, limit=200000,
                     select="community_name, resident_count", where="Year >= '2022'")

results_df = pd.DataFrame.from_records(results)
results_df.dropna(subset=['resident_count'], inplace=True)
results_df['resident_count'] = results_df['resident_count'].astype(int)
results_df.drop(
    results_df[results_df['resident_count'] == 0].index, inplace=True)
results_df = results_df.loc[~(results_df['community_name'].apply(len) == 3)]
results_df = results_df.groupby('community_name').median()

# results_df2 relates to the total count of crimes

results2 = client.get(crime_dataset_identifier, limit=200000, group="community_name",
                      select="community_name,sum(crime_count)", where="Year >= '2019'")
results_df2 = pd.DataFrame.from_records(results2)
results_df2 = results_df2.drop_duplicates()
results_df2 = results_df2.dropna(how='any')
results_df2 = results_df2.loc[~(results_df2['community_name'].apply(len) == 3)]

# final df merges both previous dataframes and calculates criminality rate

merged_df = pd.merge(results_df, results_df2, on='community_name', how='left')
merged_df = merged_df.drop_duplicates()
print("Number of results downloaded: {}".format(len(merged_df)))
merged_df['sum_crime_count'] = pd.to_numeric(merged_df['sum_crime_count'])
merged_df = merged_df.assign(criminality_rate=(
    merged_df['sum_crime_count'] / merged_df['resident_count'])*100)  # number of crimes for every 100 people
merged_df = merged_df.loc[~(merged_df['resident_count'] == 0.0)]
crim_df = merged_df[['community_name', 'criminality_rate', 'resident_count']]
crim_df = crim_df.rename(
    columns={'community_name': 'COMM_NAME', 'criminality_rate': 'CRIME_RATE', 'resident_count': 'RESIDENT_COUNT'})

# COMMUNITY SERVICES DATASET
serv_results = client.get(serv_dataset_identifier,
                          limit=2000000, select="NAME, COMM_CODE")

serv_df = pd.DataFrame.from_records(serv_results)
serv_df = serv_df.groupby('COMM_CODE').count()
serv_df = serv_df.reset_index(level='COMM_CODE')


# PARKS DATASET
parks_results = client.get(parks_dataset_identifier, limit=2000000,
                           select="ASSET_CD, LIFE_CYCLE_STATUS", where="LIFE_CYCLE_STATUS=='ACTIVE'")

parks_df = pd.DataFrame.from_records(parks_results)
parks_df['COMM_CODE'] = parks_df['ASSET_CD'].str[:3]
parks_df = parks_df.drop(['ASSET_CD'], axis=1)
parks_df = parks_df.groupby('COMM_CODE').count()
parks_df = parks_df.reset_index(level='COMM_CODE')

# SCHOOLS DATASET
schools_results = client.get(
    schools_dataset_identifier, limit=2000000, select="NAME, the_geom")

schools_df = pd.DataFrame.from_records(schools_results)
schools_df = schools_df.rename(columns={'the_geom': "POINT"})
schools_df["geometry"] = schools_df["POINT"].apply(shape)
schools_df = schools_df.drop("POINT", axis=1)

schools_gdf = gpd.GeoDataFrame(
    schools_df, geometry="geometry", crs="EPSG:4326")

# COMMUNITIES INFORMATION
comm_results = client.get(comm_dataset_identifier,
                          select="COMM_CODE,MULTIPOLYGON")
comm_df = pd.DataFrame.from_records(comm_results)
comm_df["geometry"] = comm_df["MULTIPOLYGON"].apply(shape)
comm_df = comm_df.drop("MULTIPOLYGON", axis=1)

comm_gdf = gpd.GeoDataFrame(comm_df, geometry="geometry", crs="EPSG:4326")

# Merge the new data back into the original point GeoDataFrame
points_with_polygons = gpd.sjoin(
    schools_gdf, comm_gdf, how="inner", op='within')
points_with_polygons = points_with_polygons.drop(
    columns=['index_right', 'geometry'])
schools_gdf = schools_gdf.merge(points_with_polygons, on='NAME')
schools_gdf = schools_gdf.groupby('COMM_CODE').count()
schools_gdf = schools_gdf.rename(columns={'NAME': 'SCHOOLS'})
schools_gdf = schools_gdf.reset_index(level='COMM_CODE')
schools_gdf = schools_gdf.drop("geometry", axis=1)

# LRT DATASET
lrt_results = client.get(lrt_dataset_identifier,
                         limit=2000000, select="STATIONNAM, the_geom")
lrt_df = pd.DataFrame.from_records(lrt_results)
lrt_df = lrt_df.rename(columns={'the_geom': "POINT"})
lrt_df["geometry"] = lrt_df["POINT"].apply(shape)
lrt_df = lrt_df.drop("POINT", axis=1)
lrt_gdf = gpd.GeoDataFrame(lrt_df, geometry="geometry", crs="EPSG:4326")

# Merge the new data back into the original point GeoDataFrame
points_with_polygons = gpd.sjoin(lrt_gdf, comm_gdf, how="inner", op='within')
points_with_polygons = points_with_polygons.drop(
    columns=['index_right', 'geometry'])
lrt_gdf = lrt_gdf.merge(points_with_polygons, on='STATIONNAM')
lrt_gdf = lrt_gdf.groupby('COMM_CODE').count()
lrt_gdf = lrt_gdf.rename(columns={'STATIONNAM': 'STATIONS'})
lrt_gdf = lrt_gdf.reset_index(level='COMM_CODE')
lrt_gdf = lrt_gdf.drop("geometry", axis=1)

# CEI RESULTS DATASET
cei_results = client.get(cei_dataset_identifier,
                         limit=2000000, select="VALUE, COMMUNITIES")

cei_df = pd.DataFrame.from_records(cei_results)
cei_df = cei_df.rename(columns={'VALUE': "CEI_VALUE"})
cei_df = cei_df.assign(
    COMM_NAME=cei_df['COMMUNITIES'].str.split(',')).explode('COMM_NAME')
cei_df['COMM_NAME'] = cei_df['COMM_NAME'].str.strip()
cei_df['CEI_VALUE'] = pd.to_numeric(cei_df['CEI_VALUE'])
cei_df = cei_df.groupby('COMM_NAME')['CEI_VALUE'].mean()
#cei_df = cei_df.drop("COMMUNITIES", axis=1)

# MERGING PROPERTY ASSESSMENT, CRIMINALITY, SERVICES, LRT, AND SCHOOLS
temp_merged = pd.merge(crim_df, prop_df, on='COMM_NAME', how='outer')

# remove whatever has residual in the string
mask = temp_merged['COMM_NAME'].str.contains('RESIDUAL WARD')
temp_merged = temp_merged[~mask]

temp_merged = pd.merge(temp_merged, serv_df, on='COMM_CODE', how='outer')

temp_merged = pd.merge(temp_merged, parks_df, on='COMM_CODE', how='outer')

temp_merged = pd.merge(temp_merged, schools_gdf, on='COMM_CODE', how='outer')

temp_merged = pd.merge(temp_merged, lrt_gdf, on='COMM_CODE', how='outer')

#temp_merged = pd.merge(temp_merged, cei_df, on='COMM_NAME', how='outer')

temp_merged = temp_merged.rename(
    columns={'NAME': 'COMM_SERV', 'LIFE_CYCLE_STATUS': 'COMM_PARKS'})

temp_merged = temp_merged.drop(['COMM_CODE'], axis=1)

temp_merged.fillna(0, inplace=True)

# Format the STATIONS column such that values greater than zero are assigned 1 and values equal to zero are assigned 0
temp_merged["STATIONS_BOOL"] = temp_merged["STATIONS"].apply(
    lambda x: 1 if x > 0 else 0)

# Create a boolean indexing mask to identify rows to delete
mask_name = temp_merged["COMM_NAME"].apply(
    lambda x: True if x == 0 or len(x) == 3 else False)

# Drop the rows that match the mask
temp_merged.drop(temp_merged[mask_name].index, inplace=True)

temp_merged = temp_merged.loc[temp_merged['RESIDENT_COUNT'] >= 50]


#temp_merged.hist(bins=50, figsize=(20, 15))
# plt.show()

temp_merged.to_csv('data.csv', encoding='utf-8')
