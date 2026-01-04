"""
Reranking service to improve retrieval quality.
Uses similarity scoring to rerank retrieved documents.
"""
from typing import List, Tuple
from langchain.schema import Document
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class RerankService:
    """Service for reranking retrieved documents."""
    
    def __init__(self):
        """Initialize rerank service."""
        logger.info("Rerank Service initialized")
    
    def calculate_similarity(self, query: str, document: str) -> float:
        """
        Calculate simple similarity score between query and document.
        Uses word overlap and length as basic features.
        
        Args:
            query: User query
            document: Document text
        
        Returns:
            Similarity score (0-1)
        """
        # Simple word-based similarity
        query_words = set(query.lower().split())
        doc_words = set(document.lower().split())
        
        if not query_words or not doc_words:
            return 0.0
        
        # Jaccard similarity
        intersection = len(query_words & doc_words)
        union = len(query_words | doc_words)
        jaccard = intersection / union if union > 0 else 0.0
        
        # Consider document length (prefer moderate length)
        doc_length = len(document)
        length_score = 1.0 if 100 <= doc_length <= 1000 else 0.5
        
        # Combined score
        similarity = 0.7 * jaccard + 0.3 * length_score
        
        return similarity
    
    def rerank_documents(
        self,
        query: str,
        documents: List[Document],
        top_k: int = 3
    ) -> List[Tuple[Document, float]]:
        """
        Rerank documents based on similarity to query.
        
        Args:
            query: User query
            documents: List of retrieved documents
            top_k: Number of top documents to return
        
        Returns:
            List of (document, score) tuples, sorted by score
        """
        if not documents:
            logger.warning("No documents to rerank")
            return []
        
        # Calculate similarity scores
        scored_docs = []
        for doc in documents:
            score = self.calculate_similarity(query, doc.page_content)
            scored_docs.append((doc, score))
        
        # Sort by score descending
        scored_docs.sort(key=lambda x: x[1], reverse=True)
        
        # Get top-k
        top_docs = scored_docs[:top_k]
        
        logger.info(
            f"Reranked {len(documents)} documents, "
            f"top {len(top_docs)} scores: {[f'{s:.3f}' for _, s in top_docs]}"
        )
        
        return top_docs
    
    def get_reranked_context(
        self,
        query: str,
        documents: List[Document],
        top_k: int = 3
    ) -> str:
        """
        Get concatenated context from reranked documents.
        
        Args:
            query: User query
            documents: List of retrieved documents
            top_k: Number of top documents to use
        
        Returns:
            Concatenated context string
        """
        reranked = self.rerank_documents(query, documents, top_k)
        
        context_parts = []
        for i, (doc, score) in enumerate(reranked, 1):
            context_parts.append(f"[文档 {i}]\n{doc.page_content}\n")
        
        return "\n".join(context_parts)
