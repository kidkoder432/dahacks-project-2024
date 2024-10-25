import pandas as pd

df = pd.read_csv("stars.csv")

print(len(df['constellation'].unique()))

print(df['constellation'].unique())