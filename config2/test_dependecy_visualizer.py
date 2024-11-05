import pytest
import subprocess
from unittest import mock
import tempfile
import os


# Импортируем функции из основного скрипта, например
from dependency_visualizer import parse_args, get_dependencies, generate_mermaid_graph, visualize_graph

def test_parse_args():
    # Тестируем разбор аргументов командной строки
    test_args = ["script.py", "/path/to/visualizer", "nginx", "3"]
    with mock.patch("sys.argv", test_args):
        args = parse_args()
        assert args.visualizer_path == "/path/to/visualizer"
        assert args.package_name == "nginx"
        assert args.max_depth == 3


@mock.patch("subprocess.run")
def test_get_dependencies(mock_run):
    # Мокаем результат subprocess для apt-cache
    mock_run.return_value = mock.Mock(
        returncode=0,
        stdout="Depends: libfoo\nDepends: libbar"
    )

    # Проверка на корректное построение графа зависимостей
    dependencies = get_dependencies("testpkg", 1, 2)
    assert "testpkg" in dependencies
    assert dependencies["testpkg"] == ["libfoo", "libbar"]
    assert "libfoo" in dependencies
    assert "libbar" in dependencies


def test_generate_mermaid_graph():
    # Проверяем, что генерируется корректный код для mermaid
    dependencies = {
        "pkg1": ["dep1", "dep2"],
        "dep1": ["dep3"],
        "dep2": [],
        "dep3": []
    }
    mermaid_code = generate_mermaid_graph(dependencies)
    expected_code = "graph TD\n    pkg1 --> dep1\n    pkg1 --> dep2\n    dep1 --> dep3"
    assert mermaid_code.strip() == expected_code.strip()


@mock.patch("subprocess.run")
def test_visualize_graph(mock_run):
    # Генерируем временный mermaid-код для теста
    mermaid_code = "graph TD\n    pkg1 --> dep1"
    with tempfile.NamedTemporaryFile(delete=True, suffix=".mmd") as temp_file:
        temp_file_path = temp_file.name

    # Вызываем функцию визуализации
    visualize_graph(mermaid_code, "/path/to/visualizer")

    # Проверяем, что subprocess вызван с правильными аргументами
    mock_run.assert_called_once_with(["/path/to/visualizer", mock.ANY], check=True)

    # Проверяем, что временный файл удалён после вызова функции
    assert not os.path.exists(temp_file_path)
