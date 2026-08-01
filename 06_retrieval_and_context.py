import re
from importlib import import_module
from news_api import fetch_external_news

prep = import_module("02_preprocessing")
chunking = import_module("03_chunking")
chroma_store = import_module("05_create_chroma_store")


def build_context(question, k=5, max_sources=3):
    collection = chroma_store.get_or_create_store()

    # 0. تنظيف السؤال من أي توجيهات بين أقواس لاستخدامه في البحث المباشر
    clean_search_query = re.sub(r"\(.*?\)", "", question).strip()
    if not clean_search_query:
        clean_search_query = question

    # 1. الاستعلام الأول من ChromaDB باستخدام السؤال النظيف
    results = collection.query(
        query_texts=[clean_search_query],
        n_results=k,
        include=["documents", "metadatas", "distances"],
    )

    docs = results.get("documents", [[]])[0]
    metas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    fetched_new_data = False

    # 2. فحص هل النتائج غير كافية أو غير متطابقة لجلب أخبار خارجية
    # إذا كانت القائمة فارغة أو أفضل نتيجة ضعيفة (Distance > 0.4)
    should_fetch_api = not distances or (len(distances) > 0 and min(distances) > 0.4)

    if should_fetch_api:
        # البحث في الـ API بالسؤال النظيف تماماً
        raw_new_docs = fetch_external_news(clean_search_query)
        
        if raw_new_docs:
            chunked_docs = chunking.chunk_documents(raw_new_docs)
            chroma_store.add_documents_to_store(chunked_docs)
            fetched_new_data = True

            # إعادة الاستعلام بعد إضافة الأخبار الجديدة
            results = collection.query(
                query_texts=[clean_search_query],
                n_results=k,
                include=["documents", "metadatas", "distances"],
            )
            docs = results.get("documents", [[]])[0]
            metas = results.get("metadatas", [[]])[0]
            distances = results.get("distances", [[]])[0]

    # 3. تجهيز البيانات وتحسين استخراج الميتا داتا والروابط
    rows = []
    for doc, meta, dist in zip(docs, metas, distances):
        # تحويل الـ distance إلى similarity score
        score = 1.0 - dist
        is_current = str(meta.get("is_current", "True")).lower() == "true"
        doc_id = meta.get("title", doc[:30])

        # جلب رابط المقال الأصلي بدقة
        article_url = meta.get("url") or meta.get("link") or ""

        rows.append(
            {
                "document_id": doc_id,
                "title": meta.get("title", "Untitled Document"),
                "is_current": is_current,
                "chunk_text": doc,
                "text": doc,
                "url": article_url,
                "score": score,
            }
        )

    # 4. الترتيب (الأحدث والأعلى تقييماً)
    rows = sorted(
        rows, key=lambda row: (row["is_current"], row["score"]), reverse=True
    )

    selected = []
    seen_documents = set()

    for row in rows:
        if row["document_id"] in seen_documents:
            continue
        selected.append(row)
        seen_documents.add(row["document_id"])
        if len(selected) == max_sources:
            break

    # 5. صياغة الـ Context الموجه للذكاء الاصطناعي
    context = ""
    for source_number, row in enumerate(selected, start=1):
        status = "CURRENT" if row["is_current"] else "OUTDATED"
        context += f"[Source {source_number}] {row['title']} ({status})\n{row['chunk_text']}\n\n"

    return context.strip(), selected, fetched_new_data
