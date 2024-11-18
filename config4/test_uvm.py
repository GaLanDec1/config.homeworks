# test_uvm.py
import struct
import os
import yaml
import pytest
from assembler import assemble
from uvm import UVM


@pytest.fixture
@pytest.fixture
def setup_files():
    asm_file = "test_program.asm"
    bin_file = "test_program.bin"
    log_file = "test_program_log.yaml"
    result_file = "test_result.yaml"

    # Тестовая ассемблерная программа
    test_program = """
    LOAD_CONST 0x01 0  # Адрес начала первого вектора
    LOAD_CONST 0x02 5  # Адрес начала второго вектора
    LOAD_CONST 0x03 10 # Адрес для результата
    LOAD_CONST 0x04 5  # Длина векторов

    LOAD_CONST 0x05 0
    LOOP_START:
    READ_MEM 0x06 [0x01+0x05]
    READ_MEM 0x07 [0x02+0x05]
    BITWISE_SHIFT_RIGHT 0x08 [0x06+0x07]
    WRITE_MEM 0x03 [0x08+0x05]
    INC 0x05
    CMP 0x05 0x04
    JLT LOOP_START

    HALT
    """

    with open(asm_file, 'w') as f:
        f.write(test_program)

    yield asm_file, bin_file, log_file, result_file

    for file in [asm_file, bin_file, log_file, result_file]:
        if os.path.exists(file):
            os.remove(file)



def test_assemble(setup_files):
    asm_file, bin_file, log_file, _ = setup_files

    # Ассемблируем программу
    assemble(asm_file, bin_file, log_file)

    # Проверка бинарного файла
    with open(bin_file, 'rb') as f:
        binary_content = f.read()
        print(f"Бинарное содержимое: {binary_content}")  # добавляем отладочный вывод
        print(f"Длина бинарного файла: {len(binary_content)} байт")  # добавляем отладочный вывод
        assert len(binary_content) == 20, "Бинарный файл должен содержать 20 байт для 4 команд"

        # Ожидаемые байты для каждой команды
        expected_instructions = [
            struct.pack('<BIB', 0x0C, 34, 0),
            struct.pack('<BIB', 0xB6, 570, 0),
            struct.pack('<BIB', 0x71, 878, 0),
            struct.pack('<BIB', 0xC5, 725, 0)
        ]
        for i, expected in enumerate(expected_instructions):
            assert binary_content[i * 5:(i + 1) * 5] == expected, f"Инструкция {i + 1} не совпадает с ожидаемой"

    # Проверка YAML лога
    with open(log_file, 'r') as f:
        log_content = yaml.safe_load(f)
        assert len(log_content['instructions']) == 4, "Лог-файл должен содержать 4 инструкции"

        # Проверка отдельных значений полей
        assert log_content['instructions'][0]['fields']['A'] == 0x0C
        assert log_content['instructions'][1]['fields']['B'] == 570


def test_interpreter_execution(setup_files):
    _, bin_file, _, result_file = setup_files

    # Запись тестовых команд в бинарный файл
    binary_content = [
        struct.pack('<BBH', 0x0C, 0, 34),
        struct.pack('<BBH', 0xB6, 0, 10),
        struct.pack('<BBH', 0x71, 0, 15),
        struct.pack('<BBH', 0xC5, 0, 3)
    ]
    with open(bin_file, 'wb') as f:
        f.write(b''.join(binary_content))

    # Инициализация и запуск интерпретатора
    uvm = UVM()
    uvm.run(bin_file, result_file, (0, 20))  # Теперь передаем 3 аргумента

    # Проверка содержимого файла результата
    with open(result_file, 'r') as f:
        result_content = yaml.safe_load(f)
        assert 'memory' in result_content
        print(f"[DEBUG] Interpreter result content: {result_content}")




def test_uvm_operations():
    # Тест для отдельных операций виртуальной машины
    uvm = UVM()

    # Тест команды LOAD_CONST
    uvm.load_const(123)
    assert uvm.stack[-1] == 123, "LOAD_CONST должен загрузить значение в стек"

    # Тест команды WRITE_MEM
    uvm.stack.append(10)  # Адрес
    uvm.stack.append(200)  # Значение
    uvm.write_mem(0)  # Запись по адресу 10
    assert uvm.memory[10] == 200, "WRITE_MEM должен записать значение в память по адресу"

    # Тест команды READ_MEM
    uvm.stack.append(10)  # Адрес
    uvm.read_mem(0)  # Чтение из адреса 10
    assert uvm.stack[-1] == 200, "READ_MEM должен прочитать значение из памяти в стек"

    # Тест команды BITWISE_SHIFT_RIGHT
    uvm.stack.append(5)  # Адрес
    uvm.memory[5] = 2  # Операнд для сдвига
    uvm.stack.append(8)  # Значение для сдвига вправо
    uvm.bitwise_shift_right(0)
    assert uvm.stack[-1] == 2, "BITWISE_SHIFT_RIGHT должен сдвинуть значение"
