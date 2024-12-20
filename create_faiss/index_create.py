from typing import List, Union
from langchain_community.vectorstores.faiss import FAISS
from FlagEmbedding import BGEM3FlagModel
from langchain_core.embeddings import Embeddings
import json
from langchain.schema import Document
from langchain_community.vectorstores.faiss import DistanceStrategy


class EmbeddingService(Embeddings):

    def __init__(self, retrieval_service_name: str):

        self.retrieval_service_name: str

        self.retrieval_service_name = retrieval_service_name
        self.model = BGEM3FlagModel(retrieval_service_name)

    def embed_documents(self, text: Union[str, List[str]]) -> List[List[float]]:
        try:
            if isinstance(text, str):
                text = [text]
            encoded = self.model.encode(sentences=text,batch_size=2)["dense_vecs"]
            return encoded
        except Exception as e:
            raise Exception(f"Failed to encode query: {str(e)}")

    def embed_query(self, text):
        return self.embed_documents(text)


embedding_model = EmbeddingService("BAAI/bge-m3")
# load data
with open("data/games.jsonl", "r") as f:
    data_games = [json.loads(line) for line in f]

with open("data/news.jsonl", "r") as f:
    data_news = [json.loads(line) for line in f][:1000]

texts = [d["body"] for d in data_games]
texts += [d["text"] for d in data_news]

metadata = [{"url": d["url"], "title": d["title"], "img_url": d["img_url"], "topic": "game"} for d in data_games]
metadata += [{"title": d["title"], "img_url": d["img_url"], "topic": "news"} for d in data_news]
# Step 2: Create a list of LangChain Documents
documents = []
for text, meta in zip(texts, metadata):
    documents.append(Document(page_content=text, metadata=meta))

# Step 3: Create a FAISS index
vector_store = FAISS.from_documents(
    documents,
    embedding_model,
    distance_strategy=DistanceStrategy.MAX_INNER_PRODUCT,
)

vector_store.save_local("faiss_game_new")

