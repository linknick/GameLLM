"""Tiny wrapper showing how to use LlamaIndex (llama_index) to build a vector index.
In production you'll control chunk size, metadata, and embeddings provider.
"""
from llama_index import SimpleDirectoryReader, GPTVectorStoreIndex




def build_index_from_dir(data_dir: str, persist_path: str = None):
    # read docs from directory and build a small index
    docs = SimpleDirectoryReader(data_dir).load_data()
    index = GPTVectorStoreIndex.from_documents(docs)
    if persist_path:
        index.storage_context.persist(persist_path)
    return index




def query_index(index, query: str, k: int = 5):
    return index.as_query_engine().query(query)