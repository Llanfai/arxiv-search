import argparse
import requests


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Search arXiv Papers")

    parser.add_argument("query", help="Search query string")

    parser.add_argument("--max-results",type=int, default=10,help="Maximum number of results")
    
    parser.add_argument("--output",default=None, help="Output file path (default: print to stdout)")

    return parser.parse_args()


def search_arxiv(query: str, max_results: int) -> str:

    url = "http://export.arxiv.org/api/query"
    params = {
        "search_query": f"all:{query}",
        "start": 0,
        "max_results": max_results,
    }
    response = requests.get(url,params=params)

    response.raise_for_status()

    return response.text

def main() -> None:
    args = parse_args()

    result = search_arxiv(args.query, args.max_results)
    print(result)
if __name__ == "__main__":
    main()