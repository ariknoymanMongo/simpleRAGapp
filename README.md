# MongoDB Atlas Vector Search RAG System

A RAG (Retrieval-Augmented Generation) system using MongoDB Atlas Vector Search, Voyage AI embeddings, and Google Gemini LLM.

## Features

- **Vector Search**: Semantic search using MongoDB Atlas Vector Search
- **Embeddings**: Voyage AI (voyage-3 model) for document embeddings
- **LLM**: Google Gemini (gemini-2.5-flash) for answer generation
- **PDF Processing**: Load and chunk PDF documents with metadata extraction

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure API Keys

Create a `.env` file in the project root with your API keys:

```bash
cp .env.example .env
```

Edit `.env` and add your actual keys:
- **MONGODB_URI**: Your MongoDB Atlas connection string
- **VOYAGE_API_KEY**: Get from [voyageai.com](https://www.voyageai.com/)
- **GEMINI_API_KEY**: Get from [Google AI Studio](https://makersuite.google.com/app/apikey)

**Note**: The `.env` file is already in `.gitignore` and won't be pushed to GitHub. Your keys are safe!

### 3. Create Vector Search Index

1. Go to MongoDB Atlas → Your Cluster → Search
2. Click "Create Search Index"
3. Select "JSON Editor"
4. Copy the contents of `atlas_vector_search_index.json`
5. Set index name to: `vector_index`
6. Create the index

## Usage

### Load PDF Data

The script will automatically look for `resources/mongodb.pdf`. If you want to use a different PDF, edit `load_data.py` and change the `pdf_path` variable.

```bash
python load_data.py
```

This will:
1. Load the PDF from `resources/mongodb.pdf`
2. Extract and clean pages
3. Chunk the content
4. Generate embeddings using Voyage AI
5. Store everything in MongoDB Atlas

### Test Retrieval

```bash
python test_retrieval.py
```

### Ask Questions (Interactive RAG)

```bash
python rag.py
```

Or use the simple question script:

```bash
python ask_question.py
```

## Project Structure

```
rag_atlas/
├── resources/              # PDF documents and other resources
│   └── mongodb.pdf        # Default PDF document
├── rag.py                 # Main RAG system with Gemini LLM
├── load_data.py           # Load and process PDF documents
├── test_retrieval.py      # Test vector search retrieval
├── ask_question.py        # Simple question-answering script
├── voyage_embeddings.py   # Voyage AI embeddings wrapper
├── key_param.py           # Loads API keys from .env file
├── atlas_vector_search_index.json  # Vector search index definition
├── .env                   # Your API keys (not in git)
├── .env.example           # Template for API keys
└── requirements.txt       # Python dependencies
```

## API Keys Used

- ✅ **Voyage AI** - For generating embeddings
- ✅ **Google Gemini** - For LLM in RAG pipeline
- ✅ **MongoDB Atlas** - For vector storage and search
- ❌ **OpenAI** - Not currently used (optional)

## License

MIT

