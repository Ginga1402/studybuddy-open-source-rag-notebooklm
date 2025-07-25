import os
import torch
from langchain.embeddings import HuggingFaceBgeEmbeddings
from langchain_community.chat_models import ChatOllama



# Initialize device for embeddings (CUDA if available)
print("=" * 100)
try:
    cuda_available = torch.cuda.is_available()
    print(f"✅ CUDA Available: {cuda_available}")
    DEVICE = "cuda" if cuda_available else "cpu"
    print(f"🧠 Using torch version: {torch.__version__} | Device: {DEVICE}")
except Exception as e:
    print(f"❌ Error checking Torch CUDA availability: {e}")
    DEVICE = "cpu"
print("=" * 100)



# Set up HuggingFace embedding model
model_name = "BAAI/bge-small-en-v1.5"
model_kwargs = {'device': DEVICE}
encode_kwargs = {'normalize_embeddings': True}
embeddings = HuggingFaceBgeEmbeddings(
    model_name=model_name,
    model_kwargs=model_kwargs,
    encode_kwargs=encode_kwargs
)


DIRECTORY_PATH = "/PROVIDE_YOUR_PATH/studybuddy/Data"
VECTORSORE_PATH = "/PROVIDE_YOUR_PATH/studybuddy/vector_store"


llm = ChatOllama(base_url="http://localhost:11434" model="gemma3:12b-it-q4_K_M", temperature=0.3)
