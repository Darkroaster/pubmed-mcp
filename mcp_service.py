"""
PubMed MCP服务入口
"""

import json
import sys
import argparse
from mcp_handler import MCPHandler

def main():
    """MCP服务主函数"""
    parser = argparse.ArgumentParser(description="PubMed MCP服务")
    parser.add_argument("--email", required=True, help="用户电子邮件地址（NCBI要求）")
    parser.add_argument("--api-key", help="NCBI API密钥（可选）")
    parser.add_argument("--input", help="输入JSON文件路径")
    parser.add_argument("--output", help="输出JSON文件路径")
    
    args = parser.parse_args()
    
    # 初始化MCP处理器
    handler = MCPHandler(email=args.email, api_key=args.api_key)
    
    # 处理输入
    if args.input:
        # 从文件读取请求
        try:
            with open(args.input, 'r', encoding='utf-8') as f:
                request = json.load(f)
        except Exception as e:
            print(f"读取输入文件错误: {e}")
            sys.exit(1)
    else:
        # 从标准输入读取请求
        try:
            request = json.load(sys.stdin)
        except Exception as e:
            print(f"读取标准输入错误: {e}")
            sys.exit(1)
    
    # 验证请求格式
    if not isinstance(request, dict) or "action" not in request or "params" not in request:
        print("无效的请求格式，必须包含'action'和'params'字段")
        sys.exit(1)
    
    # 处理请求
    result = handler.handle_request(request["action"], request["params"])
    
    # 输出结果
    if args.output:
        # 写入到文件
        try:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"写入输出文件错误: {e}")
            sys.exit(1)
    else:
        # 写入到标准输出
        print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()