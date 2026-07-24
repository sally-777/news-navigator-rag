# ⚡ SATECK News Intelligence Platform (Hybrid RAG System)

An AI-driven **Retrieval-Augmented Generation (RAG)** platform designed to analyze, summarize, and query both historical news datasets (BBC Dataset) and real-time live news feeds using Gemini AI and ChromaDB.

---

## 🌟 Key Features

- **Hybrid Knowledge Base:** Combines local historical BBC news data with live web search APIs for up-to-date query context.
- **Incremental Indexing:** Dynamically fetches and indexes new articles directly into ChromaDB without wiping existing historical records.
- **Fact-Checked Citations:** Generates AI summaries grounded strictly in retrieved sources to prevent hallucinations.
- **Cross-Lingual Support:** Seamlessly handles queries in Arabic and English.
- **Interactive UI:** Streamlit interface supporting category filters and Enter-key query submission.

---

## 🏗️ System Architecture & Workflow

```text
[ User Query ]
      │
      ▼
[ ChromaDB Retrieval ] ──(If Context Insufficient)──► [ Live News API ]
      │                                                     │
      └─────────────────────┬───────────────────────────────┘
                            ▼
               [ Context Aggregation & Prompting ]
                            │
                            ▼
                    [ Gemini LLM Engine ]
                            │
                            ▼
             [ AI Summary + Verified Citations ]