# pyrefly: ignore [missing-import]
from rag.vectordb import vector_store


def retrieve_context(query: str , chat_id: str):
    docs = vector_store.similarity_search(
        query=query,
        k=3,
         filter={
        "chat_id": chat_id
    }
          )
    context = "\n\n".join(
        doc.page_content
        for doc in docs
    )

    return context