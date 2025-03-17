"""
PubMed MCP服务示例
"""

import json
import base64
from io import BytesIO
import matplotlib.pyplot as plt
from PIL import Image
from mcp_handler import MCPHandler

def main():
    """运行示例"""
    # 初始化MCP处理器
    # 注意：请替换为您自己的电子邮件地址
    handler = MCPHandler(email="your.email@example.com")
    
    # 示例1：基本搜索
    print("示例1：基本搜索")
    search_request = {
        "action": "search",
        "params": {
            "query": "cancer immunotherapy",
            "max_results": 10,
            "min_date": "2020/01/01"
        }
    }
    
    search_result = handler.handle_request(search_request["action"], search_request["params"])
    print(f"找到 {search_result['data']['count']} 篇文章")
    print(f"ID列表: {search_result['data']['id_list'][:3]}...")
    print()
    
    # 如果搜索成功，继续后续示例
    if search_result["status"] == "success" and search_result["data"]["count"] > 0:
        id_list = search_result["data"]["id_list"][:5]  # 仅使用前5个ID
        
        # 示例2：获取文章详情
        print("示例2：获取文章详情")
        details_request = {
            "action": "fetch_details",
            "params": {
                "id_list": id_list
            }
        }
        
        details_result = handler.handle_request(details_request["action"], details_request["params"])
        articles = details_result["data"]["articles"]
        
        print(f"获取了 {len(articles)} 篇文章的详细信息")
        if articles:
            first_article = articles[0]
            print(f"第一篇文章标题: {first_article['title']}")
            print(f"作者: {', '.join([f'{a.get('last_name', '')} {a.get('fore_name', '')}' for a in first_article.get('authors', [])[:2]])}")
            print(f"期刊: {first_article.get('journal', {}).get('name', '')}")
            print(f"摘要: {first_article.get('abstract', '')[:100]}...")
        print()
        
        # 示例3：期刊分布分析
        print("示例3：期刊分布分析")
        journal_request = {
            "action": "journal_distribution",
            "params": {
                "id_list": id_list,
                "top_n": 5
            }
        }
        
        journal_result = handler.handle_request(journal_request["action"], journal_request["params"])
        
        if "chart" in journal_result["data"]:
            print("期刊分布图已生成")
            # 可以将Base64编码的图像保存为文件或显示
            # display_image(journal_result["data"]["chart"])
        print()
        
        # 示例4：关键词分析
        print("示例4：关键词分析")
        keyword_request = {
            "action": "keyword_analysis",
            "params": {
                "id_list": id_list,
                "top_n": 10
            }
        }
        
        keyword_result = handler.handle_request(keyword_request["action"], keyword_request["params"])
        
        if "keyword_data" in keyword_result["data"]:
            keywords = keyword_result["data"]["keyword_data"]
            print("热门关键词:")
            for kw in keywords[:5]:
                print(f"  - {kw['keyword']}: {kw['frequency']}次")
        print()
        
        # 示例5：生成词云
        print("示例5：生成词云")
        # 合并所有摘要
        all_abstracts = " ".join([a.get("abstract", "") for a in articles])
        
        wordcloud_request = {
            "action": "generate_wordcloud",
            "params": {
                "text": all_abstracts,
                "title": "Cancer Immunotherapy Research",
                "max_words": 50
            }
        }
        
        wordcloud_result = handler.handle_request(wordcloud_request["action"], wordcloud_request["params"])
        
        if "chart" in wordcloud_result["data"]:
            print("词云图已生成")
            # 可以将Base64编码的图像保存为文件或显示
            # display_image(wordcloud_result["data"]["chart"])
        print()

def display_image(base64_img):
    """显示Base64编码的图像"""
    img_data = base64.b64decode(base64_img)
    img = Image.open(BytesIO(img_data))
    img.show()

if __name__ == "__main__":
    main()