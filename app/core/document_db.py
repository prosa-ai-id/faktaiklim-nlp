import abc
from typing import Dict, List

import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.grpc import ScoredPoint
from qdrant_client.http.models import Distance, PointStruct, VectorParams

from app.config import settings
from app.core.utils import get_embedding
from app.schema import Article, Knowledges


class DocumentDB(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def search(self, embedding, **kwargs):
        pass


class QDrantDB(DocumentDB):
    def __init__(self) -> None:
        super().__init__()

        self.client = QdrantClient(
            host=settings.QDRANT_HOST,
            port=settings.QDRANT_PORT,
            timeout=120,
        )

    def create_collection(self, collection_name: str):
        # Check if collection exists and create if it doesn't
        collections = self.client.get_collections().collections
        collection_exists = any(
            collection.name == collection_name for collection in collections
        )

        if not collection_exists:
            self.client.recreate_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=settings.VECTOR_SIZE, distance=Distance.COSINE
                ),
            )
        return

    def insert(self, item_id: int, item: Article, collection_name: str):
        self.create_collection(collection_name)
        text = str(item.title) + " . " + str(item.content)
        vector = get_embedding(text)
        vector = np.array(vector, dtype=np.float32)
        result = self.client.upsert(
            collection_name=collection_name,
            points=[
                PointStruct(
                    id=int(item_id),
                    vector=vector,
                    payload=item.model_dump(),
                )
            ],
        )
        return result

    def delete(self, collection_name: str, item_id: int):
        """
        Delete a point from the specified Qdrant collection.

        Args:
            item_id (int): The ID of the point to delete
            collection_name (str): The name of the collection

        Returns:
            The result of the delete operation
        """
        result = self.client.delete(
            collection_name=collection_name, points_selector=[item_id]
        )
        # print(f"DELETE FROM {collection_name}: {result}")
        return result

    def search(self, embedding, collection_name: str) -> List[ScoredPoint]:
        docs = self.client.search(
            collection_name=collection_name,
            query_vector=embedding,
            limit=settings.TOPN,
        )
        if not docs:
            return []
        return docs

    def knowledges(self) -> Knowledges:
        knowledges = []
        for collection in self.client.get_collections().collections:
            info = self.client.get_collection(collection.name)

            knowledges.append(
                {
                    "collection_name": collection.name,
                    "documents_count": info.points_count,
                }
            )
        result = {"result": knowledges}
        return result

    def is_knowledge_exist(self, knowledge_id: str):
        knowledge_ids = [c.name for c in self.client.get_collections().collections]
        return knowledge_id in knowledge_ids


db = QDrantDB()
