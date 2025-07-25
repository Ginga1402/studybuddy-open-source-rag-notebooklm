# from langchain_community.chat_models import ChatOllama
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.output_parsers import StrOutputParser
import torch
from langchain.vectorstores import FAISS
from configuration import llm,embeddings,VECTORSORE_PATH
import os


def diagram_creation(subject: str, vector_store_name: str) -> str:
    """
    Creates an ASCII diagram based on subject using context from a vector store.

    Args:
        subject (str): Topic for which the diagram is to be generated.
        vector_store_path (str): Path to the saved FAISS vector store.

    Returns:
        str: ASCII flowchart as a string.
    """
    try:
        vector_store_path = os.path.join(VECTORSORE_PATH, vector_store_name)
        print(f"📂 Loading vector store from: {vector_store_path}")
        vector_store = FAISS.load_local(vector_store_path, embeddings, allow_dangerous_deserialization=True)
        print("✅ Vector store loaded successfully.")
    except Exception as e:
        print(f"❌ Failed to load vector store: {e}")
        return f"Error: Unable to load vector store. {str(e)}"

    try:
        print(f"🔍 Setting up retriever with subject: '{subject}'")
        retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 5})
        content = retriever.invoke(subject)
        print(f"📚 Retrieved {len(content)} relevant chunks from the vector store.")
    except Exception as e:
        print(f"❌ Error during retrieval: {e}")
        return f"Error: Failed to retrieve content. {str(e)}"

    try:
        full_text = "".join([doc.page_content for doc in content])

        print("🧠 Preparing diagram generation prompt...")
        prompt = PromptTemplate(
            template="""
            You are an expert at summarizing technical content into clear and concise diagrams.

            Using the provided context, generate an ASCII flowchart that summarizes the key concepts related to the subject: **{subject}**.

            Guidelines:
            - Use simple ASCII characters like '-', '|', '+', and '>' to draw the flowchart.
            - Organize up to 10 major points in a logical sequence or hierarchy.
            - Keep it clear, readable, and easy to follow.
            - Each node should represent a key idea or step from the context.
            - Avoid repeating content verbatim — summarize meaningfully.

            Context:
            {context}
            """,
            input_variables=["subject", "context"]
        )

        diagram_creator = prompt | llm | StrOutputParser()
        print("✏️ Generating ASCII diagram...")
        diagram = diagram_creator.invoke({"subject": subject, "context": full_text})
        print("✅ Diagram generated successfully.\n")

        return diagram

    except Exception as e:
        print(f"❌ Diagram generation failed: {e}")
        return f"Error: Failed to generate diagram. {str(e)}"


# result = diagram_creation("Thrust and Pressure", "Science")
# print(result)

