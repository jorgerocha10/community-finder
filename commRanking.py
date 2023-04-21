import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from scipy.spatial.distance import euclidean
import matplotlib.pyplot as plt


def score_and_rank(crime_rate, value, services, parks, schools, stations):
    # Read the CSV file into a dataframe
    df = pd.read_csv("data.csv")

    # Normalize the data
    scaler = MinMaxScaler()
    df[["CRIME_RATE", "ASSESSED_VALUE"]] = pd.DataFrame(
        scaler.fit_transform(df[["CRIME_RATE", "ASSESSED_VALUE"]])).values[:, ::-1]
    df[["COMM_SERV", "COMM_PARKS", "SCHOOLS", "STATIONS_BOOL"]] = scaler.fit_transform(
        df[["COMM_SERV", "COMM_PARKS", "SCHOOLS", "STATIONS_BOOL"]])

    # Calculate the distance between the user input and each community
    df["distance"] = df[["CRIME_RATE", "ASSESSED_VALUE", "COMM_SERV", "COMM_PARKS", "SCHOOLS", "STATIONS_BOOL"
                         ]].apply(lambda row: euclidean([crime_rate, value, services, parks, schools, stations], row), axis=1)

    # Sort the dataframe by distance in ascending order
    df = df.sort_values(by="distance")

    # Rank the communities by their order in the sorted dataframe
    df["rank"] = df["distance"].rank(method="min", ascending=True)

    return df


# Test the function with some example input
df = score_and_rank(0.7, 0.7, 0.7, 0.7, 0.6, 0.5)
print(df)

df.hist(bins=50, figsize=(20, 15))
plt.show()
df.to_csv('data2.csv', encoding='utf-8')
