import struct
import yaml
import sys

def parse_instruction(line):
    """Разбор строки команды и создание бинарной инструкции."""
    parts = line.split()
    if len(parts) < 3:
        raise ValueError(f"Ошибка: строка '{line}' имеет недостаточно элементов.")

    cmd_type = parts[0]
    a_value = int(parts[1], 16)  # Преобразуем поле A в 16-ричное число
    b_value = int(parts[2])  # Преобразуем поле B в десятичное число

    if cmd_type == "LOAD_CONST":
        a = a_value
    elif cmd_type == "READ_MEM":
        a = 182
    elif cmd_type == "WRITE_MEM":
        a = 113
    elif cmd_type == "BITWISE_SHIFT_RIGHT":
        a = 197
    else:
        raise ValueError(f"Неизвестная команда '{cmd_type}'")

    # Проверяем диапазон значений A
    if not (0 <= a <= 255):
        raise ValueError(f"Поле 'A' имеет недопустимое значение: {a}. Ожидалось значение в диапазоне 0–255.")

    # Ограничиваем размер B 2 байт
    b = b_value & 0xFFFF

    # Упаковываем инструкцию
    instruction = struct.pack('<BH', a, b)
    print(f"Собрана инструкция: {instruction.hex()}")  # Отладочный вывод
    return cmd_type, instruction

def assemble(asm_file, bin_file, log_file):
    """Сборка программы из ассемблерного файла в бинарный файл."""
    instructions = []
    log_data = {
        'instructions': []
    }

    # Чтение ассемблерного файла
    with open(asm_file, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue  # Пропускаем пустые строки

            try:
                cmd_type, instruction = parse_instruction(line)
                instructions.append(instruction)

                # Логируем инструкцию
                log_data['instructions'].append({
                    'opcode': cmd_type,
                    'fields': {
                        'A': struct.unpack('<B', instruction[0:1])[0],
                        'B': struct.unpack('<H', instruction[1:3])[0]  # Читаем только 2 байта поля B
                    }
                })

            except ValueError as e:
                print(e)  # Отображение ошибки для отладки

    # Запись инструкций в бинарный файл
    with open(bin_file, 'wb') as f:
        for instruction in instructions:
            f.write(instruction)

    print(f"Количество инструкций: {len(instructions)}")
    print(f"Длина бинарного файла: {len(instructions) * 3} байт")  # 3 байта на инструкцию

    # Запись лог-файла
    with open(log_file, 'w') as f:
        yaml.dump(log_data, f)

if __name__ == "__main__":
    # Проверка аргументов командной строки
    if len(sys.argv) != 4:
        print("Usage: python assembler.py <input_file> <output_file> <log_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    log_file = sys.argv[3]

    assemble(input_file, output_file, log_file)
