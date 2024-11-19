import pytest
from unittest.mock import patch, mock_open
from dependency_visualizer import parse_packages_gz, build_dependency_graph, graph_to_mermaid


def test_parse_packages_gz():
    mock_gz_content = (
        "Package: pkg1\n"
        "Depends: pkg2 (>= 1.0), pkg3\n\n"
        "Package: pkg2\n"
        "Depends: pkg4\n\n"
        "Package: pkg3\n\n"
        "Package: pkg4\n\n"
    )
    with patch("gzip.open", mock_open(read_data=mock_gz_content)):
        packages = parse_packages_gz("dummy_path")
    expected = {
        "pkg1": ["pkg2", "pkg3"],
        "pkg2": ["pkg4"],
        "pkg3": [],
        "pkg4": [],
    }
    assert packages == expected


def test_build_dependency_graph():
    packages = {
        "pkg1": ["pkg2", "pkg3"],
        "pkg2": ["pkg4"],
        "pkg3": [],
        "pkg4": [],
    }
    graph = build_dependency_graph("pkg1", packages, 2)
    expected = {
        "pkg1": ["pkg2", "pkg3"],
        "pkg2": ["pkg4"],
        "pkg3": [],
        "pkg4": [],
    }
    assert graph == expected


def test_graph_to_mermaid():
    graph = {
        "pkg1": ["pkg2", "pkg3"],
        "pkg2": ["pkg4"],
    }
    mermaid = graph_to_mermaid(graph)
    expected = "graph TD\n  pkg1 --> pkg2\n  pkg1 --> pkg3\n  pkg2 --> pkg4"
    assert mermaid.strip() == expected.strip()
