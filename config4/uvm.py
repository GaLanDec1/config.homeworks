# uvm.py
class UVM:
    def __init__(self, memory_size=1024):
        # Инициализация памяти и стека
        self.stack = []
        self.memory = [0] * memory_size

    def load_const(self, value):
        """Загрузка константы в стек."""
        self.stack.append(value)

    def read_mem(self, offset):
        """Чтение значения из памяти с учетом смещения."""
        address = self.stack.pop() + offset
        self.stack.append(self.memory[address])

    def write_mem(self, offset):
        """Запись значения в память с учетом смещения."""
        value = self.stack.pop()
        address = self.stack.pop() + offset
        self.memory[address] = value

    def bitwise_shift_right(self, shift_amount):
        # Проверим, есть ли как минимум два элемента в стеке
        if len(self.stack) < 2:
            raise RuntimeError("Недостаточно элементов в стеке для выполнения операции BITWISE_SHIFT_RIGHT")

        value = self.stack.pop()
        addr = self.stack.pop()

        # Чтение значения из памяти
        mem_value = self.memory[addr]

        # Циклический сдвиг вправо
        shift_amount = shift_amount % 8  # ограничение сдвига в пределах 8 бит
        result = (mem_value >> shift_amount) | ((mem_value & ((1 << shift_amount) - 1)) << (8 - shift_amount))

        # Помещаем результат обратно в стек
        self.stack.append(result)

    def run(self, instructions):
        """Выполнение инструкций."""
        for instr in instructions:
            opcode = instr[0]
            b_value = int.from_bytes(instr[1:4], byteorder='little')

            if opcode == 12:  # LOAD_CONST
                self.load_const(b_value)
            elif opcode == 182:  # READ_MEM
                self.read_mem(b_value)
            elif opcode == 113:  # WRITE_MEM
                self.write_mem(b_value)
            elif opcode == 197:  # BITWISE_SHIFT_RIGHT
                self.bitwise_shift_right(b_value)
