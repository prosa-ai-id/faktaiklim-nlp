import json

import pandas as pd
import requests
from tqdm import tqdm

HOST = "localhost"


def insert_data(data):
    headers = {
        "content-type": "application/json",
        "x-api-key": "ebce2698dadf0593c979a2798c84e49a0",
    }
    url = f"http://{HOST}:8092/article/{data['id']}"
    result = requests.put(url, data=json.dumps(data), headers=headers)
    r = result.json()
    return r


# fname = "/home/miftah/Downloads/giz/be_data_processing/xlsx/result.xlsx"
fname = "/srv/nas_data2/text/miftah/giz_climate_2/be_insertion_scripts/xlsx/be_data_14_nov_2024.xlsx"
df = pd.read_excel(fname, sheet_name="BE_data")

for i, row in tqdm(df.iterrows(), total=df.shape[0]):
    if i < 3954:
        continue
    text = f"{row['title']} . {row['content']}"
    data = row.to_dict()
    data["id"] = i
    # print(data)
    r = insert_data(data)
