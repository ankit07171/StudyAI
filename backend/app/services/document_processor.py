"""
Document Processing Service - Handles background PDF processing
"""
from typing import Dict
from loguru import logger
from datetime import datetime

from app.models.uploaded_file import UploadedFile
from app.services.rag.pdf_processor import PDFProcessor
from app.services.rag.chunking import text_chunker
from app.services.rag.embeddings import embedding_service
from app.services.rag.vector_store import vector_store


class DocumentProcessor:
    """Process uploaded documents through the RAG pipeline"""
    
    def __init__(self):
        self.pdf_processor = PDFProcessor()
    
    async def process_uploaded_file(self, file_id: str, user_id: str) -> Dict:
        """
        Process an uploaded file through the complete RAG pipeline
        
        Args:
            file_id: UploadedFile ID
            user_id: User ID
            
        Returns:
            Processing result
        """
        try:
            # Get the uploaded file record
            from beanie import PydanticObjectId
            uploaded_file = await UploadedFile.get(PydanticObjectId(file_id))
            
            if not uploaded_file:
                raise ValueError(f"Uploaded file {file_id} not found")
            
            logger.info(f"Starting processing for file: {uploaded_file.original_filename}")
            
            # Step 1: Extract text from PDF
            logger.info("Step 1: Extracting text from PDF")
            pdf_data = self.pdf_processor.process_pdf(uploaded_file.file_path)
            
            if not pdf_data.get('pages_text'):
                raise ValueError("No text could be extracted from PDF")
            
            # Step 2: Chunk the text
            logger.info("Step 2: Chunking text")
            chunks = text_chunker.chunk_pages(pdf_data['pages_text'])
            
            if not chunks:
                raise ValueError("No chunks could be created from text")
            
            logger.info(f"Created {len(chunks)} chunks")
            
            # Step 3: Generate embeddings and store in vector DB
            logger.info("Step 3: Generating embeddings and storing in vector DB")
            vector_ids = vector_store.add_documents(
                chunks=chunks,
                user_id=str(user_id),
                subject_id=str(uploaded_file.subject_id),
                file_id=str(uploaded_file.id),
                filename=uploaded_file.original_filename
            )
            
            # Step 4: Update uploaded file record
            logger.info("Step 4: Updating file record")
            uploaded_file.is_processed = True
            uploaded_file.processed_at = datetime.utcnow()
            uploaded_file.vector_ids = vector_ids
            uploaded_file.total_words = pdf_data.get('total_words', 0)
            await uploaded_file.save()
            
            logger.info(f"Successfully processed file: {uploaded_file.original_filename}")
            
            return {
                'success': True,
                'file_id': file_id,
                'chunks_created': len(chunks),
                'vectors_stored': len(vector_ids),
                'total_words': pdf_data.get('total_words', 0)
            }
            
        except Exception as e:
            logger.error(f"Error processing file {file_id}: {e}")
            
            # Update file with error
            try:
                uploaded_file = await UploadedFile.get(PydanticObjectId(file_id))
                if uploaded_file:
                    uploaded_file.processing_error = str(e)
                    await uploaded_file.save()
            except:
                pass
            
            return {
                'success': False,
                'file_id': file_id,
                'error': str(e)
            }


# Global document processor instance
document_processor = DocumentProcessor()
