import os
import torch
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceBgeEmbeddings
from langchain.schema import Document
from docling.document_converter import DocumentConverter


from configuration import embeddings
from configuration import DIRECTORY_PATH,VECTORSORE_PATH




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

# # Set up HuggingFace embedding model
# model_name = "BAAI/bge-small-en-v1.5"
# model_kwargs = {'device': DEVICE}
# encode_kwargs = {'normalize_embeddings': True}
# embeddings = HuggingFaceBgeEmbeddings(
#     model_name=model_name,
#     model_kwargs=model_kwargs,
#     encode_kwargs=encode_kwargs
# )


def write_to_file(filename, text):
    with open(filename, 'w') as file:
        file.write(text)







def create_vectorstore_from_pdfs(pdf_filenames: list, vectorstore_name: str):
    """
    Create a FAISS vector store from a list of PDF files.

    Args:
        pdf_filenames (list): List of PDF file names (just file names, not full paths).
        vectorstore_name (str): Name for the output vector store (folder under 'Vectorstore').

    Returns:
        None
    """
    print("🚀 Starting PDF ingestion and vector store creation pipeline...")
    converter = DocumentConverter()
    documents = []

    for filename in pdf_filenames:
        pdf_path = os.path.join(DIRECTORY_PATH, filename)
        print(f"📄 Converting PDF: {pdf_path}")
        try:
            result = converter.convert(pdf_path)
            markdown_text = result.document.export_to_markdown()
            # write_to_file("output.txt", markdown_text)
            document = Document(page_content=markdown_text,metadata={"source": pdf_path})
            documents.append(document)
            print(f"✅ Successfully converted: {filename}")
        except Exception as e:
            print(f"❌ Failed to convert {filename}: {e}")

    if not documents:
        print("⚠️ No valid documents were loaded. Aborting vector store creation.")
        return

    print("✂️ Splitting documents into chunks...")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    split_texts = text_splitter.split_documents(documents)
    print(f"🔍 Total chunks created: {len(split_texts)}")

    print("📊 Generating vector store using FAISS...")
    vectorstore_path = os.path.join(VECTORSORE_PATH, vectorstore_name)
    os.makedirs(vectorstore_path, exist_ok=True)

    try:
        vectorstore = FAISS.from_documents(split_texts, embedding=embeddings)
        vectorstore.save_local(vectorstore_path)
        print(f"✅ Vector store saved at: {vectorstore_path}")
    except Exception as e:
        print(f"❌ Failed to create/save vector store: {e}")
        raise

    print("🏁 Vector store creation pipeline completed successfully.")





# Example usage:

# create_vs = create_vectorstore_from_pdfs(["Sound.pdf"], "sound")

