"""
分析模块 - 提供PubMed数据分析功能
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from collections import Counter
from wordcloud import WordCloud
import jieba
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import networkx as nx

class PubMedAnalyzer:
    """PubMed数据分析类"""
    
    def __init__(self):
        """初始化分析器"""
        pass
    
    def create_dataframe(self, articles):
        """
        将文章列表转换为DataFrame
        
        参数:
            articles (list): 文章详情列表
            
        返回:
            pandas.DataFrame: 文章数据框
        """
        # 提取基本字段
        data = []
        for article in articles:
            # 处理出版日期
            pub_date = article.get("publication_date", {})
            year = pub_date.get("year", "")
            month = pub_date.get("month", "")
            day = pub_date.get("day", "")
            
            # 处理作者
            authors = article.get("authors", [])
            author_names = []
            for author in authors:
                if "last_name" in author and "fore_name" in author:
                    author_names.append(f"{author['last_name']} {author['fore_name']}")
            
            # 添加到数据列表
            data.append({
                "pmid": article.get("pmid", ""),
                "title": article.get("title", ""),
                "abstract": article.get("abstract", ""),
                "journal": article.get("journal", {}).get("name", ""),
                "year": year,
                "month": month,
                "day": day,
                "authors": "; ".join(author_names),
                "keywords": "; ".join(article.get("keywords", [])),
                "doi": article.get("doi", ""),
                "url": article.get("pubmed_url", "")
            })
        
        return pd.DataFrame(data)
    
    def publication_trend(self, df, time_column="year", count_column=None, title="Publication Trend"):
        """
        生成发表趋势图
        
        参数:
            df (pandas.DataFrame): 文章数据框
            time_column (str): 时间列名
            count_column (str, 可选): 计数列名，如果为None则计算每个时间单位的文章数
            title (str): 图表标题
            
        返回:
            matplotlib.figure.Figure: 趋势图
        """
        # 确保时间列为字符串类型
        df[time_column] = df[time_column].astype(str)
        
        # 按时间分组并计数
        if count_column:
            trend_data = df.groupby(time_column)[count_column].sum().reset_index()
            y_label = count_column
        else:
            trend_data = df.groupby(time_column).size().reset_index(name="count")
            y_label = "文章数量"
        
        # 按时间排序
        trend_data = trend_data.sort_values(time_column)
        
        # 创建图表
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(trend_data[time_column], trend_data["count" if not count_column else count_column], 
                marker='o', linestyle='-', linewidth=2)
        
        # 设置标签和标题
        ax.set_xlabel(time_column)
        ax.set_ylabel(y_label)
        ax.set_title(title)
        
        # 设置网格和样式
        ax.grid(True, linestyle='--', alpha=0.7)
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        return fig
    
    def journal_distribution(self, df, top_n=10, title="Top Journals"):
        """
        生成期刊分布图
        
        参数:
            df (pandas.DataFrame): 文章数据框
            top_n (int): 显示前N个期刊
            title (str): 图表标题
            
        返回:
            matplotlib.figure.Figure: 分布图
        """
        # 统计期刊频率
        journal_counts = df["journal"].value_counts().reset_index()
        journal_counts.columns = ["journal", "count"]
        
        # 获取前N个期刊
        top_journals = journal_counts.head(top_n)
        
        # 创建图表
        fig, ax = plt.subplots(figsize=(12, 8))
        bars = ax.barh(top_journals["journal"], top_journals["count"], color='skyblue')
        
        # 添加数值标签
        for bar in bars:
            width = bar.get_width()
            ax.text(width + 0.3, bar.get_y() + bar.get_height()/2, f"{width:.0f}", 
                    ha='left', va='center')
        
        # 设置标签和标题
        ax.set_xlabel("文章数量")
        ax.set_ylabel("期刊")
        ax.set_title(title)
        
        # 反转y轴，使最高频率的期刊显示在顶部
        ax.invert_yaxis()
        
        plt.tight_layout()
        return fig
    
    def author_network(self, articles, min_collaborations=2, title="Author Collaboration Network"):
        """
        生成作者合作网络图
        
        参数:
            articles (list): 文章详情列表
            min_collaborations (int): 最小合作次数
            title (str): 图表标题
            
        返回:
            matplotlib.figure.Figure: 网络图
        """
        # 创建图
        G = nx.Graph()
        
        # 统计作者合作
        collaborations = {}
        
        for article in articles:
            authors = article.get("authors", [])
            author_names = []
            
            # 提取作者姓名
            for author in authors:
                if "last_name" in author and "fore_name" in author:
                    name = f"{author['last_name']} {author['fore_name']}"
                    author_names.append(name)
                    # 添加节点
                    if name not in G:
                        G.add_node(name)
            
            # 添加合作关系
            for i in range(len(author_names)):
                for j in range(i+1, len(author_names)):
                    author1 = author_names[i]
                    author2 = author_names[j]
                    
                    # 更新合作次数
                    if (author1, author2) in collaborations:
                        collaborations[(author1, author2)] += 1
                    elif (author2, author1) in collaborations:
                        collaborations[(author2, author1)] += 1
                    else:
                        collaborations[(author1, author2)] = 1
        
        # 添加边，只包括合作次数达到阈值的
        for (author1, author2), count in collaborations.items():
            if count >= min_collaborations:
                G.add_edge(author1, author2, weight=count)
        
        # 移除孤立节点
        G.remove_nodes_from(list(nx.isolates(G)))
        
        # 如果没有足够的节点，返回空图
        if len(G.nodes) < 2:
            fig, ax = plt.subplots(figsize=(10, 8))
            ax.text(0.5, 0.5, "没有足够的作者合作数据", ha='center', va='center')
            ax.set_title(title)
            return fig
        
        # 创建图表
        fig, ax = plt.subplots(figsize=(12, 10))
        
        # 计算节点大小（基于度中心性）
        centrality = nx.degree_centrality(G)
        node_size = [centrality[node] * 3000 for node in G.nodes]
        
        # 计算边宽度（基于权重）
        edge_width = [G[u][v]['weight'] * 0.5 for u, v in G.edges]
        
        # 使用spring布局
        pos = nx.spring_layout(G, k=0.3, iterations=50)
        
        # 绘制网络
        nx.draw_networkx_nodes(G, pos, node_size=node_size, node_color='skyblue', alpha=0.8)
        nx.draw_networkx_edges(G, pos, width=edge_width, alpha=0.5, edge_color='gray')
        nx.draw_networkx_labels(G, pos, font_size=8, font_family='sans-serif')
        
        ax.set_title(title)
        ax.axis('off')
        
        plt.tight_layout()
        return fig
    
    def generate_wordcloud(self, text, title="Word Cloud", max_words=100, 
                          background_color="white", colormap="viridis", 
                          chinese=False, stopwords=None):
        """
        生成词云图
        
        参数:
            text (str): 文本内容
            title (str): 图表标题
            max_words (int): 最大词数
            background_color (str): 背景颜色
            colormap (str): 颜色映射
            chinese (bool): 是否为中文文本
            stopwords (set): 停用词集合
            
        返回:
            matplotlib.figure.Figure: 词云图
        """
        if not text:
            # 如果文本为空，返回空图
            fig, ax = plt.subplots(figsize=(10, 8))
            ax.text(0.5, 0.5, "没有足够的文本数据", ha='center', va='center')
            ax.set_title(title)
            return fig
        
        # 默认停用词
        if stopwords is None:
            stopwords = set(['the', 'and', 'of', 'to', 'in', 'a', 'is', 'that', 'for', 'with', 
                            'as', 'by', 'on', 'are', 'be', 'this', 'was', 'we', 'were', 'from'])
        
        # 处理中文文本
        if chinese:
            # 使用jieba分词
            words = jieba.cut(text)
            text = " ".join(words)
        
        # 创建词云
        wordcloud = WordCloud(
            max_words=max_words,
            background_color=background_color,
            colormap=colormap,
            stopwords=stopwords,
            width=800,
            height=400,
            random_state=42
        ).generate(text)
        
        # 创建图表
        fig, ax = plt.subplots(figsize=(10, 8))
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.set_title(title)
        ax.axis('off')
        
        plt.tight_layout()
        return fig
    
    def keyword_analysis(self, df, keyword_column="keywords", top_n=20):
        """
        分析关键词频率
        
        参数:
            df (pandas.DataFrame): 文章数据框
            keyword_column (str): 关键词列名
            top_n (int): 返回前N个关键词
            
        返回:
            pandas.DataFrame: 关键词频率数据框
        """
        # 提取所有关键词
        all_keywords = []
        for keywords in df[keyword_column].dropna():
            # 假设关键词以分号分隔
            if isinstance(keywords, str):
                keywords_list = [k.strip() for k in keywords.split(';')]
                all_keywords.extend(keywords_list)
        
        # 统计频率
        keyword_counts = Counter(all_keywords)
        
        # 转换为DataFrame
        keyword_df = pd.DataFrame({
            'keyword': list(keyword_counts.keys()),
            'frequency': list(keyword_counts.values())
        })
        
        # 排序并返回前N个
        return keyword_df.sort_values('frequency', ascending=False).head(top_n)
    
    def cluster_articles(self, df, text_column="abstract", n_clusters=5, max_features=1000):
        """
        使用K-means聚类文章
        
        参数:
            df (pandas.DataFrame): 文章数据框
            text_column (str): 文本列名
            n_clusters (int): 聚类数量
            max_features (int): 最大特征数量
            
        返回:
            tuple: (聚类结果DataFrame, 聚类可视化图)
        """
        # 过滤掉没有文本的行
        df_filtered = df[df[text_column].notna() & (df[text_column] != "")].copy()
        
        if len(df_filtered) < n_clusters:
            return df, None
        
        # 创建TF-IDF向量
        vectorizer = TfidfVectorizer(max_features=max_features, stop_words='english')
        X = vectorizer.fit_transform(df_filtered[text_column])
        
        # 应用K-means聚类
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        df_filtered['cluster'] = kmeans.fit_predict(X)
        
        # 使用PCA降维以便可视化
        pca = PCA(n_components=2)
        X_pca = pca.fit_transform(X.toarray())
        
        # 创建可视化
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # 为每个聚类绘制散点图
        for i in range(n_clusters):
            mask = df_filtered['cluster'] == i
            ax.scatter(X_pca[mask, 0], X_pca[mask, 1], label=f'Cluster {i+1}', alpha=0.7)
        
        # 添加聚类中心
        centers = pca.transform(kmeans.cluster_centers_)
        ax.scatter(centers[:, 0], centers[:, 1], s=100, c='black', marker='X', label='Centroids')
        
        ax.set_title('文章聚类')
        ax.set_xlabel('PCA Component 1')
        ax.set_ylabel('PCA Component 2')
        ax.legend()
        
        plt.tight_layout()
        
        # 合并结果回原始DataFrame
        result_df = df.copy()
        result_df = result_df.reset_index(drop=True)
        df_filtered = df_filtered.reset_index(drop=True)
        
        # 将聚类结果添加到原始DataFrame
        result_df['cluster'] = None
        for i in range(len(df_filtered)):
            idx = df_filtered.index[i]
            if idx < len(result_df):
                result_df.at[idx, 'cluster'] = df_filtered.at[idx, 'cluster']
        
        return result_df, fig
    
    def citation_analysis(self, articles_with_citations):
        """
        分析引用数据
        
        参数:
            articles_with_citations (list): 包含引用信息的文章列表
            
        返回:
            tuple: (引用统计DataFrame, 引用分布图)
        """
        # 提取PMID和引用次数
        data = []
        for article in articles_with_citations:
            data.append({
                'pmid': article.get('pmid', ''),
                'title': article.get('title', ''),
                'citations': article.get('citation_count', 0),
                'year': article.get('publication_date', {}).get('year', '')
            })
        
        # 创建DataFrame
        citation_df = pd.DataFrame(data)
        
        # 创建引用分布图
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # 按引用次数排序
        top_cited = citation_df.sort_values('citations', ascending=False).head(20)
        
        # 绘制条形图
        bars = ax.barh(top_cited['title'].str[:50], top_cited['citations'], color='skyblue')
        
        # 添加数值标签
        for bar in bars:
            width = bar.get_width()
            ax.text(width + 0.3, bar.get_y() + bar.get_height()/2, f"{width:.0f}", 
                    ha='left', va='center')
        
        ax.set_xlabel('引用次数')
        ax.set_ylabel('文章')
        ax.set_title('引用分析 - 被引用最多的文章')
        ax.invert_yaxis()  # 最高引用的文章显示在顶部
        
        plt.tight_layout()
        
        return citation_df, fig
    
    def export_to_excel(self, df, filename):
        """
        导出数据到Excel文件
        
        参数:
            df (pandas.DataFrame): 要导出的数据框
            filename (str): 输出文件名
            
        返回:
            bool: 是否成功导出
        """
        try:
            df.to_excel(filename, index=False)
            return True
        except Exception as e:
            print(f"导出Excel错误: {e}")
            return False
    
    def export_to_csv(self, df, filename, encoding='utf-8'):
        """
        导出数据到CSV文件
        
        参数:
            df (pandas.DataFrame): 要导出的数据框
            filename (str): 输出文件名
            encoding (str): 文件编码
            
        返回:
            bool: 是否成功导出
        """
        try:
            df.to_csv(filename, index=False, encoding=encoding)
            return True
        except Exception as e:
            print(f"导出CSV错误: {e}")
            return False