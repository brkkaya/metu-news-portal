from rank_bm25 import BM25Okapi
from typing import List
from langchain.schema import Document


class BM25Service:
    def __init__(self):
        self.bm25 = None
        self.documents: List[Document] = []

    def create(self, documents: List[str]):
        self.documents.extend(documents)
        tokenized_documents = [doc.page_content.split() for doc in self.documents]
        self.bm25 = BM25Okapi(tokenized_documents)

    def query(self, query: str, n_results: int = 5) -> List[int]:
        tokenized_query = query.split()
        scores = self.bm25.get_scores(tokenized_query)
        top_n_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:n_results]
        return [self.documents[indices] for indices in top_n_indices]

    def get_document(self, index: int) -> str:
        return self.documents[index]
