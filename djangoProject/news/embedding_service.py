from typing import List, Union
from FlagEmbedding import BGEM3FlagModel
from langchain_core.embeddings import Embeddings


class EmbeddingService(Embeddings):

    def __init__(self, retrieval_service_name: str):

        self.retrieval_service_name: str

        self.retrieval_service_name = retrieval_service_name
        self.model = BGEM3FlagModel(retrieval_service_name)

    def embed_documents(self, text: Union[str, List[str]]) -> List[List[float]]:
        try:
            if isinstance(text, str):
                text = [text]
            encoded = self.model.encode(sentences=text, batch_size=2)["dense_vecs"]
            return encoded
        except Exception as e:
            raise Exception(f"Failed to encode query: {str(e)}")

    def embed_query(self, text):
        return self.embed_documents(text)[0]
