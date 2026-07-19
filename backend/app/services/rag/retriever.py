"""
RAG Retriever Service
"""
from typing import List, Dict, Optional
from loguru import logger

from app.services.rag.vector_store import vector_store
from app.services.rag.embeddings import embedding_service


class RAGRetriever:
    """Retrieve relevant context for RAG queries"""
    
    def __init__(self):
        self.vector_store = vector_store
        self.embedding_service = embedding_service
    
    def retrieve(
        self,
        query: str,
        subject_id: int,
        top_k: int = 5,
        min_score: float = 0.5
    ) -> Dict:
        """
        Retrieve relevant documents for a query
        
        Args:
            query: User query
            subject_id: Subject ID
            top_k: Number of results
            min_score: Minimum similarity score
            
        Returns:
            Dictionary with context and metadata
        """
        try:
            # Query vector store
            results = self.vector_store.query(
                query_text=query,
                subject_id=subject_id,
                top_k=top_k
            )
            
            # Filter by minimum score
            filtered_results = [r for r in results if r['score'] >= min_score]
            
            # Prepare context
            context_chunks = []
            citations = []
            
            for result in filtered_results:
                context_chunks.append(result['text'])
                citations.append({
                    'file_name': result['filename'],
                    'page_number': result['page_number'],
                    'chunk_text': result['text'][:200] + '...',
                    'score': result['score']
                })
            
            # Combine context
            combined_context = '\n\n'.join(context_chunks)
            
            # Calculate confidence score (average of top results)
            confidence = sum(r['score'] for r in filtered_results) / len(filtered_results) if filtered_results else 0.0
            
            return {
                'context': combined_context,
                'citations': citations,
                'confidence_score': confidence,
                'num_results': len(filtered_results)
            }
            
        except Exception as e:
            logger.error(f"Error retrieving context: {e}")
            return {
                'context': '',
                'citations': [],
                'confidence_score': 0.0,
                'num_results': 0
            }
    
    def retrieve_with_reranking(
        self,
        query: str,
        subject_id: int,
        top_k: int = 10,
        final_k: int = 5
    ) -> Dict:
        """
        Retrieve with reranking for better results
        
        Args:
            query: User query
            subject_id: Subject ID
            top_k: Initial results to fetch
            final_k: Final results after reranking
            
        Returns:
            Dictionary with context and metadata
        """
        try:
            # Get more results initially
            initial_results = self.vector_store.query(
                query_text=query,
                subject_id=subject_id,
                top_k=top_k
            )
            
            if not initial_results:
                return self.retrieve(query, subject_id, final_k)
            
            # Rerank based on additional criteria
            # (In a production system, you could use a cross-encoder here)
            reranked = sorted(initial_results, key=lambda x: x['score'], reverse=True)
            
            # Take top results after reranking
            final_results = reranked[:final_k]
            
            # Prepare response
            context_chunks = [r['text'] for r in final_results]
            citations = [
                {
                    'file_name': r['filename'],
                    'page_number': r['page_number'],
                    'chunk_text': r['text'][:200] + '...',
                    'score': r['score']
                }
                for r in final_results
            ]
            
            confidence = sum(r['score'] for r in final_results) / len(final_results)
            
            return {
                'context': '\n\n'.join(context_chunks),
                'citations': citations,
                'confidence_score': confidence,
                'num_results': len(final_results)
            }
            
        except Exception as e:
            logger.error(f"Error in reranking retrieval: {e}")
            return self.retrieve(query, subject_id, final_k)


# Global retriever instance
rag_retriever = RAGRetriever()
