"""
Text Chunking Service
"""
from typing import List, Dict
from langchain.text_splitter import RecursiveCharacterTextSplitter
from loguru import logger

from app.core.config import settings


class TextChunker:
    """Split text into semantic chunks"""
    
    def __init__(self):
        """Initialize text splitter"""
        self.chunk_size = settings.CHUNK_SIZE
        self.chunk_overlap = settings.CHUNK_OVERLAP
        
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
    
    def chunk_text(self, text: str) -> List[str]:
        """
        Split text into chunks
        
        Args:
            text: Input text
            
        Returns:
            List of text chunks
        """
        try:
            chunks = self.splitter.split_text(text)
            return chunks
        except Exception as e:
            logger.error(f"Error chunking text: {e}")
            return [text]
    
    def chunk_pages(self, pages_text: Dict[int, str]) -> List[Dict]:
        """
        Chunk text from multiple pages with metadata
        
        Args:
            pages_text: Dictionary with page numbers and text
            
        Returns:
            List of chunks with metadata
        """
        try:
            chunks_with_metadata = []
            
            for page_num, text in pages_text.items():
                if not text.strip():
                    continue
                
                # Split text into chunks
                chunks = self.chunk_text(text)
                
                # Add metadata to each chunk
                for idx, chunk in enumerate(chunks):
                    if chunk.strip():
                        chunks_with_metadata.append({
                            'text': chunk,
                            'page_number': page_num,
                            'chunk_index': idx,
                            'chunk_type': 'text'
                        })
            
            return chunks_with_metadata
            
        except Exception as e:
            logger.error(f"Error chunking pages: {e}")
            return []
    
    def chunk_with_context(self, pages_text: Dict[int, str], context_window: int = 1) -> List[Dict]:
        """
        Chunk text with surrounding context for better retrieval
        
        Args:
            pages_text: Dictionary with page numbers and text
            context_window: Number of surrounding chunks to include
            
        Returns:
            List of chunks with context
        """
        try:
            # First get all basic chunks
            basic_chunks = self.chunk_pages(pages_text)
            
            # Add context from surrounding chunks
            chunks_with_context = []
            
            for i, chunk in enumerate(basic_chunks):
                # Get previous chunks
                context_before = []
                for j in range(max(0, i - context_window), i):
                    context_before.append(basic_chunks[j]['text'])
                
                # Get next chunks
                context_after = []
                for j in range(i + 1, min(len(basic_chunks), i + context_window + 1)):
                    context_after.append(basic_chunks[j]['text'])
                
                chunk_with_ctx = chunk.copy()
                chunk_with_ctx['context_before'] = ' '.join(context_before)
                chunk_with_ctx['context_after'] = ' '.join(context_after)
                
                chunks_with_context.append(chunk_with_ctx)
            
            return chunks_with_context
            
        except Exception as e:
            logger.error(f"Error adding context to chunks: {e}")
            return self.chunk_pages(pages_text)
    
    def extract_formulas(self, text: str) -> List[str]:
        """
        Extract mathematical formulas from text
        
        Args:
            text: Input text
            
        Returns:
            List of formulas
        """
        # Simple formula extraction (can be enhanced with regex patterns)
        formulas = []
        
        # Look for equations with = sign
        lines = text.split('\n')
        for line in lines:
            if '=' in line and any(char.isdigit() for char in line):
                formulas.append(line.strip())
        
        return formulas
    
    def extract_definitions(self, text: str) -> List[Dict[str, str]]:
        """
        Extract definitions from text
        
        Args:
            text: Input text
            
        Returns:
            List of definitions with terms
        """
        definitions = []
        
        # Look for patterns like "X is defined as", "X refers to", etc.
        definition_patterns = [
            " is defined as ",
            " refers to ",
            " means ",
            " is the ",
        ]
        
        sentences = text.split('. ')
        for sentence in sentences:
            for pattern in definition_patterns:
                if pattern in sentence.lower():
                    parts = sentence.split(pattern, 1)
                    if len(parts) == 2:
                        definitions.append({
                            'term': parts[0].strip(),
                            'definition': parts[1].strip()
                        })
                    break
        
        return definitions


# Global chunker instance
text_chunker = TextChunker()
