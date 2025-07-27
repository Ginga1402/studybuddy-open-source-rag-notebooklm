import nltk
import gensim
from gensim import corpora
from gensim.models import LdaModel
from nltk.corpus import stopwords
from langchain.vectorstores import FAISS
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
import os
import torch
from configuration import embeddings, llm, VECTORSORE_PATH


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



# Download stopwords once (outside the function)
nltk.download('stopwords')
stop_words = set(stopwords.words('english'))

def preprocess(doc, stop_words):
    """
    Tokenize and clean a document by removing stopwords and non-alphabetic words.
    """
    return [word for word in gensim.utils.simple_preprocess(doc) if word not in stop_words]

def get_topic_lists_from_vectorstore(vector_store_name: str, num_topics: int, words_per_topic: int):
    """
    Extract topics from documents stored in a FAISS vector store using LDA.

    Parameters:
        faiss_path (str): Path to the persisted FAISS index.
        num_topics (int): Number of topics to extract.
        words_per_topic (int): Number of keywords per topic.

    Returns:
        List[List[str]]: A list of topic keyword lists.
    """
    try:
        faiss_path = os.path.join(VECTORSORE_PATH, vector_store_name)
        print(f"[INFO] Loading FAISS from: {faiss_path}")
        
        vectorstore = FAISS.load_local(
            faiss_path,
            embeddings=embeddings,
            index_name="index",
            allow_dangerous_deserialization=True
        )

        documents = [doc.page_content for doc in vectorstore.docstore._dict.values()]
        print(f"[INFO] Retrieved {len(documents)} documents from vectorstore.")

        processed_docs = [preprocess(doc, stop_words) for doc in documents]
        dictionary = corpora.Dictionary(processed_docs)
        corpus = [dictionary.doc2bow(doc) for doc in processed_docs]

        lda_model = LdaModel(corpus, num_topics=num_topics, id2word=dictionary, passes=15)
        topics = lda_model.print_topics(num_words=words_per_topic)

        topic_lists = []
        for topic in topics:
            words = topic[1].split("+")
            topic_words = [word.split("*")[1].replace('"', '').strip() for word in words]
            topic_lists.append(topic_words)

        return topic_lists

    except Exception as e:
        print(f"[ERROR] Failed to extract topics: {e}")
        raise

def topics_from_vectorstore(faiss_path: str):
    """
    Uses LDA + LLM to generate named topics and descriptions from a FAISS vector store.

    Parameters:
        llm: Language model to generate topic names and descriptions.
        faiss_path (str): Path to FAISS vector store directory.

    Returns:
        str: Formatted topic descriptions with subthemes.
    """
    try:
        faiss_path = os.path.join(VECTORSORE_PATH, faiss_path)
        print(f"[INFO] Loading FAISS from: {faiss_path}")
        # Load FAISS and get number of documents
        vectorstore = FAISS.load_local(
            faiss_path,
            embeddings=embeddings,
            index_name="index",
            allow_dangerous_deserialization=True
        )
        documents = [doc.page_content for doc in vectorstore.docstore._dict.values()]
        num_docs = len(documents)
        print(f"[INFO] Found {num_docs} documents in vectorstore.")

        num_topics = max(1, num_docs // 2)  # At least 1 topic
        words_per_topic = 30

        # Get topic words
        topic_word_lists = get_topic_lists_from_vectorstore(faiss_path, num_topics, words_per_topic)

        string_lda = ""
        for topic_words in topic_word_lists:
            string_lda += str(topic_words) + "\n"

        print(f"[DEBUG] LDA Word Lists:\n{string_lda}")

        # Prompt template
        prompt_template = PromptTemplate(
            input_variables=["num_topics", "string_lda"],
            template='''
            Describe the topic of each of the {num_topics} 
            double-quote delimited lists in a simple sentence and also write down 
            three possible different subthemes. The lists are the result of an 
            algorithm for topic discovery.
            Do not provide an introduction or a conclusion, only name the 
            topics. Do not mention the word "topic" when name the topics.
            Use the following template for the response.

            1: <<<(name of the topic)>>>
            <<<(Describe the topic)>>>
            - <<<(Phrase describing the first subtheme)>>>
            - <<<(Phrase describing the second subtheme)>>>
            - <<<(Phrase describing the third subtheme)>>>

            2: <<<(name of the topic)>>>
            <<<(Describe the topic)>>>
            - <<<(Phrase describing the first subtheme)>>>
            - <<<(Phrase describing the second subtheme)>>>
            - <<<(Phrase describing the third subtheme)>>>

            ...

            n: <<<(name of the topic)>>>
            <<<(Describe the topic)>>>
            - <<<(Phrase describing the first subtheme)>>>
            - <<<(Phrase describing the second subtheme)>>>
            - <<<(Phrase describing the third subtheme)>>>

            Lists: """{string_lda}""" 
        '''

        )

        # Run the prompt chain
        chain = prompt_template | llm | StrOutputParser()
        result = chain.invoke({"num_topics": num_topics, "string_lda": string_lda})

        return result

    except Exception as e:
        print(f"[ERROR] Failed to generate topic descriptions: {e}")
        raise





# topics_description = topics_from_vectorstore(faiss_path='Science')
# print(topics_description)