import argparse
import toml
import re
import sys

class ConfigError(Exception):
    pass

class ConfigConverter:
    def __init__(self, constants=None):
        self.constants = constants or {}

    def parse_toml_file(self, input_path):
        try:
            with open(input_path, 'r') as f:
                return toml.load(f)
        except Exception as e:
            raise ConfigError(f"Ошибка чтения TOML файла: {e}")

    def convert(self, data, level=0):
        output = []
        if isinstance(data, dict):
            output.append("begin")
            for key, value in data.items():
                if not re.match(r"^[A-Za-z][_a-zA-Z0-9]*$", key):
                    raise ConfigError(f"Неверное имя ключа: {key}")
                output.append(f"{key} := {self.convert(value, level + 1)};")
            output.append("end")
        elif isinstance(data, list):
            output.append("<< " + ", ".join(self.convert(item, level + 1) for item in data) + " >>")
        elif isinstance(data, (int, float)):
            output.append(str(data))
        elif isinstance(data, str) and data.startswith("{") and data.endswith("}"):
            const_name = data[1:-1]
            if const_name not in self.constants:
                raise ConfigError(f"Неизвестная константа: {const_name}")
            output.append(str(self.constants[const_name]))
        elif isinstance(data, str):
            # Новая поддержка для строковых значений
            output.append(f"\"{data}\"")  # Оборачиваем строки в кавычки
        else:
            raise ConfigError(f"Неподдерживаемое значение: {data}")
        return " ".join(output)

    def process_constants(self, toml_data):
        for key, value in toml_data.get("constants", {}).items():
            if not re.match(r"^[A-Z][_a-zA-Z0-9]*$", key):
                raise ConfigError(f"Неверное имя константы: {key}")
            self.constants[key] = value

    def generate_output(self, toml_data):
        if "constants" in toml_data:
            self.process_constants(toml_data)
        return self.convert(toml_data)

def main():
    parser = argparse.ArgumentParser(description="Конвертер конфигурационного языка")
    parser.add_argument("--input", required=True, help="Путь к входному TOML-файлу")
    parser.add_argument("--output", required=True, help="Путь к выходному файлу")
    args = parser.parse_args()

    converter = ConfigConverter()
    try:
        toml_data = converter.parse_toml_file(args.input)
        output = converter.generate_output(toml_data)
        with open(args.output, 'w') as f:
            f.write(output)
    except ConfigError as e:
        sys.stderr.write(f"Ошибка: {e}\n")
        sys.exit(1)

if __name__ == "__main__":
    main()
