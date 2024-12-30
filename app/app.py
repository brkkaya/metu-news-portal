from typing import List
from fastapi import FastAPI
from embedding_service import EmbeddingService
from news_schema import NewsSchema, QuerySchema, UserSchema
from reranker_service import RerankerService
from vector_db import Engine
from langchain.schema import Document
import uvicorn

app = FastAPI()
reranker = RerankerService("BAAI/bge-reranker-v2-m3")
vector_db = Engine("faiss_news_portal", EmbeddingService("BAAI/bge-m3"), reranker=reranker)


def convert_faiss_to_document(faiss_document: Document):
    return NewsSchema(
        title=faiss_document.metadata.get("title", None),
        content=faiss_document.page_content,
        img_url=faiss_document.metadata.get("img_url", None),
        url=faiss_document.metadata.get("url", None),
        date=faiss_document.metadata.get("date", None),
        topic=faiss_document.metadata.get("topic"),
    )


@app.get("/")
async def read_root():
    return {"Hello": "World"}


@app.post("/search")
async def search(query: QuerySchema) -> List[NewsSchema]:
    documents = vector_db.search(query.query, query.num_results)

    response = [convert_faiss_to_document(document) for document in documents]
    if query.topic:
        response = [doc for doc in response if doc.topic == query.topic]
    return response


@app.post("/recommend")
async def search(user_request: UserSchema) -> List[NewsSchema]:
    documents = vector_db.recommend(user_request.user_name)

    response = [convert_faiss_to_document(document) for document in documents]
    if user_request.topic:
        response = [doc for doc in response if doc.topic == user_request.topic]
    return response


if __name__ == "__main__":

    uvicorn.run(app)
