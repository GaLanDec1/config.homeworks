import re
import copy
import toml
class ConfigError(Exception):
    """Класс для обработки ошибок конфигурации."""
    pass

class ConfigConverter:
    def __init__(self, constants=None):
        """Инициализация с возможностью передачи констант."""
        self.constants = constants or {}

    def evaluate_expression(self, expression, context):
        """Вычисляет выражение, используя переданные константы и текущий контекст."""
        try:
            # Объединяем context и constants для поддержки всех переменных
            full_context = {**self.constants, **context}
            return eval(expression, {}, full_context)
        except Exception as e:
            raise ConfigError(f"Ошибка в вычислении выражения: {expression}") from e

    def resolve_constants(self, value, context=None, delay_expressions=False):
        """Подставляет константы и вычисляет выражения, если они есть."""
        context = context or {}
        full_context = {**self.constants, **context}  # Полный контекст для поиска констант

        if isinstance(value, str) and value.startswith("{") and value.endswith("}"):
            expression = value[1:-1]
            if delay_expressions:
                return value  # Откладываем выполнение выражения
            return self.evaluate_expression(expression, full_context)
        elif isinstance(value, str):
            # Подстановка значений констант внутри строки, если указаны {ключи}
            pattern = re.compile(r"{(\w+)}")
            return pattern.sub(lambda match: str(full_context.get(match.group(1), match.group(0))), value)
        elif isinstance(value, dict):
            # Рекурсивная обработка словарей
            return {k: self.resolve_constants(v, full_context, delay_expressions) for k, v in value.items()}
        elif isinstance(value, list):
            # Рекурсивная обработка списков
            return [self.resolve_constants(item, full_context, delay_expressions) for item in value]
        return value

    def format_value(self, value):
        """Форматирует значение для вывода, обрабатывая строки и списки."""
        if isinstance(value, str):
            return f'"{value}"'
        elif isinstance(value, list):
            formatted_list = ', '.join(f'"{item}"' if isinstance(item, str) else str(item) for item in value)
            return f"<< {formatted_list} >>"
        return value

    def generate_output(self, data, indent=0, context=None):
        """Рекурсивно обрабатывает входные данные и преобразует в конфигурацию."""
        output = "begin\n"
        indent_str = '    ' * indent  # Уровень отступов

        # Создаем локальный контекст на каждом уровне рекурсии
        local_context = copy.deepcopy(context) if context else {}
        local_context.update(self.constants)

        # Первый проход: добавляем простые значения в локальный контекст без вычисления выражений
        for key, value in data.items():
            if not re.match(r"^[A-Za-z_]\w*$", key):
                raise ConfigError(f"Неверное имя ключа: {key}")
            # Сохраняем значение в контексте без вычисления сложных выражений
            resolved_value = self.resolve_constants(value, local_context, delay_expressions=True)
            local_context[key] = resolved_value

        # Второй проход: вычисляем выражения, которые зависят от других переменных
        for key, value in data.items():
            resolved_value = self.resolve_constants(local_context[key], local_context, delay_expressions=False)
            local_context[key] = resolved_value

            # Обработка значений в зависимости от их типа
            if isinstance(resolved_value, dict):
                output += f"{indent_str}    {key} := {self.generate_output(resolved_value, indent + 1, local_context)};\n"
            else:
                formatted_value = self.format_value(resolved_value)
                output += f"{indent_str}    {key} := {formatted_value};\n"

        output += f"{indent_str}end"
        return output
