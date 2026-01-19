from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from voyage_embeddings import VoyageAIEmbeddings
from pymongo import MongoClient
import key_param
import certifi

dbName = "rag"
collectionName = "chunked_data"
index = "vector_index"

# Create MongoDB client with SSL configuration
client = MongoClient(
    key_param.MONGODB_URI,
    tlsCAFile=certifi.where(),
    serverSelectionTimeoutMS=5000
)

# Create vector store using the client
vectorStore = MongoDBAtlasVectorSearch(
    collection=client[dbName][collectionName],
    embedding=VoyageAIEmbeddings(voyage_api_key=key_param.VOYAGE_API_KEY, model="voyage-3"),
    index_name=index,
)


def query_data(query):
    retriever = vectorStore.as_retriever(
        search_type="similarity",
        search_kwargs={
            "k": 3,
            # Your index filters on "keywords" at root level (matches document structure)
            # Uncomment to filter by keywords if needed:
            # "pre_filter": {"keywords": {"$exists": True}},
            "score_threshold": 0.01,
        },
    )

    template = """
    Use the following pieces of context to answer the question at the end.
    If you don't know the answer, just say that you don't know, don't try to make up an answer.
    Do not answer the question if there is no given context.
    Do not answer the question if it is not related to the context.
    Do not give recommendations to anything other than MongoDB.
    Context:
    {context}
    Question: {question}
    """

    custom_rag_prompt = PromptTemplate.from_template(template)

    retrieve = {
        "context": retriever | (lambda docs: "\n\n".join([d.page_content for d in docs])),
        "question": RunnablePassthrough()
    }

    llm = ChatGoogleGenerativeAI(
        google_api_key=key_param.GEMINI_API_KEY,
        model="gemini-2.5-flash",
        temperature=0
    )

    response_parser = StrOutputParser()

    rag_chain = (
        retrieve
        | custom_rag_prompt
        | llm
        | response_parser
    )

    answer = rag_chain.invoke(query)

    return answer


if __name__ == "__main__":
    print("=" * 60)
    print("RAG System - Ask questions about MongoDB")
    print("=" * 60)
    print("Type 'quit' or 'exit' to stop\n")
    
    while True:
        try:
            question = input("Ask a question: ").strip()
            
            if question.lower() in ['quit', 'exit', 'q']:
                print("\nGoodbye!")
                break
            
            if not question:
                print("Please enter a question.\n")
                continue
            
            print("\nSearching and generating answer...")
            answer = query_data(question)
            print(f"\nAnswer: {answer}\n")
            print("-" * 60 + "\n")
            
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"\nError: {e}\n")
            print("-" * 60 + "\n")

