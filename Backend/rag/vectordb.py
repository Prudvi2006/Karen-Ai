# pyrefly: ignore [missing-import]
from langchain_chroma import Chroma
from rag.embedding import embedding_model

DB_PATH = "chroma_db"

vector_store = Chroma(
    collection_name="documents",
    embedding_function=embedding_model,
    persist_directory=DB_PATH
)