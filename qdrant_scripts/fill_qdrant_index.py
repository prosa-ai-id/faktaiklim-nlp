# insert data to qdrant all at once

import json

import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.http import models
from tqdm import tqdm

# MODE = "fact"
MODE = "hoax"

# Initialize Qdrant client
# host = "localhost"
host = "10.181.131.250"
client = QdrantClient(host, port=6333)

# Define collection name
collection_name = f"climate_{MODE}"

# Load vectors from JSON file
with open(f"{MODE}.json", "r") as f:
    data = json.load(f)

# Determine vector size from the first item
vector_size = len(data["items"][0]["vector"])
print(f"VECTOR SIZE: {vector_size}")

# Create the collection
client.recreate_collection(
    collection_name=collection_name,
    vectors_config=models.VectorParams(
        size=vector_size, distance=models.Distance.COSINE
    ),
)

# Prepare points for insertion
points = []
i = 0
for item in tqdm(data["items"], desc="Preparing points"):
    vector = np.array(item["vector"], dtype=np.float32)
    points.append(
        models.PointStruct(
            id=i,  # id HAS TO BE INTEGER
            vector=vector,
            payload={
                "title": item["title"],
                "content": item["content"],
                "url": item["url"],
            },
        )
    )
    i += 1

# Insert points into the collection
try:
    operation_info = client.upsert(
        collection_name=collection_name, wait=True, points=points
    )
    print(
        f"Successfully created index '{collection_name}' and added {len(points)} points."
    )
    print(f"Operation info: {operation_info}")
except Exception as e:
    print(f"An error occurred during upsert: {str(e)}")
    print("Detailed error information:")
    import traceback

    traceback.print_exc()
