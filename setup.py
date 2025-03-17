"""
PubMed MCP服务安装脚本
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read().splitlines()

setup(
    name="pubmed-mcp",
    version="0.1.0",
    author="PubMed MCP Team",
    author_email="example@example.com",
    description="PubMed文献检索和分析多通道平台服务",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Darkroaster/pubmed-mcp",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
)