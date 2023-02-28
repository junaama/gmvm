from validation import validate_uint256, validate_uint256,validate_is_bytes, validate_length, validate_lte

class Memory:

    def __init__(self):
        self.memory = bytearray()


    def write(self, offset: int, size: int, value: bytes):
        if size:
            validate_uint256(offset)
            validate_uint256(size)
            validate_is_bytes(value)
            validate_length(value, length=size)
            validate_lte(offset + size, maximum=len(self.memory))

            for index, byte in enumerate(value):
                self.memory[offset + index] = byte

    def read(self, offset, size):
        return self.memory[offset:offset + size]

    def extend(self, offset, size):
        if size == 0:
            return
        extended_size = _ceil32(offset + size)
        if extended_size < len(self.memory):
            return
        size_to_extend = extended_size - len(self.memory)
        self.memory.extend([0] * size_to_extend)
    
    def read_range(self, offset, size):
        if offset < 0:
            raise Exception("Invalid memory access", offset, size)
        return bytes(self.memory[offset:offset + size])

def _ceil32(x):
    return -(-x // 32) * 32

# def _ceilAB(a, b):
#     return -(-a // b) * b
