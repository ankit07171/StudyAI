"""
PDF Processing Service
"""
import pymupdf
import pdfplumber
from typing import List, Dict, Optional
from pathlib import Path
from loguru import logger


class PDFProcessor:
    """Process PDF files and extract text content"""
    
    def __init__(self):
        self.supported_formats = ['.pdf']
    
    def extract_text_pymupdf(self, pdf_path: str) -> Dict[int, str]:
        """
        Extract text from PDF using PyMuPDF
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Dictionary with page numbers as keys and text as values
        """
        try:
            pages_text = {}
            doc = pymupdf.open(pdf_path)
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text()
                pages_text[page_num + 1] = text
            
            doc.close()
            return pages_text
            
        except Exception as e:
            logger.error(f"Error extracting text with PyMuPDF: {e}")
            return {}
    
    def extract_text_pdfplumber(self, pdf_path: str) -> Dict[int, str]:
        """
        Extract text from PDF using PDFPlumber (better for tables)
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Dictionary with page numbers as keys and text as values
        """
        try:
            pages_text = {}
            
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages, start=1):
                    text = page.extract_text()
                    if text:
                        pages_text[page_num] = text
            
            return pages_text
            
        except Exception as e:
            logger.error(f"Error extracting text with PDFPlumber: {e}")
            return {}
    
    def extract_tables(self, pdf_path: str) -> Dict[int, List[List[str]]]:
        """
        Extract tables from PDF
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Dictionary with page numbers as keys and tables as values
        """
        try:
            pages_tables = {}
            
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages, start=1):
                    tables = page.extract_tables()
                    if tables:
                        pages_tables[page_num] = tables
            
            return pages_tables
            
        except Exception as e:
            logger.error(f"Error extracting tables: {e}")
            return {}
    
    def get_pdf_metadata(self, pdf_path: str) -> Dict[str, any]:
        """
        Get PDF metadata
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Dictionary with metadata
        """
        try:
            doc = pymupdf.open(pdf_path)
            metadata = {
                'page_count': len(doc),
                'title': doc.metadata.get('title', ''),
                'author': doc.metadata.get('author', ''),
                'subject': doc.metadata.get('subject', ''),
                'creator': doc.metadata.get('creator', ''),
            }
            doc.close()
            return metadata
            
        except Exception as e:
            logger.error(f"Error getting PDF metadata: {e}")
            return {}
    
    def process_pdf(self, pdf_path: str) -> Dict:
        """
        Complete PDF processing
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Dictionary with all extracted data
        """
        try:
            # Extract text using both methods and combine
            text_pymupdf = self.extract_text_pymupdf(pdf_path)
            text_pdfplumber = self.extract_text_pdfplumber(pdf_path)
            
            # Use PDFPlumber as primary, PyMuPDF as fallback
            pages_text = {}
            all_pages = set(list(text_pymupdf.keys()) + list(text_pdfplumber.keys()))
            
            for page_num in all_pages:
                text = text_pdfplumber.get(page_num, '') or text_pymupdf.get(page_num, '')
                if text.strip():
                    pages_text[page_num] = text
            
            # Extract tables
            tables = self.extract_tables(pdf_path)
            
            # Get metadata
            metadata = self.get_pdf_metadata(pdf_path)
            
            # Calculate statistics
            total_words = sum(len(text.split()) for text in pages_text.values())
            
            return {
                'pages_text': pages_text,
                'tables': tables,
                'metadata': metadata,
                'total_pages': len(pages_text),
                'total_words': total_words,
            }
            
        except Exception as e:
            logger.error(f"Error processing PDF: {e}")
            raise
    
    def clean_text(self, text: str) -> str:
        """
        Clean extracted text
        
        Args:
            text: Raw text
            
        Returns:
            Cleaned text
        """
        # Remove excessive whitespace
        text = ' '.join(text.split())
        
        # Remove special characters but keep punctuation
        # Add more cleaning rules as needed
        
        return text.strip()
