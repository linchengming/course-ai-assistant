"""
Unit tests for RAG service functionality.
"""
import pytest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.utils.document_loader import DocumentLoader
from app.services.rerank_service import RerankService
from langchain.schema import Document


class TestDocumentLoader:
    """Test document loader functionality."""
    
    def test_initialization(self):
        """Test document loader initialization."""
        loader = DocumentLoader(chunk_size=500, chunk_overlap=50)
        assert loader.chunk_size == 500
        assert loader.chunk_overlap == 50
    
    def test_text_splitter(self):
        """Test text splitting."""
        loader = DocumentLoader(chunk_size=100, chunk_overlap=20)
        
        # Create a test document
        long_text = "这是一段很长的文本。" * 50
        documents = [Document(page_content=long_text, metadata={"source": "test"})]
        
        # Split documents
        split_docs = loader.split_documents(documents)
        
        assert len(split_docs) > 1
        assert all(len(doc.page_content) <= 150 for doc in split_docs)  # Allow some overflow


class TestRerankService:
    """Test reranking service functionality."""
    
    def test_initialization(self):
        """Test rerank service initialization."""
        service = RerankService()
        assert service is not None
    
    def test_calculate_similarity(self):
        """Test similarity calculation."""
        service = RerankService()
        
        query = "Python课程价格"
        doc1 = "Python编程课程的价格是3999元，早鸟优惠2999元。"
        doc2 = "Java课程内容包括基础语法和面向对象编程。"
        doc3 = "这是一段完全不相关的内容。"
        
        score1 = service.calculate_similarity(query, doc1)
        score2 = service.calculate_similarity(query, doc2)
        score3 = service.calculate_similarity(query, doc3)
        
        # Doc1 should have highest score as it's most relevant
        assert score1 > score2
        assert score1 > score3
    
    def test_rerank_documents(self):
        """Test document reranking."""
        service = RerankService()
        
        query = "退费政策"
        documents = [
            Document(page_content="课程退费政策：7天内可全额退费。", metadata={"source": "faq1"}),
            Document(page_content="课程内容包括Python基础和进阶。", metadata={"source": "course1"}),
            Document(page_content="关于退费的详细说明和流程。", metadata={"source": "faq2"}),
        ]
        
        reranked = service.rerank_documents(query, documents, top_k=2)
        
        assert len(reranked) == 2
        assert all(isinstance(doc, Document) for doc, score in reranked)
        assert all(isinstance(score, float) for doc, score in reranked)
        
        # Check that scores are in descending order
        scores = [score for _, score in reranked]
        assert scores[0] >= scores[1]
    
    def test_get_reranked_context(self):
        """Test getting reranked context."""
        service = RerankService()
        
        query = "课程价格"
        documents = [
            Document(page_content="价格3999元", metadata={"source": "doc1"}),
            Document(page_content="包含基础和进阶", metadata={"source": "doc2"}),
            Document(page_content="优惠价格2999元", metadata={"source": "doc3"}),
        ]
        
        context = service.get_reranked_context(query, documents, top_k=2)
        
        assert isinstance(context, str)
        assert len(context) > 0
        assert "[文档" in context


class TestPromptSelection:
    """Test prompt template selection logic."""
    
    def test_refund_keywords(self):
        """Test that refund keywords are properly detected."""
        refund_keywords = ["退费", "退款", "退课", "退钱", "退还", "取消课程"]
        
        test_questions = [
            "课程可以退费吗？",
            "退款政策是什么？",
            "我想退课",
            "能退钱吗？",
            "如何退还学费？",
            "取消课程的流程"
        ]
        
        for question in test_questions:
            has_refund_keyword = any(kw in question for kw in refund_keywords)
            assert has_refund_keyword, f"Failed to detect refund keyword in: {question}"


@pytest.mark.asyncio
async def test_api_health_check():
    """Test health check endpoint."""
    # This would require running the FastAPI app
    # Simplified test - just ensure imports work
    from app.api.chat import health_check
    assert health_check is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
