import os
from langchain_groq import ChatGroq
from chromadb import Client
import chromadb
from huggingface_hub import InferenceClient
from dotenv import load_dotenv


load_dotenv()


chroma_client = chromadb.CloudClient(
  api_key=os.getenv("CHROMA_API_KEY"),
  tenant=os.getenv("CHROMA_TENANT_ID"),
  database='ChatBotChallenge'
)

HF_TOKEN = os.getenv("HF_TOKEN")
HFClient = InferenceClient(provider="hf-inference", token=HF_TOKEN)
HF_MODEL_ID = os.getenv("HF_MODEL_ID")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL")
GROQ_API_URL = os.getenv("GROQ_API_URL")

collection = chroma_client.get_or_create_collection(name="tesa_embeddings")

llm = ChatGroq(
    model=GROQ_MODEL,
    temperature=0,
    max_tokens=None,
    reasoning_format="parsed",
    timeout=None,
    max_retries=2,
    api_key=GROQ_API_KEY
)


search_query = "What are Dietl's preferred dishes?"
raw_embedding = HFClient.feature_extraction(
    [search_query], 
    model=HF_MODEL_ID
)  

search_embedding = raw_embedding[0]

results = collection.query(
    query_embeddings=[search_embedding],
    n_results=1
)

# Safely extract cloud client responses [[[text]]]
try:
    if results["documents"] and len(results["documents"]) > 0:
        first_match = results["documents"][0]
        if isinstance(first_match, list) and len(first_match) > 0:
            retrieved_context = str(first_match[0])
        else:
            retrieved_context = str(first_match)
    else:
        retrieved_context = "No relevant context found in the database."
except Exception:
    retrieved_context = "No relevant context found in the database."

##print(f"\n[Retrieved Context]: {retrieved_context}")

messages = [
    (
        "system",
        "You are a helpful assistant. Answer the user's question using the provided context.",
    ),
    (
        "human", 
        f"Context:\n{retrieved_context}\n\nQuestion: {search_query}"
    ),
]

# print("\n=== Generating LLM Response ===")
# try:
#     ai_response = llm.invoke(messages)
#     print("\n[Groq Output]:")
#     # Some LLM clients return objects with `.content`, others return strings
#     content = getattr(ai_response, "content", None) or getattr(ai_response, "text", None) or str(ai_response)
#     print(content)
# except Exception as e:
#     print(f"LLM invocation failed: {e}\nFalling back to a simple answer using retrieved context.")
#     print("\n[Fallback Output]:")
#     print(retrieved_context)


