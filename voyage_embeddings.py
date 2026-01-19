"""Custom Voyage AI embeddings wrapper for LangChain."""
from typing import List
import voyageai
from langchain_core.embeddings import Embeddings


class VoyageAIEmbeddings(Embeddings):
    """Voyage AI embeddings wrapper for LangChain."""

    def __init__(self, voyage_api_key: str, model: str = "voyage-3", **kwargs):
        """Initialize Voyage AI embeddings.

        Args:
            voyage_api_key: Voyage AI API key
            model: Model name to use (default: "voyage-3")
            **kwargs: Additional arguments
        """
        self.client = voyageai.Client(api_key=voyage_api_key)
        self.model = model

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed search docs."""
        result = self.client.embed(texts, model=self.model, input_type="document")
        return result.embeddings

    def embed_query(self, text: str) -> List[float]:
        """Embed query text."""
        result = self.client.embed([text], model=self.model, input_type="query")
        return result.embeddings[0]

