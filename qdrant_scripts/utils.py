import hashlib
import json
import logging
import os
import pickle

import requests
from config import settings

qdrant_url = "http://10.181.131.250:8895/forward"


def vector(text):
    headers = {"content-type": "application/json"}
    data = {"inputs": [text]}
    r = requests.post(qdrant_url, data=json.dumps(data), headers=headers)
    r = r.json()["output"][0]
    return r


def get_embedding(text: str):
    if settings.CACHE_QUERY_EMBEDDING:
        cache_key = hashlib.md5(text.strip().encode()).hexdigest()
        if cache_key in os.listdir(".cache"):
            with open(f".cache/{cache_key}", "rb") as f:
                logging.info("use cached embedding")
                return pickle.load(f)

    logging.info("create embedding")
    embedding = vector(text)

    if settings.CACHE_QUERY_EMBEDDING:
        cache_key = hashlib.md5(text.strip().encode()).hexdigest()
        with open(f".cache/{cache_key}", "wb") as f:
            pickle.dump(embedding, f, protocol=pickle.HIGHEST_PROTOCOL)

    return embedding
