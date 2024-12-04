import json
from typing import Dict, List

from config import settings
from document_db import QDrantDB
from qdrant_client.models import ScoredPoint
from utils import get_embedding

db = QDrantDB()


class ClimateSearch:
    def __init__(self) -> None:
        pass

    def convert_to_items(self, docs: List[ScoredPoint], hoax_status: str) -> List[Dict]:
        items = []
        for doc in docs:
            item = doc.payload
            item["score"] = doc.score
            item["hoax_status"] = hoax_status
            items.append(item)
        return items

    def check(self, text: str):
        hoax_docs = db.search(get_embedding(text), settings.HOAX_COLLECTION_NAME)
        hoax_docs = self.convert_to_items(hoax_docs, hoax_status="hoax")
        fact_docs = db.search(get_embedding(text), settings.FACT_COLLECTION_NAME)
        fact_docs = self.convert_to_items(fact_docs, hoax_status="fact")
        docs = hoax_docs + fact_docs
        docs = sorted(docs, key=lambda d: d["score"], reverse=True)
        print(json.dumps(docs, indent=3))
        return docs


if __name__ == "__main__":
    cs = ClimateSearch()
    res = cs.check("cek iklim query")
