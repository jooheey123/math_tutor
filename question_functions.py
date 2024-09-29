from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader



def get_goals():
        # Initialize the OpenAI embedding model
    embedding_model = OpenAIEmbedding(model="text-embedding-ada-002")

    # Load documents from a directory (you can change this path as needed)
    documents = SimpleDirectoryReader("data").load_data()

    # Create an index from the documents
    index = VectorStoreIndex.from_documents(documents)

    # Create a query engine
    query_engine = index.as_query_engine()

    # Query
    response = query_engine.query("What are the main things to learn?")
    fc_response = str(response)
    return fc_response