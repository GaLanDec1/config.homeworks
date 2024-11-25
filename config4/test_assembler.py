import pytest
import struct
from assembler import parse_instruction

def test_load_const():
    cmd_type, instruction = parse_instruction("LOAD_CONST 0x0C 34")
    assert cmd_type == "LOAD_CONST"
    assert instruction == bytes([0x0C, 0x22, 0x00])

def test_read_mem():
    cmd_type, instruction = parse_instruction("READ_MEM 0xB6 570")
    assert cmd_type == "READ_MEM"
    assert instruction == bytes([0xB6, 0x3A, 0x02])

def test_write_mem():
    cmd_type, instruction = parse_instruction("WRITE_MEM 0x71 878")
    assert cmd_type == "WRITE_MEM"
    assert instruction == bytes([0x71, 0x6E, 0x03])

def test_bitwise_shift_right():
    cmd_type, instruction = parse_instruction("BITWISE_SHIFT_RIGHT 0xC5 725")
    assert cmd_type == "BITWISE_SHIFT_RIGHT"
    assert instruction == bytes([0xC5, 0xD5, 0x02])

def test_invalid_command():
    with pytest.raises(ValueError):
        parse_instruction("INVALID_CMD 0x00 1234")

def test_invalid_a_value():
    with pytest.raises(ValueError):
        parse_instruction("LOAD_CONST 0x100 1234")

def test_invalid_line_format():
    with pytest.raises(ValueError):
        parse_instruction("LOAD_CONST 0x12")

if __name__ == '__main__':
    pytest.main()
