from pinecone import Pinecone, ServerlessSpec
import openai
from typing import List, Dict, Optional
from app.core.config import settings
import logging
import hashlib

logger = logging.getLogger(__name__)

class VectorService:
    def __init__(self):
        self.openai_api_key = settings.OPENAI_API_KEY
        self.pinecone_api_key = settings.PINECONE_API_KEY

        if self.openai_api_key:
            openai.api_key = self.openai_api_key

        if self.pinecone_api_key:
            self.pc = Pinecone(api_key=self.pinecone_api_key)
            self._initialize_index()

    def _initialize_index(self):
        """Initialize Pinecone index if it doesn't exist"""
        try:
            indexes = self.pc.list_indexes()
            if settings.PINECONE_INDEX not in [index.name for index in indexes]:
                self.pc.create_index(
                    name=settings.PINECONE_INDEX,
                    dimension=1536,  # OpenAI embedding dimension
                    metric='cosine',
                    spec=ServerlessSpec(
                        cloud='aws',
                        region='us-west-2'
                    )
                )
                logger.info(f"Created Pinecone index: {settings.PINECONE_INDEX}")

            self.index = self.pc.Index(settings.PINECONE_INDEX)
        except Exception as e:
            logger.error(f"Error initializing Pinecone index: {e}")
            self.index = None

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings using OpenAI's text-embedding-3-small model
        Best practice: Use text-embedding-3-small for cost-effectiveness
        """
        if not self.openai_api_key:
            logger.warning("OpenAI API key not configured")
            return []

        try:
            client = openai.OpenAI(api_key=self.openai_api_key)
            response = client.embeddings.create(
                input=texts,
                model="text-embedding-3-small"
            )
            return [embedding.embedding for embedding in response.data]
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            return []

    def store_vectors(self, website_url: str, page_data: List[Dict]) -> List[str]:
        """
        Store keyword vectors in Pinecone with metadata
        Returns list of vector IDs
        """
        if not self.index:
            logger.warning("Pinecone index not available")
            return []

        vector_ids = []
        vectors_to_upsert = []

        for page in page_data:
            if not page.get("keywords"):
                continue

            # Combine keywords into a single text for embedding
            keywords_text = " ".join(page["keywords"])

            # Generate unique ID for this page
            vector_id = hashlib.md5(
                f"{website_url}_{page['url']}".encode()
            ).hexdigest()

            # Generate embedding
            embeddings = self.generate_embeddings([keywords_text])
            if not embeddings:
                continue

            # Prepare vector with metadata
            vector_data = {
                "id": vector_id,
                "values": embeddings[0],
                "metadata": {
                    "website_url": website_url,
                    "page_url": page["url"],
                    "keywords": keywords_text,
                    "position": page.get("position"),
                    "search_volume": page.get("search_volume")
                }
            }

            vectors_to_upsert.append(vector_data)
            vector_ids.append(vector_id)

        # Batch upsert to Pinecone
        if vectors_to_upsert:
            try:
                self.index.upsert(vectors=vectors_to_upsert)
                logger.info(f"Stored {len(vectors_to_upsert)} vectors for {website_url}")
            except Exception as e:
                logger.error(f"Error storing vectors: {e}")
                return []

        return vector_ids

    def search_similar(self, query: str, filters: Dict = None, top_k: int = 10) -> List[Dict]:
        """
        Search for similar content using vector similarity
        """
        if not self.index:
            logger.warning("Pinecone index not available")
            return []

        # Generate embedding for query
        embeddings = self.generate_embeddings([query])
        if not embeddings:
            return []

        try:
            # Search in Pinecone
            results = self.index.query(
                vector=embeddings[0],
                top_k=top_k,
                include_metadata=True,
                filter=filters
            )

            return [
                {
                    "score": match.score,
                    "website_url": match.metadata.get("website_url"),
                    "page_url": match.metadata.get("page_url"),
                    "keywords": match.metadata.get("keywords"),
                    "position": match.metadata.get("position")
                }
                for match in results.matches
            ]
        except Exception as e:
            logger.error(f"Error searching vectors: {e}")
            return []

vector_service = VectorService()