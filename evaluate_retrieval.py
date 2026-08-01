from importlib import import_module

# استدعاء الـ Vector Store
chroma_store = import_module("05_create_chroma_store")
collection = chroma_store.get_or_create_store()

# 1. قائمة الـ Ground Truth (أسئلة حقيقية متوافقة مع الـ Chunks بتاعتك)
ground_truth_data = [
    {
        "question": "What is the future of TV and home theatre systems?",
        "expected_id": "bbc_doc_0_chunk_0",
    },
    {
        "question": "How will technology allow personalized TV content?",
        "expected_id": "bbc_doc_0_chunk_2",
    },
    {
        "question": "What affects advertising revenues and brand identity?",
        "expected_id": "bbc_doc_0_chunk_3",
    },
    {
        "question": "What happened with former WorldCom boss?",
        "expected_id": "bbc_doc_1_chunk_0",
    },
]


def evaluate_retrieval(k=5):
    hits = 0
    reciprocal_ranks = []

    for item in ground_truth_data:
        question = item["question"]
        expected_id = item["expected_id"]

        # 2. الاستعلام من ChromaDB (بدون include="ids" لأنها بتيجي تلقائياً)
        results = collection.query(
            query_texts=[question],
            n_results=k,
            include=["documents", "distances"],
        )

        retrieved_ids = results.get("ids", [[]])[0]

        # 3. حساب الـ Hit Rate والـ MRR
        found = False
        for rank, r_id in enumerate(retrieved_ids, start=1):
            if expected_id.lower() == r_id.lower():
                hits += 1
                reciprocal_ranks.append(1.0 / rank)
                found = True
                break

        if not found:
            reciprocal_ranks.append(0.0)

    total_queries = len(ground_truth_data)
    hit_rate = hits / total_queries if total_queries > 0 else 0
    mrr = sum(reciprocal_ranks) / total_queries if total_queries > 0 else 0

    print("\n==============================================")
    print(" 📊 RETRIEVAL EVALUATION RESULTS (Ground Truth)")
    print("==============================================")
    print(f"Total Test Queries: {total_queries}")
    print(f"Hit Rate@{k}: {hit_rate * 100:.2f}%")
    print(f"MRR (Mean Reciprocal Rank): {mrr:.4f}")
    print("==============================================\n")


if __name__ == "__main__":
    evaluate_retrieval(k=5)