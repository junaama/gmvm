from stack import Stack
from storage import Storage
from memory import Memory
from opcode_values import STOP
class ExecutionContext:

    def __init__(self, code=bytes(), pc=0, stack=Stack(), memory=Memory(), storage=Storage()):
        self.code = code
        self.pc = pc
        self.stack = stack
        self.memory = memory
        self.storage = storage
        self.state = {}
        self.stopped = False
        self.returndata = bytes()

    def stop(self):
        self.stopped = True
    
    def read_code(self, bytes):
        value = int.from_bytes(self.code[self.pc : self.pc + bytes], "big")
        self.pc += bytes
        return value

    def peek_code(self):
        if self.pc < len(self.code):
            return self.code[self.pc]
        else:
            return STOP
    
    def return_data(self, offset, size):
        self.stopped = True
        self.returndata = self.memory.read_range(offset=offset, size=size)




