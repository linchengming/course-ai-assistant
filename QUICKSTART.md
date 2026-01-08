# 快速开始指南

## 5分钟快速体验

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 配置API Key
```bash
cp .env.example .env
# 编辑 .env 文件，填入您的 OpenAI API Key
```

### 3. 初始化数据库（自动创建示例数据）
```bash
python scripts/init_vectordb.py
```

输出示例：
```
====================================================
Initializing Vector Database
====================================================
Created sample course and FAQ documents
Loading documents from ./data/documents...
Loaded 23 chunks from documents
Loading FAQs from ./data/faqs...
Loaded 41 chunks from FAQs
Total documents loaded: 64
Initializing RAG service...
Creating vector embeddings (this may take a while)...
====================================================
✅ Successfully initialized vector database with 64 documents!
Vector database stored at: ./vectordb
====================================================
```

### 4. 启动服务
```bash
python -m app.main
```

输出示例：
```
2026-01-04 17:30:00 - app.main - INFO - ========================================
2026-01-04 17:30:00 - app.main - INFO - Course AI Assistant Starting...
2026-01-04 17:30:00 - app.main - INFO - Host: 0.0.0.0:8000
2026-01-04 17:30:00 - app.main - INFO - Vector DB: ./vectordb
2026-01-04 17:30:00 - app.main - INFO - ========================================
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 5. 打开浏览器
访问：http://localhost:8000

## 示例问题

尝试以下问题来体验AI助手：

1. **课程内容相关**
   - "Python课程包含哪些内容？"
   - "这个课程需要多长时间？"
   - "课程价格是多少？"

2. **退费政策相关**（使用优化的专门Prompt）
   - "课程可以退费吗？"
   - "退费流程是什么？"
   - "什么情况下不能退费？"

3. **学习方式相关**
   - "课程是怎么上课的？"
   - "可以下载视频吗？"
   - "遇到问题怎么办？"

## 查看统计

点击界面上的"查看统计"按钮，可以看到：
- 总查询数
- 平均响应时间
- 准确率
- 知识库文档数

## 日志分析

```bash
python scripts/analyze_logs.py
```

会生成详细的分析报告和CSV文件。

## 添加自己的文档

1. 将文档放入 `data/documents/` 或 `data/faqs/`
2. 支持格式：PDF、DOCX、TXT、Markdown
3. 重新初始化：`python scripts/init_vectordb.py`

## API使用示例

### cURL
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "课程的退费政策是什么？"}'
```

### Python
```python
import requests

response = requests.post(
    "http://localhost:8000/api/chat",
    json={"message": "Python课程包含什么内容？"}
)

data = response.json()
print(f"答案: {data['answer']}")
print(f"来源: {data['sources']}")
```

### JavaScript
```javascript
fetch('http://localhost:8000/api/chat', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({message: '课程价格是多少？'})
})
.then(res => res.json())
.then(data => console.log(data.answer));
```

## 常见问题

### Q: 向量数据库在哪里？
A: 在 `./vectordb` 目录，由Chroma自动管理

### Q: 如何重新初始化数据库？
A: 删除 `vectordb` 目录，重新运行 `python scripts/init_vectordb.py`

### Q: 如何修改Prompt？
A: 编辑 `app/config.py` 中的 `REFUND_POLICY_PROMPT` 或 `GENERAL_PROMPT`

### Q: 如何调整检索数量？
A: 在 `.env` 中设置 `RETRIEVAL_TOP_K` 和 `RERANK_TOP_K`

## 下一步

- 添加更多课程文档到 `data/documents/`
- 自定义Prompt模板以适应特定问题
- 分析日志以持续优化
- 部署到生产环境（使用Docker）

祝您使用愉快！🎉
