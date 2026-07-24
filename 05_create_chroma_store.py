from pathlib import Path
import chromadb
from chromadb.config import Settings

# مسار قاعدة البيانات داخل المشروع
DB_PATH = Path("./chroma_db")
COLLECTION_NAME = "news_navigator"


def get_or_create_client():
    return chromadb.PersistentClient(
        path=str(DB_PATH),
        settings=Settings(anonymized_telemetry=False),
    )


def get_or_create_store():
    client = get_or_create_client()
    return client.get_or_create_collection(COLLECTION_NAME)


def add_documents_to_store(chunked_docs, embeddings_list=None, batch_size=500):
    collection = get_or_create_store()
    if not chunked_docs:
        return collection

    ids = [str(doc["id"]) for doc in chunked_docs]
    documents = [str(doc["text"]) for doc in chunked_docs]

    # ✨ تم إضافة حقل الـ url هنا عشان الـ Frontend يقرأه ويظهره كـ رابط شغال
    metadatas = [
        {
            "title": str(doc["metadata"].get("title", "N/A")),
            "category": str(doc["metadata"].get("category", "general")),
            "is_current": str(doc["metadata"].get("is_current", True)),
            "url": str(doc["metadata"].get("url", "")),  # <--- إضافة مهمة جداً!
        }
        for doc in chunked_docs
    ]

    total_items = len(ids)

    # رفع البيانات على دفعات مع الحفاظ على البيانات القديمة دون مسحها
    for i in range(0, total_items, batch_size):
        end_idx = i + batch_size

        b_ids = ids[i:end_idx]
        b_docs = documents[i:end_idx]
        b_meta = metadatas[i:end_idx]

        if embeddings_list is not None:
            b_emb = embeddings_list[i:end_idx]
            collection.upsert(
                ids=b_ids,
                documents=b_docs,
                metadatas=b_meta,
                embeddings=b_emb,
            )
        else:
            collection.upsert(
                ids=b_ids,
                documents=b_docs,
                metadatas=b_meta,
            )

    return collection