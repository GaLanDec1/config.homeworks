import argparse
import subprocess
import os
import tempfile

def parse_args():
    parser = argparse.ArgumentParser(description="Визуализатор зависимостей пакета")
    parser.add_argument("visualizer_path", help="Путь к программе для визуализации графов")
    parser.add_argument("package_name", help="Имя анализируемого пакета")
    parser.add_argument("max_depth", type=int, help="Максимальная глубина анализа зависимостей")
    return parser.parse_args()


def get_dependencies(package_name, depth, max_depth, dependencies=None):
    if dependencies is None:
        dependencies = {}
    if depth > max_depth:
        return

    # Выполняем команду `apt-cache depends`
    result = subprocess.run(
        ["apt-cache", "depends", package_name],
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        raise ValueError(f"Не удалось получить зависимости для пакета: {package_name}")

    # Разбор вывода команды
    dependencies[package_name] = []
    for line in result.stdout.splitlines():
        if line.strip().startswith("Depends:"):
            dep_pkg = line.split()[-1]
            dependencies[package_name].append(dep_pkg)
            if dep_pkg not in dependencies:
                get_dependencies(dep_pkg, depth + 1, max_depth, dependencies)

    return dependencies
def generate_mermaid_graph(dependencies):
    mermaid_graph = ["graph TD"]
    for pkg, deps in dependencies.items():
        for dep in deps:
            mermaid_graph.append(f"    {pkg} --> {dep}")
    return "\n".join(mermaid_graph)


def visualize_graph(mermaid_code, visualizer_path):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mmd") as temp_file:
        temp_file.write(mermaid_code.encode())
        temp_file_path = temp_file.name

    try:
        subprocess.run([visualizer_path, temp_file_path], check=True)
    finally:
        os.remove(temp_file_path)
def main():
    args = parse_args()
    dependencies = get_dependencies(args.package_name, 1, args.max_depth)
    mermaid_code = generate_mermaid_graph(dependencies)
    visualize_graph(mermaid_code, args.visualizer_path)
