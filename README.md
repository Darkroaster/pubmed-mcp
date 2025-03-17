# PubMed MCP服务

PubMed文献检索和分析多通道平台(MCP)服务，提供与PubMed数据库交互的功能，支持文献检索、数据分析和可视化。

## 功能特点

- **文献检索**：基本搜索和高级搜索功能，支持多种过滤条件
- **数据获取**：获取文章详细信息，包括标题、作者、摘要、关键词等
- **趋势分析**：分析特定主题的发表趋势
- **期刊分布**：分析文章在不同期刊上的分布情况
- **作者网络**：生成作者合作关系网络图
- **关键词分析**：分析文章关键词频率
- **文本聚类**：基于文章内容进行聚类分析
- **引用分析**：分析文章被引用情况
- **全文链接**：获取文章全文链接
- **词云生成**：基于文章内容生成词云图

## 使用方法

### 1. 基本搜索

```json
{
  "action": "search",
  "params": {
    "query": "cancer therapy",
    "max_results": 100,
    "sort": "relevance",
    "min_date": "2020/01/01",
    "max_date": "2023/12/31"
  }
}
```

### 2. 获取文章详情

```json
{
  "action": "fetch_details",
  "params": {
    "id_list": ["34567890", "34567891", "34567892"]
  }
}
```

### 3. 高级搜索

```json
{
  "action": "advanced_search",
  "params": {
    "search_params": {
      "author": "Smith J",
      "title": "cancer",
      "journal": "Nature",
      "year": "2022",
      "max_results": 50
    }
  }
}
```

### 4. 发表趋势分析

```json
{
  "action": "publication_trends",
  "params": {
    "query": "artificial intelligence",
    "start_year": 2010,
    "end_year": 2023
  }
}
```

### 5. 期刊分布分析

```json
{
  "action": "journal_distribution",
  "params": {
    "id_list": ["34567890", "34567891", "34567892"],
    "top_n": 10
  }
}
```

### 6. 作者网络分析

```json
{
  "action": "author_network",
  "params": {
    "id_list": ["34567890", "34567891", "34567892"],
    "min_collaborations": 2
  }
}
```

### 7. 关键词分析

```json
{
  "action": "keyword_analysis",
  "params": {
    "id_list": ["34567890", "34567891", "34567892"],
    "top_n": 20
  }
}
```

### 8. 文章聚类

```json
{
  "action": "cluster_articles",
  "params": {
    "id_list": ["34567890", "34567891", "34567892"],
    "n_clusters": 5,
    "text_column": "abstract"
  }
}
```

### 9. 引用分析

```json
{
  "action": "citation_analysis",
  "params": {
    "id_list": ["34567890", "34567891", "34567892"]
  }
}
```

### 10. 获取全文链接

```json
{
  "action": "download_full_text",
  "params": {
    "pmid": "34567890"
  }
}
```

### 11. 生成词云

```json
{
  "action": "generate_wordcloud",
  "params": {
    "text": "这里是要生成词云的文本内容...",
    "title": "文章关键词",
    "max_words": 100,
    "chinese": true
  }
}
```

## 安装依赖

```bash
pip install -r requirements.txt
```

## 注意事项

1. 使用前需要提供有效的电子邮件地址，这是NCBI API使用要求
2. 请遵循NCBI的使用政策，避免过于频繁的请求
3. 对于大量数据的处理，请考虑使用批处理方式
4. 建议申请NCBI API密钥以提高请求限制

## 示例代码

```python
from mcp_handler import MCPHandler

# 初始化处理器
handler = MCPHandler(email="your.email@example.com", api_key="your_api_key")

# 处理搜索请求
request = {
    "action": "search",
    "params": {
        "query": "cancer immunotherapy",
        "max_results": 50
    }
}

result = handler.handle_request(request["action"], request["params"])
print(result)
```

## 许可证

MIT