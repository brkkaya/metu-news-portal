from typing import List, Union
import numpy as np
import requests
from langchain_core.embeddings import Embeddings
from tqdm import tqdm
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class RetrievalService(Embeddings):

    def __init__(self):

        self.retrieval_service_name: str
        self.url_query: str
        self.url_document: str
        self.dimension: int
        self.info: str

        self.url_query = "https://llm-embedding-bge-ft-ai-chatbot.apps.tocpgt01.tcs.turkcell.tgc" + "/embedding_query"
        self.url_document = (
            "https://llm-embedding-bge-ft-ai-chatbot.apps.tocpgt01.tcs.turkcell.tgc" + "/embedding_document"
        )

    def _embed_documents(self, text: Union[str, List[str]]) -> List[List[float]]:
        try:
            if isinstance(text, str):
                text = [text]
            elif not isinstance(text, list) or not all(isinstance(t, str) for t in text):
                raise RuntimeError("Input 'text' must be a string or a list of strings.")
            output = []
            for d in tqdm(text):
                response = requests.post(self.url_document, json={"text": d}, timeout=300, verify=False)  # FIX ON PROD
                response.raise_for_status()

                embeddings = [data["embedding"] for data in response.json()["data"]]
                output.append(embeddings)
            return np.asarray(output).squeeze(1).tolist()
        except Exception as err:
            return self._embed_documents(text=text)

    def _embed_query(self, text: str) -> List[float]:
        try:
            response = requests.post(self.url_query, json={"text": text}, timeout=300, verify=False)  # FIX ON PROD
            response.raise_for_status()

            embeddings = [data["embedding"] for data in response.json()["data"]]
            return np.asarray(embeddings).reshape(-1).tolist()
        except Exception as err:
            return self._embed_query(text=text)

    def embed_query(self, text: str) -> List[float]:
        out = self._embed_query(text=text)
        return out

    def embed_documents(self, document: str) -> List[float]:
        embedding = self._embed_documents(text=document)
        return embedding
