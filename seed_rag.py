import os
import uuid
from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from huggingface_hub import InferenceClient
import chromadb

load_dotenv()

# Chroma / HF configuration
chroma_client = chromadb.CloudClient(
    api_key=os.getenv("CHROMA_API_KEY"),
    tenant=os.getenv("CHROMA_TENANT_ID"),
    database=os.getenv("CHROMA_DATABASE", "ChatBotChallenge")
)

HF_TOKEN = os.getenv("HF_TOKEN")
HFClient = InferenceClient(provider="hf-inference", token=HF_TOKEN)
HF_MODEL_ID = os.getenv("HF_MODEL_ID")

collection = chroma_client.get_or_create_collection(name=os.getenv("CHROMA_COLLECTION", "tesa_embeddings"))

favFoods = "Alexis Dietl's favourite foods are asado, hotDogs, sweetbreads and dulce de leche cake. Although I can tell as well I love the typical south korean types of foods. All kinds of them, like rice with pork and kimchi, or the famous korean barbecue. I also like to eat a lot of fruits, especially in the summer, like watermelon and peaches. I also have a sweet tooth, so I enjoy desserts like ice cream and chocolate cake. Overall, I have a diverse palate and enjoy trying new foods from different cuisines around the world."

randomText = "Space exploration is the use of astronomy and space technology to explore outer space. Since the first artificial satellite—Sputnik 1—launched in 1957, humanity has sent robotic probes and humans to explore the cosmos. I want to also mark down many influences in the academy."

# Build documents and split
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

doc_1 = Document(page_content=favFoods)
doc_2 = Document(page_content=randomText)
docs = [doc_1, doc_2]

text_splitter = RecursiveCharacterTextSplitter(chunk_size=600, chunk_overlap=100)
splits = text_splitter.split_documents(docs)
text_chunks = [split.page_content for split in splits]

# Create embeddings
embeddings = HFClient.feature_extraction(
    text_chunks,
    model=HF_MODEL_ID
)

# ChromaDB requires a unique string ID for every document inserted
ids = [str(uuid.uuid4()) for _ in text_chunks]

# Upsert into ChromaDB
print("Saving vectors to ChromaDB...")
collection.upsert(
    ids=ids,
    embeddings=embeddings,
    documents=text_chunks,
)

print(f"✅ Successfully saved {len(text_chunks)} vectors to ChromaDB!")
