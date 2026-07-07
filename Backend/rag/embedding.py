embedding_model = None


def get_embedding_model():

    global embedding_model

    if embedding_model is None:

        from langchain_huggingface import HuggingFaceEmbeddings

        embedding_model = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2",
            model_kwargs={
                "device": "cpu"
            }
        )

    return embedding_model