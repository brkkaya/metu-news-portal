from news.models import NewsSchema
from langchain.schema import Document


def convert_faiss_to_document(faiss_document: Document):
    return NewsSchema(
        title=faiss_document.metadata.get("title", None),
        content=faiss_document.page_content,
        img_url=faiss_document.metadata.get("img_url", None),
        url=faiss_document.metadata.get("url", None),
        date=faiss_document.metadata.get("date", None),
        topic=faiss_document.metadata.get("topic"),
    )
