"""arXiv 论文搜索命令行工具。"""

import argparse
import requests
from dataclasses import dataclass, asdict
from xml.etree import ElementTree as ET
import json


@dataclass
class Paper:
    title: str
    summary: str
    arxiv_id: str
    published: str
    authors: list[str]
    pdf_url: str


def parse_args() -> argparse.Namespace:
    """解析命令行参数。"""
    parser = argparse.ArgumentParser(description="Search arXiv Papers")

    # 位置参数:搜索关键词(必填)
    parser.add_argument("query", help="Search query string")

    # 可选参数:返回结果的最大数量,默认 10
    parser.add_argument(
        "--max-results", type=int, default=10, help="Maximum number of results"
    )

    # 可选参数:结果写入的文件路径,默认打印到 stdout
    parser.add_argument(
        "--output", default=None, help="Output file path (default: print to stdout)"
    )

    return parser.parse_args()


def search_arxiv(query: str, max_results: int) -> str:
    """调用 arXiv API 搜索论文,返回原始 XML 响应文本。"""
    url = "http://export.arxiv.org/api/query"
    # 查询参数,requests 会自动 URL-encode 并拼接到 url 后面
    # "all:" 是 arXiv API 的查询前缀,表示在标题、摘要等所有字段中搜索
    params = {
        "search_query": f"all:{query}",
        "start": 0,
        "max_results": max_results,
    }
    response = requests.get(url, params=params)

    # 状态码非 2xx 时抛出 requests.HTTPError,避免静默拿到错误页面
    response.raise_for_status()

    return response.text


def parse_papers(xml_text: str) -> list[Paper]:
    root = ET.fromstring(xml_text)
    ns = {
        "atom": "http://www.w3.org/2005/Atom",
        "arxiv": "http://arxiv.org/schemas/atom",
    }

    papers: list[Paper] = []
    # findall aim to find all specific element in this field
    for entry in root.findall("atom:entry", ns):
        #find is aim to find the first one specific element in the son field ,text() aim to get the content of element text,get() access the attributes
        title = entry.find("atom:title", ns).text
        summary = entry.find("atom:summary", ns).text
        arxiv_id = entry.find("atom:id", ns).text
        published = entry.find("atom:published", ns).text

        authors: list[str] = []
        for author in entry.findall("atom:author", ns):
            name = author.find("atom:name", ns)
            if name is not None:
                authors.append(name.text)


        pdf_url = ""
        for link in entry.findall("atom:link",ns):
            rel = link.get("rel")
            link_type = link.get("type")
            if rel == "related" and link_type == "application/pdf":
                pdf_url = link.get("href")
                break

        papers.append(Paper(
            title=title,
            summary=summary,
            arxiv_id=arxiv_id,
            authors=authors,
            published=published,
            pdf_url=pdf_url,
        ))

    return papers


def main() -> None:
    """程序入口:解析参数 -> 搜索 -> 打印结果。"""
    args = parse_args()
    xml_result = search_arxiv(args.query, args.max_results)
    papers = parse_papers(xml_result)


    if args.output is None:
        for paper in papers:
            print(f"Title: {paper.title}")
            print(f"Authors: {', '.join(paper.authors)}")
            print(f"Published: {paper.published}")
            print(f"PDF: {paper.pdf_url}")
            print(f"Summary: {paper.summary[:200]}...")
            print("---")
    else:
        with open(args.output,"w", encoding="utf-8") as f:
            papers_data = [asdict(paper) for paper in papers]
            json.dump(papers_data, f, ensure_ascii=False, indent=2)

# Python 惯用法:仅当文件被直接运行时执行 main(),
# 被其他模块 import 时不执行(类似 Go main 包中 func main 的角色)
if __name__ == "__main__":
    main()
