"""
RAG (Retrieval Augmented Generation) service.
Handles document retrieval, reranking, and response generation.
"""
import os
from typing import List, Tuple, Optional
from pathlib import Path
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.schema import Document
from app.config import get_settings, REFUND_POLICY_PROMPT, GENERAL_PROMPT
from app.services.llm_service import LLMService
from app.services.rerank_service import RerankService
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class RAGService:
    """Service for RAG-based question answering."""
    
    def __init__(self):
        """Initialize RAG service with vector store and services."""
        self.settings = get_settings()
        
        # Initialize embeddings
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=self.settings.openai_api_key,
            model=self.settings.openai_embedding_model
        )
        
        # Initialize vector store
        self.vectordb_path = self.settings.vectordb_path
        self.collection_name = self.settings.collection_name
        self.vectorstore = None
        
        # Initialize services
        self.llm_service = LLMService()
        self.rerank_service = RerankService()
        
        # Load vector store if it exists
        self._load_vectorstore()
        
        logger.info("RAG Service initialized")
    
    def _load_vectorstore(self):
        """Load existing vector store if available."""
        vectordb_path = Path(self.vectordb_path)
        
        if vectordb_path.exists():
            try:
                self.vectorstore = Chroma(
                    persist_directory=self.vectordb_path,
                    embedding_function=self.embeddings,
                    collection_name=self.collection_name
                )
                count = self.vectorstore._collection.count()
                logger.info(f"Loaded vector store with {count} documents")
            except Exception as e:
                logger.warning(f"Could not load vector store: {str(e)}")
                self.vectorstore = None
        else:
            logger.warning(f"Vector store not found at {self.vectordb_path}")
    
    def initialize_vectorstore(self, documents: List[Document]):
        """
        Initialize vector store with documents.
        
        Args:
            documents: List of Document objects to store
        """
        if not documents:
            logger.error("No documents provided for initialization")
            return
        
        try:
            # Create vector store
            self.vectorstore = Chroma.from_documents(
                documents=documents,
                embedding=self.embeddings,
                persist_directory=self.vectordb_path,
                collection_name=self.collection_name
            )
            
            logger.info(f"Initialized vector store with {len(documents)} documents")
            
        except Exception as e:
            logger.error(f"Error initializing vector store: {str(e)}")
            raise
    
    def get_document_count(self) -> int:
        """Get the number of documents in the vector store."""
        if self.vectorstore is None:
            return 0
        try:
            return self.vectorstore._collection.count()
        except Exception as e:
            logger.warning(f"Error getting document count: {e}")
            return 0
    
    def retrieve_documents(
        self,
        query: str,
        top_k: Optional[int] = None
    ) -> List[Document]:
        """
        Retrieve relevant documents for a query.
        
        Args:
            query: User query
            top_k: Number of documents to retrieve (default from settings)
        
        Returns:
            List of relevant documents
        """
        if self.vectorstore is None:
            logger.error("Vector store not initialized")
            return []
        
        k = top_k or self.settings.retrieval_top_k
        
        try:
            documents = self.vectorstore.similarity_search(query, k=k)
            logger.info(f"Retrieved {len(documents)} documents for query")
            return documents
            
        except Exception as e:
            logger.error(f"Error retrieving documents: {str(e)}")
            return []
    
    def _select_prompt_template(self, question: str) -> str:
        """
        Select appropriate prompt template based on question.
        
        Args:
            question: User question
        
        Returns:
            Appropriate prompt template
        """
        # Keywords for refund policy
        refund_keywords = ["退费", "退款", "退课", "退钱", "退还", "取消课程"]
        
        question_lower = question.lower()
        if any(keyword in question_lower for keyword in refund_keywords):
            logger.info("Using refund policy prompt template")
            return REFUND_POLICY_PROMPT
        
        return GENERAL_PROMPT
    
    def answer_question(
        self,
        question: str,
        session_id: Optional[str] = None
    ) -> Tuple[str, List[str]]:
        """
        Answer a question using RAG pipeline.
        
        Args:
            question: User question
            session_id: Optional session ID for context
        
        Returns:
            Tuple of (answer, source_documents)
        """
        if self.vectorstore is None:
            return "抱歉，知识库尚未初始化。请先导入课程文档。", []
        
        try:
            # Step 1: Retrieve candidate documents (top-K)
            retrieved_docs = self.retrieve_documents(question)
            
            if not retrieved_docs:
                return "抱歉，我找不到相关的课程信息。请换个方式提问。", []
            
            # Step 2: Rerank documents to get top-N
            reranked_context = self.rerank_service.get_reranked_context(
                question,
                retrieved_docs,
                top_k=self.settings.rerank_top_k
            )
            
            # Step 3: Select appropriate prompt template
            prompt_template = self._select_prompt_template(question)
            
            # Step 4: Generate answer
            answer = self.llm_service.generate_with_context(
                question=question,
                context=reranked_context,
                prompt_template=prompt_template
            )
            
            # Extract source information
            sources = []
            for doc in retrieved_docs[:self.settings.rerank_top_k]:
                source = doc.metadata.get('source', 'unknown')
                if source not in sources:
                    sources.append(os.path.basename(source))
            
            return answer, sources
            
        except Exception as e:
            logger.error(f"Error answering question: {str(e)}")
            return "抱歉，处理您的问题时出现错误。请稍后再试。", []
