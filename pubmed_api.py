"""
PubMed API模块 - 提供与PubMed数据库交互的功能
"""

import time
import json
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime
import pandas as pd
from Bio import Entrez
from tqdm import tqdm

class PubMedAPI:
    """PubMed API交互类"""
    
    def __init__(self, email, tool="PubMedMCP", api_key=None):
        """
        初始化PubMed API交互类
        
        参数:
            email (str): 用户电子邮件地址（NCBI要求提供）
            tool (str): 工具名称（NCBI要求提供）
            api_key (str, 可选): NCBI API密钥，可提高请求限制
        """
        self.email = email
        self.tool = tool
        self.api_key = api_key
        
        # 设置Entrez参数
        Entrez.email = email
        Entrez.tool = tool
        if api_key:
            Entrez.api_key = api_key
    
    def search(self, query, max_results=100, sort="relevance", min_date=None, max_date=None):
        """
        搜索PubMed文献
        
        参数:
            query (str): 搜索查询字符串
            max_results (int): 最大结果数量
            sort (str): 排序方式 ("relevance", "pub_date")
            min_date (str): 最早日期 (YYYY/MM/DD)
            max_date (str): 最晚日期 (YYYY/MM/DD)
            
        返回:
            list: PubMed ID列表
        """
        # 构建日期范围
        date_range = ""
        if min_date or max_date:
            min_date = min_date or "1900/01/01"
            max_date = max_date or datetime.now().strftime("%Y/%m/%d")
            date_range = f" AND {min_date}:{max_date}[Date - Publication]"
        
        # 完整查询
        full_query = query + date_range
        
        # 执行搜索
        try:
            handle = Entrez.esearch(
                db="pubmed",
                term=full_query,
                retmax=max_results,
                sort=sort
            )
            record = Entrez.read(handle)
            handle.close()
            
            return record["IdList"]
        except Exception as e:
            print(f"搜索错误: {e}")
            return []
    
    def fetch_details(self, id_list, batch_size=100):
        """
        获取文章详细信息
        
        参数:
            id_list (list): PubMed ID列表
            batch_size (int): 批处理大小
            
        返回:
            list: 文章详细信息列表
        """
        articles = []
        
        # 分批处理
        for i in range(0, len(id_list), batch_size):
            batch_ids = id_list[i:i+batch_size]
            try:
                handle = Entrez.efetch(db="pubmed", id=batch_ids, retmode="xml")
                records = Entrez.read(handle)
                handle.close()
                
                for record in records["PubmedArticle"]:
                    article = self._parse_article(record)
                    articles.append(article)
                
                # 遵循NCBI API使用指南，避免过多请求
                time.sleep(0.34)  # 每秒不超过3个请求
            except Exception as e:
                print(f"获取详情错误 (IDs {batch_ids}): {e}")
        
        return articles
    
    def _parse_article(self, record):
        """解析PubMed文章记录"""
        article_data = {}
        
        try:
            # 基本信息
            article_data["pmid"] = record["MedlineCitation"]["PMID"]
            
            article = record["MedlineCitation"]["Article"]
            
            # 标题
            article_data["title"] = article.get("ArticleTitle", "")
            
            # 期刊信息
            journal = article.get("Journal", {})
            journal_info = {
                "name": journal.get("Title", ""),
                "iso_abbreviation": journal.get("ISOAbbreviation", ""),
                "issn": journal.get("ISSN", ""),
            }
            
            # 出版日期
            pub_date = {}
            if "PubDate" in journal.get("JournalIssue", {}):
                date_fields = journal["JournalIssue"]["PubDate"]
                if "Year" in date_fields:
                    pub_date["year"] = date_fields["Year"]
                if "Month" in date_fields:
                    pub_date["month"] = date_fields["Month"]
                if "Day" in date_fields:
                    pub_date["day"] = date_fields["Day"]
            
            article_data["journal"] = journal_info
            article_data["publication_date"] = pub_date
            
            # 作者
            authors = []
            if "AuthorList" in article:
                for author in article["AuthorList"]:
                    if "LastName" in author and "ForeName" in author:
                        authors.append({
                            "last_name": author["LastName"],
                            "fore_name": author["ForeName"],
                            "initials": author.get("Initials", ""),
                            "affiliations": author.get("AffiliationInfo", [])
                        })
            article_data["authors"] = authors
            
            # 摘要
            abstract = ""
            if "Abstract" in article:
                abstract_parts = []
                for abstract_text in article["Abstract"]["AbstractText"]:
                    if isinstance(abstract_text, str):
                        abstract_parts.append(abstract_text)
                    elif isinstance(abstract_text, dict):
                        # 处理带标签的摘要部分
                        label = abstract_text.get("Label", "")
                        text = abstract_text.get("#text", "")
                        if label and text:
                            abstract_parts.append(f"{label}: {text}")
                        elif text:
                            abstract_parts.append(text)
                abstract = " ".join(abstract_parts)
            article_data["abstract"] = abstract
            
            # 关键词
            keywords = []
            if "KeywordList" in record["MedlineCitation"]:
                for keyword_list in record["MedlineCitation"]["KeywordList"]:
                    keywords.extend(keyword_list)
            article_data["keywords"] = keywords
            
            # DOI
            article_data["doi"] = ""
            if "ArticleIdList" in record["PubmedData"]:
                for article_id in record["PubmedData"]["ArticleIdList"]:
                    if article_id.attributes.get("IdType") == "doi":
                        article_data["doi"] = str(article_id)
            
            # PubMed URL
            article_data["pubmed_url"] = f"https://pubmed.ncbi.nlm.nih.gov/{article_data['pmid']}/"
            
        except Exception as e:
            print(f"解析文章错误: {e}")
        
        return article_data
    
    def advanced_search(self, params):
        """
        高级搜索功能
        
        参数:
            params (dict): 搜索参数字典，可包含以下键:
                - author: 作者名
                - title: 标题关键词
                - journal: 期刊名
                - year: 出版年份
                - abstract: 摘要关键词
                - mesh_terms: MeSH术语
                
        返回:
            list: PubMed ID列表
        """
        query_parts = []
        
        # 构建查询部分
        if "author" in params and params["author"]:
            query_parts.append(f"{params['author']}[Author]")
        
        if "title" in params and params["title"]:
            query_parts.append(f"{params['title']}[Title]")
        
        if "journal" in params and params["journal"]:
            query_parts.append(f"{params['journal']}[Journal]")
        
        if "year" in params and params["year"]:
            query_parts.append(f"{params['year']}[Publication Date]")
        
        if "abstract" in params and params["abstract"]:
            query_parts.append(f"{params['abstract']}[Abstract]")
        
        if "mesh_terms" in params and params["mesh_terms"]:
            query_parts.append(f"{params['mesh_terms']}[MeSH Terms]")
        
        # 组合查询
        query = " AND ".join(query_parts)
        
        # 执行搜索
        return self.search(query, 
                          max_results=params.get("max_results", 100),
                          sort=params.get("sort", "relevance"),
                          min_date=params.get("min_date"),
                          max_date=params.get("max_date"))
    
    def get_publication_trends(self, query, start_year, end_year=None):
        """
        获取发表趋势数据
        
        参数:
            query (str): 搜索查询
            start_year (int): 开始年份
            end_year (int, 可选): 结束年份，默认为当前年份
            
        返回:
            pandas.DataFrame: 年度发表数量数据
        """
        if not end_year:
            end_year = datetime.now().year
        
        years = list(range(start_year, end_year + 1))
        counts = []
        
        for year in years:
            year_query = f"({query}) AND {year}[Publication Date]"
            try:
                handle = Entrez.esearch(db="pubmed", term=year_query)
                record = Entrez.read(handle)
                handle.close()
                counts.append(int(record["Count"]))
                time.sleep(0.34)  # 遵循NCBI API使用指南
            except Exception as e:
                print(f"获取{year}年趋势数据错误: {e}")
                counts.append(0)
        
        return pd.DataFrame({"year": years, "publication_count": counts})
    
    def get_journal_distribution(self, id_list, top_n=10):
        """
        获取期刊分布数据
        
        参数:
            id_list (list): PubMed ID列表
            top_n (int): 返回前N个期刊
            
        返回:
            pandas.DataFrame: 期刊分布数据
        """
        articles = self.fetch_details(id_list)
        
        # 统计期刊出现次数
        journal_counts = {}
        for article in articles:
            journal_name = article.get("journal", {}).get("name", "Unknown")
            if journal_name in journal_counts:
                journal_counts[journal_name] += 1
            else:
                journal_counts[journal_name] = 1
        
        # 转换为DataFrame并排序
        df = pd.DataFrame({
            "journal": list(journal_counts.keys()),
            "article_count": list(journal_counts.values())
        })
        df = df.sort_values("article_count", ascending=False).reset_index(drop=True)
        
        return df.head(top_n)
    
    def download_full_text(self, pmid):
        """
        尝试获取全文链接
        
        参数:
            pmid (str): PubMed ID
            
        返回:
            dict: 包含全文链接信息的字典
        """
        result = {
            "pmid": pmid,
            "has_free_full_text": False,
            "full_text_links": []
        }
        
        try:
            # 使用ELink查找全文链接
            handle = Entrez.elink(dbfrom="pubmed", id=pmid, linkname="pubmed_pmc")
            record = Entrez.read(handle)
            handle.close()
            
            # 检查是否有PMC链接
            if record and record[0]["LinkSetDb"]:
                for link in record[0]["LinkSetDb"][0]["Link"]:
                    pmc_id = link["Id"]
                    result["has_free_full_text"] = True
                    result["full_text_links"].append({
                        "type": "PMC",
                        "url": f"https://www.ncbi.nlm.nih.gov/pmc/articles/PMC{pmc_id}/"
                    })
            
            # 如果没有PMC链接，尝试获取DOI链接
            if not result["has_free_full_text"]:
                handle = Entrez.efetch(db="pubmed", id=pmid, retmode="xml")
                record = Entrez.read(handle)
                handle.close()
                
                if "PubmedArticle" in record and record["PubmedArticle"]:
                    article = record["PubmedArticle"][0]
                    if "PubmedData" in article and "ArticleIdList" in article["PubmedData"]:
                        for article_id in article["PubmedData"]["ArticleIdList"]:
                            if article_id.attributes.get("IdType") == "doi":
                                doi = str(article_id)
                                result["full_text_links"].append({
                                    "type": "DOI",
                                    "url": f"https://doi.org/{doi}"
                                })
        
        except Exception as e:
            print(f"获取全文链接错误 (PMID {pmid}): {e}")
        
        return result
    
    def get_citation_count(self, pmid):
        """
        获取文章被引用次数
        
        参数:
            pmid (str): PubMed ID
            
        返回:
            int: 被引用次数
        """
        try:
            # 使用ELink查找引用该文章的文章
            handle = Entrez.elink(dbfrom="pubmed", id=pmid, linkname="pubmed_pubmed_citedin")
            record = Entrez.read(handle)
            handle.close()
            
            # 计算引用次数
            if record and record[0]["LinkSetDb"]:
                return len(record[0]["LinkSetDb"][0]["Link"])
            return 0
        
        except Exception as e:
            print(f"获取引用次数错误 (PMID {pmid}): {e}")
            return 0