from typing import List, Tuple, Union
class Stack:
    
    def __init__(self, max_depth=1024) -> None:
        self.stack: List[Tuple[type, Union[int, bytes]]] = []
        self.max_depth = max_depth
        self._pop = self.stack.pop
    
    def __len__(self) -> int:
        return len(self.stack)

    def push(self, item):
        if len(self.stack) >= self.max_depth:
            raise Exception("Stack overflow")
        self.stack.append(item)

    def pop(self):
        if len(self.stack) == 0:
            raise Exception("Stack underflow")
        return self.stack.pop()
    
    def pop_bytes(self):
        if not self.stack:
            raise Exception("Stack underflow")

        val_type, popped_val = self._pop() 
        if val_type is bytes:
            return popped_val
        elif val_type is int:
            return int_to_big_endian(popped_val) 
        else:
            raise Exception("Invalid type")

    def peek(self):
        if len(self.stack) == 0:
            raise Exception("Stack underflow")
        return self.stack[-1]

    def swap(self, offset):
        idx = -1 * offset - 1
        self.stack[-1], self.stack[idx] = self.stack[idx], self.stack[-1]

    def dup(self, offset):
        if len(self.stack) > 1023:
            raise Exception("Stack overflow")
        idx = -1 * offset
        self.stack.append(self.stack[idx])

def int_to_big_endian(value) -> bytes:
    return value.to_bytes((value.bit_length() + 7) // 8, 'big')

def big_endian_to_int(value):
    return int.from_bytes(value, 'big')