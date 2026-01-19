from pymongo import MongoClient
from voyage_embeddings import VoyageAIEmbeddings
from langchain_mongodb import MongoDBAtlasVectorSearch
import key_param
import certifi

dbName = "rag"
collectionName = "chunked_data"  # Updated to match new collection
index = "vector_index"

# Create MongoDB client with SSL configuration
client = MongoClient(
    key_param.MONGODB_URI,
    tlsCAFile=certifi.where(),
    serverSelectionTimeoutMS=5000
)

# Create vector store
vectorStore = MongoDBAtlasVectorSearch(
    collection=client[dbName][collectionName],
    embedding=VoyageAIEmbeddings(voyage_api_key=key_param.VOYAGE_API_KEY, model="voyage-3"),
    index_name=index,
)

question = "how many nodes i need for sharded cluster?"
print(f"Question: {question}\n")

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

print("Retrieving relevant documents...")
results = retriever.invoke(question)

print(f"\nFound {len(results)} relevant documents:\n")
print("=" * 60)
for i, doc in enumerate(results, 1):
    print(f"\nDocument {i}:")
    print(f"Content: {doc.page_content[:300]}...")
    print(f"Metadata: {doc.metadata}")

