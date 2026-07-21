"""
Vector Store Service using Pinecone
"""
from typing import List, Dict, Optional
from pinecone import Pinecone, ServerlessSpec
from loguru import logger
import uuid

from app.core.config import settings
from app.services.rag.embeddings import embedding_service


class VectorStoreService:
    """Manage vector embeddings in Pinecone"""
    
    def __init__(self):
        """Initialize Pinecone connection"""
        try:
            # Initialize Pinecone (new API v5)
            self.pc = Pinecone(api_key=settings.PINECONE_API_KEY)
            
            # Get or create index
            self.index_name = settings.PINECONE_INDEX_NAME
            
            # Check if index exists
            existing_indexes = [index.name for index in self.pc.list_indexes()]
            
            if self.index_name not in existing_indexes:
                # Create index with serverless spec
                self.pc.create_index(
                    name=self.index_name,
                    dimension=settings.EMBEDDING_DIMENSION,
                    metric='cosine',
                    spec=ServerlessSpec(
                        cloud='aws',
                        region=settings.PINECONE_ENVIRONMENT
                    )
                )
                logger.info(f"Created Pinecone index: {self.index_name}")
            
            self.index = self.pc.Index(self.index_name)
            logger.info(f"Connected to Pinecone index: {self.index_name}")
            
        except Exception as e:
            logger.error(f"Error initializing Pinecone: {e}")
            raise
    
    def add_documents(
        self,
        chunks: List[Dict],
        user_id: int,
        subject_id: str,
        file_id: str,
        filename: str
    ) -> List[str]:
        """
        Add document chunks to vector store
        
        Args:
            chunks: List of text chunks with metadata
            user_id: User ID
            subject_id: Subject ID
            file_id: Uploaded file ID
            filename: Original filename
            
        Returns:
            List of vector IDs
        """
        try:
            vectors = []
            vector_ids = []
            
            for chunk in chunks:
                # Generate unique vector ID
                vector_id = str(uuid.uuid4())
                vector_ids.append(vector_id)
                
                # Generate embedding
                embedding = embedding_service.generate_embedding(chunk['text'])
                
                # Prepare metadata
                metadata = {
                    'user_id': user_id,
                    'subject_id': subject_id,
                    'file_id': file_id,
                    'filename': filename,
                    'page_number': chunk.get('page_number', 0),
                    'chunk_index': chunk.get('chunk_index', 0),
                    'chunk_type': chunk.get('chunk_type', 'text'),
                    'text': chunk['text'][:1000],  # Store truncated text in metadata
                }
                
                vectors.append((vector_id, embedding, metadata))
            
            # Upsert vectors in batches
            batch_size = 100
            for i in range(0, len(vectors), batch_size):
                batch = vectors[i:i + batch_size]
                self.index.upsert(vectors=batch)
            
            logger.info(f"Added {len(vectors)} vectors to Pinecone for file {filename}")
            return vector_ids
            
        except Exception as e:
            logger.error(f"Error adding documents to vector store: {e}")
            raise
    
    def query(
        self,
        query_text: str,
        subject_id: str,
        top_k: int = 5,
        filter_dict: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Query vector store for similar documents
        
        Args:
            query_text: Query text
            subject_id: Subject ID to filter by
            top_k: Number of results to return
            filter_dict: Additional filters
            
        Returns:
            List of matching documents with scores
        """
        try:
            # Generate query embedding
            query_embedding = embedding_service.generate_embedding(query_text)
            
            # Prepare filter
            filter_metadata = {'subject_id': subject_id}
            if filter_dict:
                filter_metadata.update(filter_dict)
            
            # Query index
            results = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True,
                filter=filter_metadata
            )
            
            # Format results
            documents = []
            for match in results['matches']:
                documents.append({
                    'id': match['id'],
                    'score': match['score'],
                    'text': match['metadata'].get('text', ''),
                    'page_number': match['metadata'].get('page_number', 0),
                    'filename': match['metadata'].get('filename', ''),
                    'file_id': str(match['metadata'].get('file_id', '')),
                    'chunk_type': match['metadata'].get('chunk_type', 'text'),
                })
            
            return documents
            
        except Exception as e:
            logger.error(f"Error querying vector store: {e}")
            return []
    
    def delete_by_file(self, file_id: str) -> bool:
        """
        Delete all vectors for a specific file
        
        Args:
            file_id: File ID
            
        Returns:
            Success status
        """
        try:
            self.index.delete(filter={'file_id': file_id})
            logger.info(f"Deleted vectors for file {file_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting vectors: {e}")
            return False
    
    def delete_by_subject(self, subject_id: int) -> bool:
        """
        Delete all vectors for a specific subject
        
        Args:
            subject_id: Subject ID
            
        Returns:
            Success status
        """
        try:
            self.index.delete(filter={'subject_id': subject_id})
            logger.info(f"Deleted vectors for subject {subject_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting vectors: {e}")
            return False
    
    def get_stats(self) -> Dict:
        """
        Get index statistics
        
        Returns:
            Dictionary with stats
        """
        try:
            stats = self.index.describe_index_stats()
            return {
                'total_vectors': stats.get('total_vector_count', 0) if stats else 0,
                'dimension': settings.EMBEDDING_DIMENSION,
                'namespaces': stats.get('namespaces', {}) if stats else {},
            }
        except Exception as e:
            logger.error(f"Error getting index stats: {e}")
            return {
                'total_vectors': 0,
                'dimension': settings.EMBEDDING_DIMENSION,
                'namespaces': {},
            }


# Global vector store instance
vector_store = VectorStoreService()
