from collections import defaultdict
from langchain_community.vectorstores.faiss import FAISS
from langchain_community.vectorstores.faiss import DistanceStrategy
from typing import List
from langchain.schema import Document
from news.reranker_service import RerankerService
from news.bm25_service import BM25Service
from news.embedding_service import EmbeddingService
from news.user_history import UserHistoryService


class Engine:
    def __init__(self, index_path: str, embedding_model: EmbeddingService, reranker: RerankerService):
        self.vector_store = FAISS.load_local(index_path, embedding_model, allow_dangerous_deserialization=True)
        self.bm25_service = BM25Service()
        self.reranker = reranker
        self.user_history = UserHistoryService("data/user_history_doc.json", "data/user_history_query.json")
        self.load_data()

    def load_data(self):
        docstore_ids = self.vector_store.index_to_docstore_id
        # Access the docstore
        docstore = self.vector_store.docstore

        # Extract all documents
        self.all_documents = [docstore.search(doc_id) for doc_id in docstore_ids.values()]
        self.bm25_service.create(documents=self.all_documents)

    def search(self, query: str, k: int = 5, apply_rerank: bool = True) -> List[Document]:
        docs = self.vector_store.similarity_search(query, k=k, distance_strategy=DistanceStrategy.MAX_INNER_PRODUCT)
        docs += self.bm25_service.query(query, k)
        if apply_rerank:
            docs = self.reranker.sort_documents(docs, query)
        return docs

    def recommend(self, id: str) -> List[Document]:
        doc_ids, queries = self.user_history.get_user_history(id)
        if not doc_ids:  # if not exists return recents
            return []

        doc_ids = doc_ids[-10:]
        queries = queries[-10:]

        documents: List[Document] = [
            self.vector_store.docstore.search(self.vector_store.index_to_docstore_id[idx]) for idx in doc_ids
        ]
        docs: List[Document] = []
        for document in documents:
            docs += self.search(document.page_content, 5, apply_rerank=False)

        for query in queries:
            docs += self.search(query, 5, apply_rerank=False)

        seen = set()
        unique_docs = []
        for doc in docs:
            if doc.page_content not in seen:
                unique_docs.append(doc)
                seen.add(doc.page_content)
        sorted_docs_by_query = self.reranker.sort_documents(unique_docs, queries[-1])
        sorted_docs_by_doc = self.reranker.sort_documents(unique_docs, documents[-1].page_content)

        docs = rank_fusion([sorted_docs_by_query, sorted_docs_by_doc])
        return docs


def rank_fusion(ranked_lists: List[List[Document]], k: int = 60) -> List[Document]:
    """Apply Reciprocal Rank Fusion to combine ranked lists."""
    score_dict = defaultdict(float)

    for ranked_list in ranked_lists:
        for rank, doc in enumerate(ranked_list):
            doc_id = ranked_list.index(doc)  # Use unique identifier
            score_dict[doc_id] += 1 / (k + rank + 1)

    # Sort documents by combined scores
    fused_docs = sorted(score_dict.items(), key=lambda x: x[1], reverse=True)
    return [doc for doc_id, _ in fused_docs for doc in ranked_lists[0] if ranked_lists[0].index(doc) == doc_id]
