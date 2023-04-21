/**********community-finder**********/

Welcome to the City of Calgary Community Finder! This repository retrieves multiple datasets from the City of Calgary's open data portal and generates a structured, normalized dataset. This dataset is then utilized by a Euclidean distance script to rank, based on user input, the best communities to live in. 

/commFinder.py/ 

This script contains a Python script for analyzing community data in Calgary, Canada. The script retrieves data from several datasets using the Socrata API, including property assessment values, criminality statistics, community services, parks, schools, and communities information.

The script requires the pandas, geopandas, sodapy, and matplotlib libraries to be installed. It also requires an API token to access the Socrata datasets, which can be obtained from the City of Calgary Open Data Portal. The API token should be stored in a separate creds.py file, which is imported in the script.

The main functionalities of the script include:

Retrieving property assessment values for properties in Calgary from the "PROPERTY ASSESSMENT VALUE DATASET" and calculating the median assessed value for each community.
Retrieving criminality statistics from the "CRIMINALITY DATASET" and calculating the median resident count and total crime count for each community. The script also calculates the criminality rate, which is the number of crimes per 100 residents, and stores the results in a dataframe.
Retrieving community services data from the "COMMUNITY SERVICES DATASET" and counting the number of services in each community.
Retrieving parks data from the "PARKS DATASET" and counting the number of active parks in each community.
Retrieving schools data from the "SCHOOLS DATASET" and creating a GeoDataFrame with the school locations.
Retrieving communities information from the "COMMUNITIES INFORMATION DATASET" and creating a GeoDataFrame with the community boundaries.
The script then merges the data from the different datasets into a final GeoDataFrame, which can be used for further analysis or visualization. The final GeoDataFrame includes community codes, names, criminality rate, resident count, total crime count, number of community services, number of active parks, and community boundaries. The script also generates plots using matplotlib to visualize the data, including a bar chart of the top 10 communities with the highest and lowest criminality rates, and a map of the communities in Calgary color-coded by criminality rate.

Note: The script is limited to retrieving a maximum of 2 million records from each dataset due to API limitations. If more data is needed, the limit parameter in the client.get() function can be adjusted accordingly.

/**********commRanking.py**********/

This Python code utilizes various data processing and analysis libraries such as pandas, sklearn, scipy, and matplotlib to implement a community ranking system for the City of Calgary. The score_and_rank() function takes in user-defined input parameters for crime rate, value, services, parks, schools, and stations. It then reads a CSV file containing community data into a pandas dataframe, normalizes the data using MinMaxScaler, calculates the Euclidean distance between the user input and each community, sorts the communities based on distance, assigns a rank to each community, and returns the resulting dataframe.

To use the code, you can call the score_and_rank() function with your desired input values to obtain a ranked list of communities. An example usage of the function is provided at the end of the code, where it is called with some example input values and the resulting dataframe is printed to the console. Additionally, the resulting dataframe is saved to a new CSV file named "data2.csv" for further analysis or visualization.
