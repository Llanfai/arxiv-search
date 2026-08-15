from unittest.mock import Mock, patch
from requests.exceptions import HTTPError

from arxiv_search.main import parse_args, parse_papers, search_arxiv


SAMPLE_XML = """<?xml version='1.0' encoding='UTF-8'?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <entry>
    <title>Test Paper</title>
    <summary>This is a test summary.</summary>
    <id>http://arxiv.org/abs/1234.56789</id>
    <published>2024-01-01T00:00:00Z</published>
    <author><name>Alice</name></author>
    <author><name>Bob</name></author>
    <link rel="alternate" type="text/html" href="http://arxiv.org/abs/1234.56789"/>
    <link rel="related" type="application/pdf" href="http://arxiv.org/pdf/1234.56789"/>
  </entry>
</feed>
"""


def test_parse_args_default_values():
    args = parse_args(["attention"])
    assert args.query == "attention"
    assert args.max_results == 10
    assert args.output is None


def test_parse_args_custom_values():
    args = parse_args(["attention", "--max-results", "5", "--output", "out.json"])
    assert args.query == "attention"
    assert args.max_results == 5
    assert args.output == "out.json"


def test_parse_papers_extracts_paper_info():
    papers = parse_papers(SAMPLE_XML)
    assert len(papers) == 1

    paper = papers[0]
    assert paper.title == "Test Paper"
    assert paper.summary == "This is a test summary."
    assert paper.arxiv_id == "http://arxiv.org/abs/1234.56789"
    assert paper.authors == ["Alice", "Bob"]
    assert paper.published == "2024-01-01T00:00:00Z"
    assert paper.pdf_url == "http://arxiv.org/pdf/1234.56789"


def test_search_arxiv_success():
    mock_response = Mock()
    mock_response.text = SAMPLE_XML
    mock_response.raise_for_status.return_value = None

    with patch("arxiv_search.main.requests.get", return_value=mock_response):
        result = search_arxiv("attention", 1)
        assert result == SAMPLE_XML

def test_search_arxiv_retries_on_rate_limit():
    mock_429 = Mock()
    mock_429.status_code = 429
    mock_429.raise_for_status.side_effect = HTTPError(response=mock_429)


    mock_200 = Mock()
    mock_200.text = SAMPLE_XML
    mock_200.raise_for_status.return_value = None

    with patch("arxiv_search.main.requests.get", side_effect=[mock_429, mock_200]):
        result = search_arxiv("attention", 1, max_retries=2)
        assert result == SAMPLE_XML