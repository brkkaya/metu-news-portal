from typing import List, Tuple
from FlagEmbedding import FlagReranker
from langchain.schema import Document


class RerankerService:

    def __init__(self, retrieval_service_name: str):
        self.retrieval_service_name: str

        self.retrieval_service_name = retrieval_service_name
        self.model = FlagReranker(retrieval_service_name)

    def get_scores_documents(self, pairs: List[Tuple[str, str]]) -> List[List[float]]:
        try:
            scores = self.model.compute_score(pairs)
            return scores
        except Exception as e:
            raise Exception(f"Failed to encode query: {str(e)}")

    def sort_documents(self, documents: List[Document], query: str, top_k: int = 10) -> List[Document]:
        pairs = [(query, doc.page_content) for doc in documents]
        scores = self.get_scores_documents(pairs)
        sorted_docs_with_scores = sorted(zip(documents, scores), key=lambda x: x[1], reverse=True)
        sorted_documents = [doc for doc, score in sorted_docs_with_scores][:top_k]
        return sorted_documents
