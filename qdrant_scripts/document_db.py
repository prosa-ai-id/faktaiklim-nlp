import abc
from typing import List

from config import settings
from qdrant_client import QdrantClient
from qdrant_client.grpc import ScoredPoint
from schema import Knowledges


class DocumentDB(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def search(self, embedding, **kwargs):
        pass


class QDrantDB(DocumentDB):
    def __init__(self) -> None:
        super().__init__()

        self.client = QdrantClient(settings.QDRANT_HOST, port=settings.QDRANT_PORT)

    def search(self, embedding, collection_name: str) -> List[ScoredPoint]:
        docs = self.client.search(
            collection_name=collection_name,
            query_vector=embedding,
            limit=2,
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
                    "id": collection.name,
                    "name": collection.name.title(),
                    "documents_count": info.vectors_count,
                }
            )
        return knowledges

    def is_knowledge_exist(self, knowledge_id: str):
        knowledge_ids = [c.name for c in self.client.get_collections().collections]
        return knowledge_id in knowledge_ids


db = QDrantDB()
