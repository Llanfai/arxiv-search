# arxiv-search

一句话描述：这是一个通过 arXiv API 搜索论文的命令行工具。

## Features

- 通过 arXiv API 按关键词搜索论文
- 支持限制返回结果数量
- 支持输出 JSON 文件
- 429 限流时自动重试

## Installation

```bash
git clone https://github.com/Llanfai/arxiv-search.git
cd arxiv-search
conda create -n arxiv-search python=3.13 -y
conda activate arxiv-search
pip install -e .


 
# 打印到终端
arxiv-search "attention" --max-results 1

# 保存为 JSON
arxiv-search "attention" --max-results 5 --output result.json


```

 ## Usage

```bash
\# 打印到终端

arxiv-search "attention" --max-results 1

\# 保存为 JSON

arxiv-search "attention" --max-results 5 --output result.json
```

## Development

```bash
pytest -v
```
