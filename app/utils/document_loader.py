"""
Document loader for processing various file formats.
Supports PDF, DOCX, TXT, and Markdown files.
"""
import os
from pathlib import Path
from typing import List, Dict
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    Docx2txtLoader
)
from langchain.schema import Document
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class DocumentLoader:
    """Load and process documents from various formats."""
    
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        """
        Initialize document loader.
        
        Args:
            chunk_size: Size of text chunks
            chunk_overlap: Overlap between chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", "。", "！", "？", ".", "!", "?", " ", ""]
        )
    
    def load_file(self, file_path: str) -> List[Document]:
        """
        Load a single file and return documents.
        
        Args:
            file_path: Path to the file
        
        Returns:
            List of Document objects
        """
        path = Path(file_path)
        
        if not path.exists():
            logger.error(f"File not found: {file_path}")
            return []
        
        try:
            # Select loader based on file extension
            ext = path.suffix.lower()
            
            if ext == '.pdf':
                loader = PyPDFLoader(str(path))
            elif ext == '.docx':
                loader = Docx2txtLoader(str(path))
            elif ext in ['.txt', '.md', '.markdown']:
                loader = TextLoader(str(path), encoding='utf-8')
            else:
                logger.warning(f"Unsupported file format: {ext}")
                return []
            
            documents = loader.load()
            logger.info(f"Loaded {len(documents)} documents from {path.name}")
            return documents
            
        except Exception as e:
            logger.error(f"Error loading file {file_path}: {str(e)}")
            return []
    
    def load_directory(self, directory_path: str) -> List[Document]:
        """
        Load all supported files from a directory.
        
        Args:
            directory_path: Path to the directory
        
        Returns:
            List of Document objects
        """
        directory = Path(directory_path)
        
        if not directory.exists():
            logger.error(f"Directory not found: {directory_path}")
            return []
        
        all_documents = []
        supported_extensions = ['.pdf', '.docx', '.txt', '.md', '.markdown']
        
        for file_path in directory.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in supported_extensions:
                documents = self.load_file(str(file_path))
                all_documents.extend(documents)
        
        logger.info(f"Loaded {len(all_documents)} total documents from {directory_path}")
        return all_documents
    
    def split_documents(self, documents: List[Document]) -> List[Document]:
        """
        Split documents into smaller chunks.
        
        Args:
            documents: List of Document objects
        
        Returns:
            List of split Document objects
        """
        if not documents:
            return []
        
        split_docs = self.text_splitter.split_documents(documents)
        logger.info(f"Split {len(documents)} documents into {len(split_docs)} chunks")
        return split_docs
    
    def load_and_split(self, path: str) -> List[Document]:
        """
        Load and split documents from a file or directory.
        
        Args:
            path: Path to file or directory
        
        Returns:
            List of split Document objects
        """
        path_obj = Path(path)
        
        if path_obj.is_file():
            documents = self.load_file(path)
        elif path_obj.is_dir():
            documents = self.load_directory(path)
        else:
            logger.error(f"Invalid path: {path}")
            return []
        
        return self.split_documents(documents)
