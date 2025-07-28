from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.output_parsers import StrOutputParser
import torch
from langchain.vectorstores import FAISS
from configuration import llm,embeddings,VECTORSORE_PATH
import os




def summary_creation(subject: str, vector_store_name: str) -> str:
    """
    Generate a student-friendly summary of a given subject using retrieved context from a vector store.

    Args:
        subject (str): The topic or question to summarize.
        vectorstore_path (str): Path to the saved FAISS vector store.

    Returns:
        str: Summary text
    """
    try:
        vector_store_path = os.path.join(VECTORSORE_PATH, vector_store_name)
        print(f"📂 Loading vector store from: {vector_store_path}")
        vector_store = FAISS.load_local(vector_store_path, embeddings, allow_dangerous_deserialization=True)
        print("✅ Vector store loaded successfully.")
    except Exception as e:
        print(f"❌ Error loading vector store: {e}")
        return f"Error: Unable to load vector store. {str(e)}"

    try:
        print(f"🔍 Retrieving documents for subject: '{subject}'")
        retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 5})
        content = retriever.invoke(subject)
        print(f"📄 Retrieved {len(content)} relevant documents.")

        full_text = "".join([doc.page_content for doc in content])
    except Exception as e:
        print(f"❌ Retrieval failed: {e}")
        return f"Error: Failed to retrieve documents. {str(e)}"

    try:
        print("🧠 Preparing summarization prompt...")
        prompt = PromptTemplate(
            template="""
            You are a helpful tutor summarizing complex topics for high school students.

            Using the context below, generate a clear and concise summary of **{subject}**.

            The summary should:
            1. Explain the main concepts and principles in simple language
            2. Highlight key experiments or demonstrations
            3. Mention important formulas or equations where relevant
            4. Address any important or commonly asked questions
            5. Be easy to follow, using bullet points or a numbered list for clarity

            Context:
            {context}

            ONLY RETURN SUMMARY BELOW:
            """,
            input_variables=["subject", "context"]
        )

        summary_creator = prompt | llm | StrOutputParser()
        print("✏️ Generating summary...")
        summary = summary_creator.invoke({"subject": subject, "context": full_text})
        print("✅ Summary generated successfully.")
        return summary

    except Exception as e:
        print(f"❌ Summarization failed: {e}")
        return f"Error: Failed to generate summary. {str(e)}"




# sample_summary = summary_creation("Thrust and Pressure", "Science")

# print(sample_summary)
