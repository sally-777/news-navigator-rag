from importlib import import_module

preprocess_text = import_module("02_preprocessing").preprocess_text


def chunk_text(text, chunk_size=60, overlap=15):
    words = text.split()
    chunks = []
    start = 0

    while start < len(words):
        end = start + chunk_size
        chunks.append(" ".join(words[start:end]))
        if end >= len(words):
            break
        start += chunk_size - overlap

    return chunks


def chunk_documents(documents):
    chunked_docs = []

    for doc in documents:
        for chunk_number, chunk in enumerate(chunk_text(doc["text"])):
            chunked_docs.append(
                {
                    "id": f"{doc['id']}_chunk_{chunk_number}",
                    "text": chunk,
                    "search_text": preprocess_text(f"{doc['title']} {chunk}"),
                    "metadata": {
                        "title": doc["title"],
                        "category": doc.get("category", "general"),
                        "is_current": doc.get("is_current", True),
                        "url": doc.get("url", ""),  # 👈 تم إضافة الرابط هنا ليصل إلى ChromaDB
                    },
                }
            )

    return chunked_docs
