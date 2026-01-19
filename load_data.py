from pymongo import MongoClient
from langchain_community.vectorstores import MongoDBAtlasVectorSearch
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from voyage_embeddings import VoyageAIEmbeddings
import key_param
import re
import certifi

# Set the MongoDB URI, DB, Collection Names
# Configure SSL/TLS for MongoDB Atlas connection
client = MongoClient(
    key_param.MONGODB_URI,
    tlsCAFile=certifi.where(),
    serverSelectionTimeoutMS=5000
)
dbName = "rag"
collectionName = "chunked_data"
collection = client[dbName][collectionName]

import os

# Default PDF path in resources folder
default_pdf_path = os.path.join("resources", "mongodb.pdf")

# Check if default PDF exists, otherwise use fallback
if not os.path.exists(default_pdf_path):
    fallback_path = os.path.expanduser("~/Downloads/mongodb.pdf")
    pdf_path = fallback_path if os.path.exists(fallback_path) else default_pdf_path
else:
    pdf_path = default_pdf_path

print(f"Loading PDF from: {pdf_path}")
loader = PyPDFLoader(pdf_path)
pages = loader.load()
print(f"Loaded {len(pages)} pages from PDF")

cleaned_pages = []
for page in pages:
    if len(page.page_content.split(" ")) > 20:
        cleaned_pages.append(page)
print(f"Cleaned pages: {len(cleaned_pages)} pages with content")

text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=150)


def extract_metadata(doc):
    """Extract metadata from document using heuristics."""
    content = doc.page_content
    
    # Extract title from first sentence or first 50 characters
    first_sentence = content.split('.')[0] if '.' in content else content
    title = first_sentence[:50].strip() if len(first_sentence) > 50 else first_sentence.strip()
    
    # Extract keywords: common important words (excluding stop words)
    words = re.findall(r'\b[a-zA-Z]{4,}\b', content.lower())
    # Filter out common stop words and get top keywords
    stop_words = {'the', 'this', 'that', 'with', 'from', 'have', 'been', 'will', 'mongodb', 'document', 'collection'}
    keywords = [w for w in words if w not in stop_words][:10]
    
    # Detect code: check for common code patterns
    code_patterns = [
        r'```',  # Code blocks
        r'\{.*\}',  # Curly braces
        r'\(.*\)',  # Function calls
        r'def\s+\w+',  # Function definitions
        r'import\s+\w+',  # Imports
        r'\.\w+\(',  # Method calls
    ]
    has_code = any(re.search(pattern, content) for pattern in code_patterns)
    
    # Add metadata to document
    doc.metadata['title'] = title
    doc.metadata['keywords'] = list(set(keywords))  # Remove duplicates
    doc.metadata['hasCode'] = has_code
    
    return doc


# Extract metadata for each page
print("Extracting metadata...")
docs = [extract_metadata(page) for page in cleaned_pages]
print(f"Metadata extracted for {len(docs)} documents")

print("Chunking documents...")
split_docs = text_splitter.split_documents(docs)
print(f"Created {len(split_docs)} chunks")

print("Creating embeddings with Voyage AI...")
embeddings = VoyageAIEmbeddings(voyage_api_key=key_param.VOYAGE_API_KEY, model="voyage-3")

print("Storing documents in MongoDB Atlas...")
vectorStore = MongoDBAtlasVectorSearch.from_documents(
    split_docs, embeddings, collection=collection
)
print(f"Successfully loaded {len(split_docs)} chunks with embeddings into MongoDB Atlas!")

