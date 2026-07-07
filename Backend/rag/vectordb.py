from langchain_chroma import Chroma
from rag.embedding import get_embedding_model

DB_PATH = "chroma_db"

vector_store = None


def get_vector_store():

    global vector_store

    if vector_store is None:

        vector_store = Chroma(
            collection_name="documents",
            embedding_function=get_embedding_model(),
            persist_directory=DB_PATH
        )

    return vector_store