import gzip
import re
from collections import defaultdict
import argparse
from pathlib import Path
import subprocess


def parse_packages_gz(file_path):
    """
    Разбирает файл Packages.gz и возвращает словарь с зависимостями пакетов.
    """
    packages = {}
    with gzip.open(file_path, "rt", encoding="utf-8") as f:
        content = f.read()
    package_entries = content.split("\n\n")

    for entry in package_entries:
        name = None
        dependencies = []
        for line in entry.split("\n"):
            if line.startswith("Package:"):
                name = line.split(": ")[1].strip()
            elif line.startswith("Depends:"):
                deps_raw = line.split(": ")[1].strip()
                dependencies = [
                    re.split(r" \(.*?\)", dep)[0] for dep in deps_raw.split(", ")
                ]
        if name:
            packages[name] = dependencies
    return packages


def build_dependency_graph(package_name, packages, max_depth):
    """
    Рекурсивно строит граф зависимостей до указанной глубины.
    """
    graph = defaultdict(list)
    visited = set()

    def traverse(package, depth):
        if depth > max_depth or package in visited or package not in packages:
            return
        visited.add(package)
        dependencies = packages.get(package, [])
        graph[package].extend(dependencies)
        for dep in dependencies:
            traverse(dep, depth + 1)

    traverse(package_name, 0)
    return graph


def graph_to_mermaid(graph):
    """
    Преобразует граф зависимостей в формат Mermaid.
    """
    lines = ["graph TD"]
    for package, dependencies in graph.items():
        for dep in dependencies:
            lines.append(f"  {package} --> {dep}")
    return "\n".join(lines)


def generate_graph_image(mermaid_code, output_path, visualizer_path):
    """
    Генерирует графическое изображение графа.
    """
    temp_mermaid_file = Path("temp_graph.mmd")
    temp_mermaid_file.write_text(mermaid_code, encoding="utf-8")

    try:
        subprocess.run(
            [visualizer_path, "-i", str(temp_mermaid_file), "-o", str(output_path)],
            check=True
        )
    finally:
        temp_mermaid_file.unlink()


def main():
    parser = argparse.ArgumentParser(description="Визуализатор графа зависимостей пакета Ubuntu.")
    parser.add_argument("packages_gz", help="Путь к файлу Packages.gz.")
    parser.add_argument("visualizer_path", help="Путь к программе для визуализации графов.")
    parser.add_argument("package_name", help="Имя анализируемого пакета.")
    parser.add_argument("max_depth", type=int, help="Максимальная глубина анализа зависимостей.")
    parser.add_argument("output_path", help="Путь для сохранения графического файла.")
    args = parser.parse_args()

    packages = parse_packages_gz(args.packages_gz)
    if args.package_name not in packages:
        print(f"Пакет '{args.package_name}' не найден в файле Packages.gz.")
        return

    graph = build_dependency_graph(args.package_name, packages, args.max_depth)
    mermaid_code = graph_to_mermaid(graph)
    generate_graph_image(mermaid_code, args.output_path, args.visualizer_path)
    print(f"Граф зависимостей сохранён в {args.output_path}")


if __name__ == "__main__":
    main()
