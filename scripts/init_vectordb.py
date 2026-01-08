"""
Script to initialize the vector database with course documents.
Run this script before starting the application.
"""
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.utils.document_loader import DocumentLoader
from app.services.rag_service import RAGService
from app.utils.logger import setup_logger
from app.config import get_settings

logger = setup_logger(__name__)


def main():
    """Initialize vector database with documents."""
    logger.info("=" * 60)
    logger.info("Initializing Vector Database")
    logger.info("=" * 60)
    
    settings = get_settings()
    
    # Paths to document directories
    documents_dir = Path("./data/documents")
    faqs_dir = Path("./data/faqs")
    
    # Check if directories exist
    if not documents_dir.exists() and not faqs_dir.exists():
        logger.warning("No document directories found. Creating sample data...")
        create_sample_data()
    
    # Initialize document loader
    loader = DocumentLoader(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap
    )
    
    # Load documents
    all_documents = []
    
    if documents_dir.exists():
        logger.info(f"Loading documents from {documents_dir}...")
        docs = loader.load_and_split(str(documents_dir))
        all_documents.extend(docs)
        logger.info(f"Loaded {len(docs)} chunks from documents")
    
    if faqs_dir.exists():
        logger.info(f"Loading FAQs from {faqs_dir}...")
        faqs = loader.load_and_split(str(faqs_dir))
        all_documents.extend(faqs)
        logger.info(f"Loaded {len(faqs)} chunks from FAQs")
    
    if not all_documents:
        logger.error("No documents loaded! Please add documents to data/documents or data/faqs")
        return
    
    logger.info(f"Total documents loaded: {len(all_documents)}")
    
    # Initialize RAG service
    logger.info("Initializing RAG service...")
    rag_service = RAGService()
    
    # Initialize vector store
    logger.info("Creating vector embeddings (this may take a while)...")
    rag_service.initialize_vectorstore(all_documents)
    
    # Verify
    doc_count = rag_service.get_document_count()
    logger.info("=" * 60)
    logger.info(f"✅ Successfully initialized vector database with {doc_count} documents!")
    logger.info(f"Vector database stored at: {settings.vectordb_path}")
    logger.info("=" * 60)
    logger.info("You can now start the application with: python -m app.main")


def create_sample_data():
    """Create sample data if no documents exist."""
    documents_dir = Path("./data/documents")
    faqs_dir = Path("./data/faqs")
    
    documents_dir.mkdir(parents=True, exist_ok=True)
    faqs_dir.mkdir(parents=True, exist_ok=True)
    
    # Sample course document
    course_doc = """# Python编程课程介绍

## 课程概述
本课程是为初学者设计的Python编程入门课程，适合零基础学员。

## 课程内容
1. Python基础语法
2. 数据类型与变量
3. 控制流程（if/else/for/while）
4. 函数与模块
5. 面向对象编程
6. 文件操作
7. 异常处理
8. 常用库介绍

## 课程时长
- 总时长：60小时
- 学习周期：3个月
- 上课方式：在线直播 + 录播回放

## 课程价格
- 标准价格：3999元
- 早鸟优惠：2999元（前50名）
- 学生优惠：2499元（需提供学生证）

## 适合人群
- 编程零基础学员
- 想转行做程序员的职场人士
- 对Python感兴趣的学生

## 课程特色
- 实战项目驱动学习
- 一对一答疑辅导
- 终身回看权限
- 就业推荐服务
"""

    # Sample FAQ document
    faq_doc = """# 常见问题解答 (FAQ)

## 退费政策

### 退费条件
1. **7天无理由退费**：购买课程后7天内，如未观看超过20%的课程内容，可申请全额退费
2. **30天内部分退费**：购买后30天内，观看进度不超过50%，可退还50%费用
3. **特殊情况退费**：因个人特殊原因（如健康、家庭等）无法继续学习，可提供证明材料申请特殊退费

### 退费流程
1. 联系客服提交退费申请
2. 填写退费申请表
3. 提供必要的证明材料（如适用）
4. 审核通过后3-7个工作日内退款至原支付账户

### 不支持退费的情况
- 已完成课程学习的（观看进度超过80%）
- 已获得课程结业证书的
- 购买超过3个月的课程
- 参与过特殊促销活动（明确标注不可退费）

## 学习相关问题

### Q: 课程有效期多长？
A: 课程购买后3年内有效，可以随时回看。

### Q: 可以调整学习进度吗？
A: 可以，我们的课程支持自主学习，您可以根据自己的时间安排学习进度。

### Q: 是否提供课程资料？
A: 是的，所有课程配套PPT、代码示例和练习题都可以下载。

### Q: 遇到问题如何获得帮助？
A: 我们提供三种答疑方式：
1. 课程讨论区提问
2. 每周直播答疑
3. 一对一在线辅导（需预约）

### Q: 是否有学习证书？
A: 完成全部课程并通过考核后，可获得课程结业证书。

## 技术支持

### Q: 支持哪些设备学习？
A: 支持电脑（Windows/Mac）、平板、手机等多种设备，推荐使用电脑学习以获得最佳体验。

### Q: 视频无法播放怎么办？
A: 请检查网络连接，尝试切换清晰度或联系技术支持。

### Q: 如何下载课程视频？
A: 在课程页面点击下载按钮，选择清晰度后即可下载到本地。建议使用WiFi环境下载。
"""

    # Write sample files
    with open(documents_dir / "python_course.md", "w", encoding="utf-8") as f:
        f.write(course_doc)
    
    with open(faqs_dir / "faq.md", "w", encoding="utf-8") as f:
        f.write(faq_doc)
    
    logger.info("Created sample course and FAQ documents")


if __name__ == "__main__":
    main()
