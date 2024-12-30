from typing import List, Union
from langchain_community.vectorstores.faiss import FAISS
from FlagEmbedding import BGEM3FlagModel
from langchain_core.embeddings import Embeddings

import json
from langchain.schema import Document
from langchain_community.vectorstores.faiss import DistanceStrategy


# load data
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

jsonl_files = [
    # ("data_raw/games_summary_fixed.jsonl","game"),
    ("data_raw/metu_scrape_summary_fixed.jsonl",'metu'),
    ("data_raw/news_summary_fixed.jsonl","sports"),
    ("data_raw/yeni_cnbc_sanat_summary_fixed.jsonl","art"),
    ("data_raw/yeni_economist_bilim_summary_fixed.jsonl","science"),
    ("data_raw/yeni_guardian_sanat_summary_fixed.jsonl","art"),
    ("data_raw/yeni_sciencenews_bilim_summary_fixed.jsonl","science"),
    ("data_raw/yeni_webtekno_bilim_summary_fixed.jsonl","science"),
]

metadata = []
texts = []
for file,topic in jsonl_files:
    with open(file, "r") as f:
        data = [json.loads(line) for line in f]
        texts += [d["body"] for d in data]
        metadata += [{"title": d["title"],"url":d.get("url",None), "img_url": d["img_url"], "summary":d['answer'],"topic": topic} for d in data]
        
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
