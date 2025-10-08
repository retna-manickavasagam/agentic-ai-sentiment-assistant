# inspect_csv.py
import pandas as pd

df = pd.read_csv("data/raw/raw3000.csv")
print("Columns:", df.columns.tolist())
print(df.head(3).to_dict(orient="records"))
