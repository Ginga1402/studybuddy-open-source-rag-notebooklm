from langchain import PromptTemplate
from langchain.chains import RetrievalQA
from langchain.vectorstores import FAISS
import torch
import os

from configuration import llm,embeddings,VECTORSORE_PATH




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



prompt_template = """Use the following pieces of information to answer the user's question.
If you don't know the answer, just say that you don't know, don't try to make up an answer.

Context: {context}
Question: {question}

Only return the helpful answer below and nothing else.
Helpful answer:
"""


def generate_answer(question: str, vector_store_name: str):
    """
    Generates an answer using RAG by retrieving context from a vector store.

    Args:
        question (str): The user's question.
        vector_store_name (str): Name of the FAISS vector store.

    Returns:
        Tuple[str, str]: The answer and the source document's filename.
    """
    try:
        vector_store_path = os.path.join(VECTORSORE_PATH, vector_store_name)
        print(f"📂 Loading vector store from: {vector_store_path}")
        vector_store = FAISS.load_local(vector_store_path, embeddings, allow_dangerous_deserialization=True)
        print("✅ Vector store loaded.")
    except Exception as e:
        print(f"❌ Failed to load vector store: {e}")
        return f"Error: Could not load vector store. {str(e)}", None

    try:
        print("🔍 Creating retriever and QA chain...")
        retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 3})
        prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])

        qa = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=retriever,
            return_source_documents=True,
            chain_type_kwargs={"prompt": prompt},
            verbose=True
            

        )

        print(f"💬 Asking question: '{question}'")
        response = qa.invoke({"query": question})
        print("✅ Answer generated.")

        answer = response['result']
        source = response['source_documents'][0].metadata.get('source', 'Unknown')

        print(f"📝 Answer: {answer}")
        print(f"📄 Source: {source}")
        return answer, source

    except Exception as e:
        print(f"❌ Failed to generate answer: {e}")
        return f"Error: Failed to answer question. {str(e)}", None





# answer,source = generate_answer(question = "CHARACTERISTICS OF A SOUND WAVE", vector_store_name = "sound")

# print("answer::::  " , answer)
# print("source:   ", source)
