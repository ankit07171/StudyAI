"""
Embeddings Service
"""
from sentence_transformers import SentenceTransformer
from typing import List
from loguru import logger
import numpy as np

from app.core.config import settings


class EmbeddingService:
    """Generate embeddings for text chunks"""
    
    def __init__(self):
        """Initialize embedding model"""
        try:
            self.model = SentenceTransformer(settings.EMBEDDING_MODEL)
            self.dimension = settings.EMBEDDING_DIMENSION
            logger.info(f"Loaded embedding model: {settings.EMBEDDING_MODEL}")
        except Exception as e:
            logger.error(f"Error loading embedding model: {e}")
            raise
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text
        
        Args:
            text: Input text
            
        Returns:
            Embedding vector
        """
        try:
            embedding = self.model.encode(text, convert_to_numpy=True)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise
    
    def generate_embeddings_batch(self, texts: List[str], batch_size: int = 32) -> List[List[float]]:
        """
        Generate embeddings for multiple texts in batches
        
        Args:
            texts: List of input texts
            batch_size: Batch size for processing
            
        Returns:
            List of embedding vectors
        """
        try:
            embeddings = self.model.encode(
                texts,
                batch_size=batch_size,
                show_progress_bar=True,
                convert_to_numpy=True
            )
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"Error generating batch embeddings: {e}")
            raise
    
    def compute_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """
        Compute cosine similarity between two embeddings
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Similarity score (0 to 1)
        """
        try:
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)
            
            similarity = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
            return float(similarity)
        except Exception as e:
            logger.error(f"Error computing similarity: {e}")
            return 0.0
    
    def get_model_info(self) -> dict:
        """
        Get embedding model information
        
        Returns:
            Dictionary with model info
        """
        return {
            'model_name': settings.EMBEDDING_MODEL,
            'dimension': self.dimension,
            'max_seq_length': self.model.max_seq_length,
        }


# Global embedding service instance
embedding_service = EmbeddingService()
