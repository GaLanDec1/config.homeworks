import struct
import yaml

class UVM:
    def __init__(self):
        self.stack = []
        self.memory = {}

    def load_binary(self, bin_file):
        """Загружает команды из бинарного файла."""
        instructions = []
        with open(bin_file, 'rb') as f:
            while True:
                bytes_read = f.read(5)
                if len(bytes_read) < 5:
                    break
                a, _, b = struct.unpack('<BBH', bytes_read)
                instructions.append((a, b))
        return instructions

    def execute_instruction(self, a, b):
        """Выполняет команду на основе кода A и значения B."""
        if a == 0x0C:  # LOAD_CONST
            self.stack.append(b)
        elif a == 182:  # READ_MEM
            address = self.stack.pop() + b
            value = self.memory.get(address, 0)
            self.stack.append(value)
        elif a == 113:  # WRITE_MEM
            address = self.stack.pop() + b
            value = self.stack.pop()
            self.memory[address] = value
        elif a == 197:  # BITWISE_SHIFT_RIGHT
            address = self.stack.pop() + b
            operand1 = self.stack.pop()
            operand2 = self.memory.get(address, 0)
            result = (operand1 >> (operand2 % 32)) | (operand1 << (32 - (operand2 % 32)))
            self.stack.append(result)
        else:
            raise ValueError(f"Неизвестная команда A={a}")

    def run(self, bin_file, result_file, memory_range):
        """Загружает команды, выполняет их и записывает результат в файл."""
        instructions = self.load_binary(bin_file)
        for a, b in instructions:
            self.execute_instruction(a, b)

        # Записываем память в указанном диапазоне в YAML файл
        start, end = memory_range
        memory_content = {addr: val for addr, val in self.memory.items() if start <= addr < end}
        result = {'memory': memory_content}

        with open(result_file, 'w') as f:
            yaml.dump(result, f)
