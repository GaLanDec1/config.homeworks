import pytest
import toml
from config_converter import ConfigConverter, ConfigError

def normalize_whitespace(text):
    """Утилита для удаления лишних пробелов и символов новой строки"""
    return "".join(text.split())

# Пример 1: Простой словарь конфигурации интернет-магазина
def test_ecommerce_config():
    converter = ConfigConverter()
    toml_data = toml.loads("""
    [Product]
    Name = "Laptop"
    Price = 1500
    """)
    expected_output = """
    begin
        Product := begin
            Name := "Laptop";
            Price := 1500;
        end;
    end
    """
    generated_output = converter.generate_output(toml_data)
    assert normalize_whitespace(generated_output) == normalize_whitespace(expected_output)

# Пример 2: Конфигурация логистики
def test_logistics_config():
    converter = ConfigConverter()
    toml_data = toml.loads("""
    [Shipping]
    Warehouse = "Main"
    Routes = ["RouteA", "RouteB", "RouteC"]
    """)
    expected_output = """
    begin
        Shipping := begin
            Warehouse := "Main";
            Routes := << "RouteA", "RouteB", "RouteC" >>;
        end;
    end
    """
    generated_output = converter.generate_output(toml_data)
    assert normalize_whitespace(generated_output) == normalize_whitespace(expected_output)

# Пример 3: Подстановка секретов для разных клиентов
def test_secrets_substitution():
    converter = ConfigConverter(constants={"Secrets": {"AccessToken": "123ABC"}})
    toml_data = toml.loads("""
    WebSecrets = "{Secrets}"
    DesktopSecrets = "{Secrets}"
    """)
    expected_output = """
    begin
        Secrets := begin
            AccessToken := "123ABC";
        end;
        WebSecrets := begin
            AccessToken := "123ABC";
        end;
        DesktopSecrets := begin
            AccessToken := "123ABC";
        end;
    end
    """
    generated_output = converter.generate_output(toml_data)
    assert normalize_whitespace(generated_output) == normalize_whitespace(expected_output)

# Тест вычисления выражений с константами
def test_constant_expression_evaluation():
    converter = ConfigConverter(constants={"PI": 3.1415})
    toml_data = toml.loads("""
    [Circle]
    radius = 10
    circumference = "{PI * radius}"
    """)
    expected_output = """
    begin
        Circle := begin
            radius := 10;
            circumference := 31.415;
        end;
    end
    """
    generated_output = converter.generate_output(toml_data)
    assert normalize_whitespace(generated_output) == normalize_whitespace(expected_output)

# Тест невалидного имени ключа
def test_invalid_key_name():
    converter = ConfigConverter()
    toml_data = toml.loads("""
    ["123InvalidKey"]
    value = 42
    """)
    with pytest.raises(ConfigError, match="Неверное имя ключа"):
        converter.generate_output(toml_data)
