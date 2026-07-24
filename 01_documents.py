import pandas as pd

def get_initial_documents(csv_path="bbc-text.csv"):
    df = pd.read_csv(csv_path)
    documents = []
    for idx, row in df.iterrows():
        documents.append({
            "id": f"bbc_doc_{idx}",
            "title": f"BBC News - {row['category'].capitalize()} Article {idx}",
            "is_current": True,
            "category": row["category"],
            "text": row["text"]
        })
    return documents