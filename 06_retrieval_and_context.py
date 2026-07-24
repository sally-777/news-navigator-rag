from importlib import import_module
from news_api import fetch_external_news

prep = import_module("02_preprocessing")
chunking = import_module("03_chunking")
chroma_store = import_module("05_create_chroma_store")


def build_context(question, k=5, max_sources=3):
    collection = chroma_store.get_or_create_store()

    # 1. الاستعلام الأول من ChromaDB
    results = collection.query(
        query_texts=[question],
        n_results=k,
        include=["documents", "metadatas", "distances"],
    )

    docs = results.get("documents", [[]])[0]
    metas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    fetched_new_data = False

    # 2. لو مفيش نتائج أو النتائج بعيدة (Distance > 0.8) نطلب من News API
    if not distances or min(distances) > 0.8:
        raw_new_docs = fetch_external_news(question)
        if raw_new_docs:
            chunked_docs = chunking.chunk_documents(raw_new_docs)
            chroma_store.add_documents_to_store(chunked_docs)
            fetched_new_data = True

            # re-query بعد التحديث التراكمي
            results = collection.query(
                query_texts=[question],
                n_results=k,
                include=["documents", "metadatas", "distances"],
            )
            docs = results.get("documents", [[]])[0]
            metas = results.get("metadatas", [[]])[0]
            distances = results.get("distances", [[]])[0]

    # 3. تجهيز الـ rows بنفس طريقة الدكتور
    rows = []
    for doc, meta, dist in zip(docs, metas, distances):
        # نحول الـ distance إلى score (كل ما قل الـ distance كل ما زاد الـ similarity score)
        score = 1.0 - dist
        is_current = str(meta.get("is_current", "True")).lower() == "true"
        doc_id = meta.get("title", doc[:30])

        rows.append(
            {
                "document_id": doc_id,
                "title": meta.get("title", "Untitled Document"),
                "is_current": is_current,
                "chunk_text": doc,
                "score": score,
            }
        )

    # 4. الترتيب بأسلوب الدكتور (الأحدث والأعلى تقييماً)
    rows = sorted(
        rows, key=lambda row: (row["is_current"], row["score"]), reverse=True
    )

    selected = []
    seen_documents = set()

    for row in rows:
        if row["score"] <= 0:
            continue
        if row["document_id"] in seen_documents:
            continue
        selected.append(row)
        seen_documents.add(row["document_id"])
        if len(selected) == max_sources:
            break

    # 5. صياغة الـ Context النهائي بنفس شكل الدكتور تماماً
    context = ""
    for source_number, row in enumerate(selected, start=1):
        status = "CURRENT" if row["is_current"] else "OUTDATED"
        context += f"[Source {source_number}] {row['title']} ({status})\n{row['chunk_text']}\n\n"

    return context.strip(), selected, fetched_new_data