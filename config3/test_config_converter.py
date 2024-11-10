import pytest
from config_converter import ConfigConverter, ConfigError

def normalize_whitespace(text):
    """Утилита для удаления лишних пробелов и символов новой строки"""
    return "".join(text.split())

def test_simple_dict_conversion():
    converter = ConfigConverter()
    toml_data = {
        "Item": {
            "Name": "Widget",
            "Price": 25
        }
    }
    expected_output = """
    begin
        Item := begin
            Name := "Widget";
            Price := 25;
        end;
    end
    """
    generated_output = converter.generate_output(toml_data)
    assert normalize_whitespace(generated_output) == normalize_whitespace(expected_output)
def test_array_conversion():
    converter = ConfigConverter()
    toml_data = {
        "items": [1, 2, 3, 4]
    }
    expected_output = "begin items := << 1, 2, 3, 4 >>; end"
    assert converter.generate_output(toml_data).strip() == expected_output.strip()

def test_nested_dict_conversion():
    converter = ConfigConverter()
    toml_data = {
        "Order": {
            "ID": 1001,
            "Details": {
                "Product": "Gadget",
                "Quantity": 10
            }
        }
    }
    expected_output = """
    begin
        Order := begin
            ID := 1001;
            Details := begin
                Product := "Gadget";
                Quantity := 10;
            end;
        end;
    end
    """
    generated_output = converter.generate_output(toml_data)
    assert normalize_whitespace(generated_output) == normalize_whitespace(expected_output)

def test_constants():
    converter = ConfigConverter(constants={"PI": 3.14})
    toml_data = {
        "Circle": {
            "radius": 10,
            "area": "{PI}"
        }
    }
    expected_output = "begin Circle := begin radius := 10; area := 3.14; end; end"
    assert converter.generate_output(toml_data).strip() == expected_output.strip()

def test_invalid_key_name():
    converter = ConfigConverter()
    toml_data = {
        "123InvalidKey": {
            "value": 42
        }
    }
    with pytest.raises(ConfigError, match="Неверное имя ключа"):
        converter.generate_output(toml_data)
