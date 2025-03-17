"""
MCP处理器模块 - 处理MCP服务请求
"""

import json
import base64
import io
import matplotlib.pyplot as plt
from pubmed_api import PubMedAPI
from analysis import PubMedAnalyzer

class MCPHandler:
    """MCP服务处理器类"""
    
    def __init__(self, email, api_key=None):
        """
        初始化MCP处理器
        
        参数:
            email (str): 用户电子邮件地址（NCBI要求提供）
            api_key (str, 可选): NCBI API密钥
        """
        self.pubmed_api = PubMedAPI(email=email, api_key=api_key)
        self.analyzer = PubMedAnalyzer()
    
    def handle_request(self, action, params):
        """
        处理MCP请求
        
        参数:
            action (str): 请求的操作
            params (dict): 操作参数
            
        返回:
            dict: 操作结果
        """
        try:
            # 根据操作类型分发请求
            if action == "search":
                return self._handle_search(params)
            elif action == "fetch_details":
                return self._handle_fetch_details(params)
            elif action == "advanced_search":
                return self._handle_advanced_search(params)
            elif action == "publication_trends":
                return self._handle_publication_trends(params)
            elif action == "journal_distribution":
                return self._handle_journal_distribution(params)
            elif action == "author_network":
                return self._handle_author_network(params)
            elif action == "keyword_analysis":
                return self._handle_keyword_analysis(params)
            elif action == "cluster_articles":
                return self._handle_cluster_articles(params)
            elif action == "citation_analysis":
                return self._handle_citation_analysis(params)
            elif action == "download_full_text":
                return self._handle_download_full_text(params)
            elif action == "generate_wordcloud":
                return self._handle_generate_wordcloud(params)
            else:
                return {"status": "error", "message": f"未知操作: {action}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def _handle_search(self, params):
        """处理基本搜索请求"""
        query = params.get("query", "")
        max_results = int(params.get("max_results", 100))
        sort = params.get("sort", "relevance")
        min_date = params.get("min_date")
        max_date = params.get("max_date")
        
        if not query:
            return {"status": "error", "message": "搜索查询不能为空"}
        
        # 执行搜索
        id_list = self.pubmed_api.search(
            query=query,
            max_results=max_results,
            sort=sort,
            min_date=min_date,
            max_date=max_date
        )
        
        return {
            "status": "success",
            "data": {
                "id_list": id_list,
                "count": len(id_list)
            }
        }
    
    def _handle_fetch_details(self, params):
        """处理获取文章详情请求"""
        id_list = params.get("id_list", [])
        
        if not id_list:
            return {"status": "error", "message": "ID列表不能为空"}
        
        # 获取文章详情
        articles = self.pubmed_api.fetch_details(id_list)
        
        return {
            "status": "success",
            "data": {
                "articles": articles,
                "count": len(articles)
            }
        }
    
    def _handle_advanced_search(self, params):
        """处理高级搜索请求"""
        search_params = params.get("search_params", {})
        
        if not search_params:
            return {"status": "error", "message": "搜索参数不能为空"}
        
        # 执行高级搜索
        id_list = self.pubmed_api.advanced_search(search_params)
        
        return {
            "status": "success",
            "data": {
                "id_list": id_list,
                "count": len(id_list)
            }
        }
    
    def _handle_publication_trends(self, params):
        """处理发表趋势请求"""
        query = params.get("query", "")
        start_year = int(params.get("start_year", 2000))
        end_year = params.get("end_year")
        
        if end_year:
            end_year = int(end_year)
        
        if not query:
            return {"status": "error", "message": "搜索查询不能为空"}
        
        # 获取趋势数据
        trend_df = self.pubmed_api.get_publication_trends(query, start_year, end_year)
        
        # 生成趋势图
        fig = self.analyzer.publication_trend(
            trend_df, 
            time_column="year", 
            count_column="publication_count",
            title=f"Publication Trend: {query}"
        )
        
        # 将图表转换为Base64编码
        img_data = self._fig_to_base64(fig)
        
        return {
            "status": "success",
            "data": {
                "trend_data": trend_df.to_dict(orient="records"),
                "chart": img_data
            }
        }
    
    def _handle_journal_distribution(self, params):
        """处理期刊分布请求"""
        id_list = params.get("id_list", [])
        top_n = int(params.get("top_n", 10))
        
        if not id_list:
            return {"status": "error", "message": "ID列表不能为空"}
        
        # 获取期刊分布
        journal_df = self.pubmed_api.get_journal_distribution(id_list, top_n)
        
        # 生成分布图
        fig = self.analyzer.journal_distribution(
            journal_df,
            top_n=top_n,
            title="Top Journals"
        )
        
        # 将图表转换为Base64编码
        img_data = self._fig_to_base64(fig)
        
        return {
            "status": "success",
            "data": {
                "journal_data": journal_df.to_dict(orient="records"),
                "chart": img_data
            }
        }
    
    def _handle_author_network(self, params):
        """处理作者网络请求"""
        id_list = params.get("id_list", [])
        min_collaborations = int(params.get("min_collaborations", 2))
        
        if not id_list:
            return {"status": "error", "message": "ID列表不能为空"}
        
        # 获取文章详情
        articles = self.pubmed_api.fetch_details(id_list)
        
        # 生成作者网络图
        fig = self.analyzer.author_network(
            articles,
            min_collaborations=min_collaborations,
            title="Author Collaboration Network"
        )
        
        # 将图表转换为Base64编码
        img_data = self._fig_to_base64(fig)
        
        return {
            "status": "success",
            "data": {
                "chart": img_data
            }
        }
    
    def _handle_keyword_analysis(self, params):
        """处理关键词分析请求"""
        id_list = params.get("id_list", [])
        top_n = int(params.get("top_n", 20))
        
        if not id_list:
            return {"status": "error", "message": "ID列表不能为空"}
        
        # 获取文章详情
        articles = self.pubmed_api.fetch_details(id_list)
        
        # 转换为DataFrame
        df = self.analyzer.create_dataframe(articles)
        
        # 分析关键词
        keyword_df = self.analyzer.keyword_analysis(df, keyword_column="keywords", top_n=top_n)
        
        return {
            "status": "success",
            "data": {
                "keyword_data": keyword_df.to_dict(orient="records")
            }
        }
    
    def _handle_cluster_articles(self, params):
        """处理文章聚类请求"""
        id_list = params.get("id_list", [])
        n_clusters = int(params.get("n_clusters", 5))
        text_column = params.get("text_column", "abstract")
        
        if not id_list:
            return {"status": "error", "message": "ID列表不能为空"}
        
        # 获取文章详情
        articles = self.pubmed_api.fetch_details(id_list)
        
        # 转换为DataFrame
        df = self.analyzer.create_dataframe(articles)
        
        # 聚类文章
        result_df, fig = self.analyzer.cluster_articles(
            df,
            text_column=text_column,
            n_clusters=n_clusters
        )
        
        # 将图表转换为Base64编码
        img_data = None
        if fig:
            img_data = self._fig_to_base64(fig)
        
        return {
            "status": "success",
            "data": {
                "clustered_articles": result_df.to_dict(orient="records"),
                "chart": img_data
            }
        }
    
    def _handle_citation_analysis(self, params):
        """处理引用分析请求"""
        id_list = params.get("id_list", [])
        
        if not id_list:
            return {"status": "error", "message": "ID列表不能为空"}
        
        # 获取文章详情
        articles = self.pubmed_api.fetch_details(id_list)
        
        # 获取引用信息
        articles_with_citations = []
        for article in articles:
            pmid = article.get("pmid", "")
            citation_count = self.pubmed_api.get_citation_count(pmid)
            article["citation_count"] = citation_count
            articles_with_citations.append(article)
        
        # 分析引用数据
        citation_df, fig = self.analyzer.citation_analysis(articles_with_citations)
        
        # 将图表转换为Base64编码
        img_data = self._fig_to_base64(fig)
        
        return {
            "status": "success",
            "data": {
                "citation_data": citation_df.to_dict(orient="records"),
                "chart": img_data
            }
        }
    
    def _handle_download_full_text(self, params):
        """处理下载全文请求"""
        pmid = params.get("pmid", "")
        
        if not pmid:
            return {"status": "error", "message": "PMID不能为空"}
        
        # 获取全文链接
        full_text_info = self.pubmed_api.download_full_text(pmid)
        
        return {
            "status": "success",
            "data": full_text_info
        }
    
    def _handle_generate_wordcloud(self, params):
        """处理生成词云请求"""
        text = params.get("text", "")
        title = params.get("title", "Word Cloud")
        max_words = int(params.get("max_words", 100))
        background_color = params.get("background_color", "white")
        colormap = params.get("colormap", "viridis")
        chinese = params.get("chinese", False)
        
        if not text:
            return {"status": "error", "message": "文本不能为空"}
        
        # 生成词云
        fig = self.analyzer.generate_wordcloud(
            text,
            title=title,
            max_words=max_words,
            background_color=background_color,
            colormap=colormap,
            chinese=chinese
        )
        
        # 将图表转换为Base64编码
        img_data = self._fig_to_base64(fig)
        
        return {
            "status": "success",
            "data": {
                "chart": img_data
            }
        }
    
    def _fig_to_base64(self, fig):
        """将matplotlib图表转换为Base64编码"""
        buf = io.BytesIO()
        fig.savefig(buf, format='png', dpi=300, bbox_inches='tight')
        buf.seek(0)
        img_bytes = buf.getvalue()
        img_base64 = base64.b64encode(img_bytes).decode('utf-8')
        plt.close(fig)  # 关闭图表以释放内存
        return img_base64