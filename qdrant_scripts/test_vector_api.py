import json

import pandas as pd
import requests
from tqdm import tqdm
from utils import get_embedding

MODE = "fact"
# MODE = "hoax"

tqdm.pandas()
# url = "http://10.181.131.250:8895/forward"
url = "http://10.181.131.250:8899/forward"

# fname = "../es_scripts/climate_es_data.xlsx"
fname = "/home/miftah/Downloads/giz/es_scripts/climate_es_data.xlsx"
df = pd.read_excel(fname, sheet_name="Sheet1")
df = df[df["hoax_status"] == MODE]
df = df[:4]

df["text"] = df["title"] + " . " + df["content"]
df["vector"] = df["text"].progress_apply(get_embedding)


# Save df to list of dict, fname = vectors.json
result = df.to_dict(orient="records")
vector_size = len(result[0]["vector"])
print(f"VECTOR SIZE: {vector_size}")
result = {"total": len(result), "items": result}
json_outf = f"{MODE}.json"
json_outf = f"test.json"
with open(json_outf, "w") as f:
    json.dump(result, f, indent=3)

print(f"Processing complete. Results saved to {json_outf}")
