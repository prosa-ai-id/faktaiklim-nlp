import json
import re
from typing import Dict, List

from app import schema
from app.config import settings
from app.core.document_db import db
from app.core.search import ClimateSearch
from app.core.utils import predict_doc_cls, predict_doc_multi_cls, predict_doc_pair_cls
from app.log import logger


class Climate:
    def __init__(self):
        self.cs = ClimateSearch()
        self.first_similarity_threshold = 0.90  # use this to check if query input is copy pasted from first search item result
        return

    def determine_hoax_status(self, item: schema.Article):
        hoax_list = ["hoaks", "hoax", "misinformasi", "salah", "penipuan", "fitnah"]
        c = item.classification
        c = c.lower().strip()
        hoax_status = "fact"
        if c in hoax_list:
            hoax_status = "hoax"
        return hoax_status

    def insert_article(self, item_id: int, item: schema.Article):
        hoax_status = self.determine_hoax_status(item)
        collection_name = settings.FACT_COLLECTION_NAME
        if hoax_status == "hoax":
            collection_name = settings.HOAX_COLLECTION_NAME
        db_result = db.insert(item_id, item, collection_name)
        db_status = db_result.status
        status = "inserted" if db_status == "completed" else "not inserted"
        result = {"status": f"item id {item_id} is {status} into {collection_name}"}
        return result

    def delete_article(self, item_id: int):
        collection_names = [
            settings.HOAX_COLLECTION_NAME,
            settings.FACT_COLLECTION_NAME,
        ]
        # result = {"status": f"item id {item_id} is not deleted from {collection_names}"}
        for collection_name in collection_names:
            db_result = db.delete(collection_name, item_id)
            db_status = db_result.status
            # if db_status == "completed":
            #     status = "deleted"
            #     result = {"status": f"item id {item_id} is {status} from {collection_name}"}
            #     return result
        cs = ", ".join(collection_names)
        result = {"status": f"item id {item_id} is deleted from {cs}"}
        return result

    def get_subtopic_text(self, topics: List[str], text: str) -> str:
        if not topics:
            return text
        topics_str = "\n".join(topics)
        subtopic_text = f"TOPIK ARTIKEL:\n{topics_str}\nTEKS BERITA:\n{text}"
        # logger.info(f"\nSUBTOPIC TEXT:\n{subtopic_text[:200]}..")
        return subtopic_text

    def get_topic_subtopic(self, text: str) -> dict:
        # logger.info(f"INPUT TEXT FOR /topic : {text[:100]}..")
        logger.info(f"INPUT TEXT FOR /topic : {text}..")

        topic_url = settings.TOPIC_SERVING_URL
        topic2score = predict_doc_multi_cls(topic_url, text)

        subtopic_url = settings.SUBTOPIC_SERVING_URL
        subtopic_text = self.get_subtopic_text(topic2score.keys(), text)
        subtopic2score = predict_doc_multi_cls(subtopic_url, subtopic_text)

        result = {"topic": topic2score, "subtopic": subtopic2score}
        return result

    def get_stance(self, text: str, searched_text: str) -> str:
        stance_url = settings.STANCE_SERVING_URL
        stance, confidence = predict_doc_pair_cls(stance_url, text, searched_text)
        return stance

    def update_hoax_status(self, text: str, doc: Dict) -> Dict:
        title = doc["title"]
        content = doc["content"]
        searched_text = f"{title} . {content}"
        stance = self.get_stance(text, searched_text)

        hoax_status = doc["hoax_status"]
        # if stance == "unrelated":
        # logger.info(f"FOUND UNRELATED. text: '{text[:30]}..' text_from_search_result: '{searched_text[:30]}..'")
        # hoax_status = stance
        # elif stance == "oppose":
        if stance == "oppose":
            # logger.info(f"FOUND OPPOSE. text: {text[:30]}. searched_text: {searched_text[:30]}")
            hoax_status = "hoax" if hoax_status == "fact" else "fact"
        doc["hoax_status"] = hoax_status
        doc["stance"] = stance
        # return stance
        return doc

    def calculate_hoax_probability(self, docs: List[Dict]) -> float:
        prob = 0
        if settings.USE_DB_SCORE:
            all_db_scores = sum(d["score"] for d in docs)
            hoax_db_scores = sum(d["score"] for d in docs if d["hoax_status"] == "hoax")
            # print(f"HOAX DB SCORES: {hoax_db_scores}")
            # print(f"ALL DB SCORES: {all_db_scores}")
            prob = hoax_db_scores / all_db_scores
        else:
            hoax_count = 0
            fact_count = 0
            for i, doc in enumerate(docs):
                hoax_status = doc["hoax_status"]
                hoax_count += hoax_status == "hoax"
                fact_count += hoax_status == "fact"
            prob = hoax_count / (hoax_count + fact_count)
        return prob

    def clean_string(self, text):
        text = str(text)
        text = text.replace("\\xe2\\x80\\x99", "'")
        text = text.replace("\\xe2\\x80\\x98", "'")
        text = text.replace("\\xe2\\x80\\x9c", '"')
        text = text.replace("\\xe2\\x80\\x9d", '"')
        text = text.replace("\\xe2\\x80\\x93", "-")
        text = text.replace("\\xe2\\x80\\x94", "-")
        cleaned = re.sub(r"[^a-z\s]", " ", text.lower())
        return " ".join(cleaned.split())

    def calculate_similarity(self, text: str, first_doc_text: str) -> float:
        """
        Calculate similarity between two text strings using character-level n-grams and Jaccard similarity.

        Args:
            text (str): Input text to compare
            first_doc_text (str): Document text to compare against

        Returns:
            float: Similarity score between 0 and 1, where 1 indicates identical texts
        """

        def get_ngrams(string: str, n: int = 3) -> set:
            """Generate character n-grams from string."""
            return set(string[i : i + n] for i in range(len(string) - n + 1))

        # Handle edge cases
        if not text or not first_doc_text:
            return 0.0
        if text == first_doc_text:
            return 1.0

        # Generate n-grams for both texts
        text_ngrams = get_ngrams(text)
        doc_ngrams = get_ngrams(first_doc_text)

        # Calculate Jaccard similarity
        intersection = len(text_ngrams.intersection(doc_ngrams))
        union = len(text_ngrams.union(doc_ngrams))

        if union == 0:
            return 0.0

        similarity = intersection / union
        return similarity

    def check_ngram(self, cleaned_text: str, docs: List[Dict]):
        first_doc = docs[0]
        first_doc_title = self.clean_string(first_doc["title"])
        first_doc_content = self.clean_string(first_doc["content"])
        title_similarity = self.calculate_similarity(cleaned_text, first_doc_title)
        # print(f"FIRST TITLE SIMILARITY: {title_similarity}")
        found_similar = False

        if title_similarity > self.first_similarity_threshold:
            # print(f"SIMILAR WITH 1ST TITLE: {first_doc_title}")
            found_similar = True
        else:
            content_similarity = self.calculate_similarity(
                cleaned_text, first_doc_content
            )
            # print(f"FIRST CONTENT SIMILARITY: {content_similarity}")
            if content_similarity > self.first_similarity_threshold:
                # print(f"SIMILAR WITH 1ST CONTENT: {first_doc_content}")
                found_similar = True
            else:
                first_doc_title_content = f"{first_doc_title} {first_doc_content}"
                title_content_similarity = self.calculate_similarity(
                    cleaned_text, first_doc_title_content
                )
                # print(f"FIRST TITLE+CONTENT SIMILARITY: {title_content_similarity}")
                if title_content_similarity > self.first_similarity_threshold:
                    # print(f"SIMILAR WITH 1ST TITLE+CONTENT: {first_doc_title_content}")
                    found_similar = True
        if found_similar:
            docs[0]["score"] *= 100
        return docs

    def get_title_jaccard(self, cleaned_text, docs):
        for doc in docs:
            doc_title = self.clean_string(doc["title"])
            title_similarity = self.calculate_similarity(cleaned_text, doc_title)
            doc["jaccard_score"] = title_similarity
        return docs

    def rearrange_using_jaccard(
        self, cleaned_text: str, docs: List[Dict]
    ) -> List[Dict]:
        """
        Rearrange documents based on Jaccard similarity scores between input text and document titles.
        If the highest scoring document exceeds the similarity threshold, it's moved to the front
        and its score is amplified.

        Args:
            text (str): Input text to compare against document titles
            docs (List[Dict]): List of document dictionaries

        Returns:
            List[Dict]: Rearranged list of documents
        """
        if not docs:
            return docs

        # Calculate Jaccard scores for all documents
        docs = self.get_title_jaccard(cleaned_text, docs)

        # Find document with highest Jaccard score
        max_jaccard_doc = max(docs, key=lambda x: x.get("jaccard_score", 0))
        max_jaccard_score = max_jaccard_doc.get("jaccard_score", 0)

        # If highest score exceeds threshold, rearrange docs
        found_similar = False
        if max_jaccard_score >= self.first_similarity_threshold:
            # Remove the max scoring doc from its current position
            docs.remove(max_jaccard_doc)
            # Amplify its score
            max_jaccard_doc["score"] *= 100
            # Insert it at the beginning
            docs.insert(0, max_jaccard_doc)
            found_similar = True

        return docs, found_similar

    def check_veracity(self, text: str) -> dict:
        logger.info(f"INPUT TEXT FOR /check : {text[:100]}..")
        cleaned_text = self.clean_string(text)
        docs = self.cs.search(text)
        new_docs = []
        for doc in docs:
            # stance = self.update_hoax_status(text, doc)
            # if stance != "unrelated":
            #     doc["stance"] = stance
            doc = self.update_hoax_status(text, doc)
            if doc["stance"] != "unrelated":
                new_docs.append(doc)

            if len(new_docs) == settings.TOPN:
                break
        new_docs, found_similar = self.rearrange_using_jaccard(cleaned_text, new_docs)
        if not found_similar:
            new_docs = self.check_ngram(cleaned_text, new_docs)
        docs = new_docs

        hoax_probability = self.calculate_hoax_probability(docs)
        result = {"relevant_items": docs, "hoax_probability": hoax_probability}

        return result
