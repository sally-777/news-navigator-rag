from importlib import import_module

chroma_store = import_module("05_create_chroma_store")
collection = chroma_store.get_or_create_store()

# استخراج أول 10 عناصر من ChromaDB
data = collection.get(limit=10)
for doc_id, text in zip(data["ids"], data["documents"]):
    print(f"ID: {doc_id} | Snippet: {text[:50]}...")           