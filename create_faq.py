# from langchain_community.chat_models import ChatOllama
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.output_parsers import StrOutputParser
import torch,os
from langchain.vectorstores import FAISS
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





def FAQ_creation(subject, vector_store_name, num_questions):
    """
    Generates student-friendly FAQs based on a given subject and vector store.

    Args:
        subject (str): The subject/topic to base the FAQs on.
        vector_store_name (str): Name of the FAISS vector store directory.
        num_questions (int): Number of FAQs to generate.

    Returns:
        str: Formatted FAQ content.
    """
    print(f"\n🔍 Starting FAQ generation for subject: '{subject}', Vector Store: '{vector_store_name}'")

    try:
        vector_store_path = os.path.join(VECTORSORE_PATH, vector_store_name)
        print(f"📂 Loading vector store from: {vector_store_path}")

        vector_store = FAISS.load_local(
            vector_store_path, 
            embeddings, 
            allow_dangerous_deserialization=True
        )

        retriever = vector_store.as_retriever(
            search_type="similarity", 
            search_kwargs={"k": 5}
        )
        print("✅ Vector store loaded and retriever initialized.")

    except Exception as e:
        print(f"❌ Error loading vector store: {e}")
        return f"Error loading vector store: {str(e)}"

    try:
        content = retriever.invoke(subject)
        full_text = "".join([doc.page_content for doc in content])
        print("📚 Retrieved and aggregated relevant content.")

        prompt = PromptTemplate(
            input_variables=["num_ques", "context"],
            template="""
                    You are an AI learning assistant that helps students study more effectively. Based on the content below, generate {num_ques} Frequently Asked Questions (FAQs) that serve as a structured learning guide for students.

                    ### Context:
                    {context}

                    Generate a list of {num_ques} guiding FAQs that cover the most important aspects of the material. These FAQs should help a student understand, review, and retain the content effectively.

                    ### Output Format:
                    1. **Q:** [Question 1]  
                    **A:** [Answer 1]

                    2. **Q:** [Question 2]  
                    **A:** [Answer 2]

                    ...

                    ONLY RETURN FAQ AND NOTHING ELSE
                    """
            )

        FAQ_creator = prompt | llm | StrOutputParser()
        FAQ = FAQ_creator.invoke({
            "num_ques": num_questions,
            "context": full_text
        })

        print("✅ FAQ successfully generated.\n")
        return FAQ

    except Exception as e:
        print(f"❌ Error during FAQ generation: {e}")
        return f"Error during FAQ generation: {str(e)}"





# faqs = FAQ_creation("Thrust and Pressure", "Science", 5)

# print(faqs)

