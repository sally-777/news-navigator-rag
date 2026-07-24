import os
from importlib import import_module
from dotenv import load_dotenv
from openai import OpenAI

# استدعاء دالة بناء السياق من الملف السادس
build_context = import_module("06_retrieval_and_context").build_context

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini")


def build_prompt(question, context):
    return f"""You are a helpful and intelligent AI News Assistant.

Analyze the provided Context (which contains relevant news articles, summaries, or keywords) and answer the Question.

Instructions:
1. Synthesize the provided context into a clear, coherent, and informative response.
2. If the context contains relevant keywords or phrases, connect them intelligently to answer the user's question.
3. Prefer CURRENT sources over OUTDATED sources.
4. Cite sources like [Source 1], [Source 2] where appropriate.
5. Only say "I do not know" if the context is completely empty or totally unrelated to the question.

Question:
{question}

Context:
{context}
"""


def ask_openrouter(prompt):
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENROUTER_API_KEY,
    )
    response = client.chat.completions.create(
        model=OPENROUTER_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )
    return response.choices[0].message.content


def answer_question(question):
    context, sources, fetched_new_data = build_context(question)
    prompt = build_prompt(question, context)

    if not OPENROUTER_API_KEY or OPENROUTER_API_KEY.startswith("sk-or-v1-your"):
        return "Missing or invalid OPENROUTER_API_KEY.", sources, fetched_new_data

    try:
        answer = ask_openrouter(prompt)
        return answer, sources, fetched_new_data
    except Exception as e:
        return f"Error communicating with OpenRouter: {e}", sources, fetched_new_data