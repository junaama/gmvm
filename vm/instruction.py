from execution_context import ExecutionContext
from opcode_values import *
from constants import MAX_UINT256
from vm.memory import _ceil32

class Instruction:

    def __init__(self, opcode: int, name: str):
        self.opcode = opcode
        self.name = name

    def execute(self, context: ExecutionContext) -> None:
        raise Exception("Not implemented")

INSTRUCTIONS = []
INSTRUCTIONS_BY_OPCODE = {}

def add_instruction(opcode: int, name: str, execute_fn: callable):
    instruction = Instruction(opcode, name)
    instruction.execute = execute_fn
    INSTRUCTIONS.append(instruction)
    INSTRUCTIONS_BY_OPCODE[opcode] = instruction
    return instruction


def decode_opcode(context: ExecutionContext):
    if context.pc < 0:
        raise Exception("Program counter is invalid")
    if context.pc >= len(context.code):
        return STOP
    opcode = context.read_code(1)
    instruction = INSTRUCTIONS_BY_OPCODE.get(opcode)
    if instruction is None:
        raise Exception(f"Invalid opcode: {opcode}")
    return instruction

def is_valid_opcode(opcode: int) -> bool:
    return opcode in INSTRUCTIONS_BY_OPCODE

def unsigned_to_signed(value: int) -> int:
    if value <= 2**255 - 1:
        return value
    else:
        return value - 2**256


def signed_to_unsigned(value: int) -> int:
    if value < 0:
        return value + 2**256
    else:
        return value

# from opcodes in opcode_values call add_instruction for each

ADD = add_instruction(ADD, "ADD", lambda ctx: ctx.stack.push((ctx.stack.pop() + ctx.stack.pop()) & MAX_UINT256))
SUB = add_instruction(SUB, "SUB", lambda ctx: ctx.stack.push((ctx.stack.pop() - ctx.stack.pop()) & MAX_UINT256))
MUL = add_instruction(MUL, "MUL", lambda ctx: ctx.stack.push((ctx.stack.pop() * ctx.stack.pop()) & MAX_UINT256))

def div(ctx):
    num = ctx.stack.pop()
    denom = ctx.stack.pop()
    if denom == 0:
        result = 0
    else:
        result = (num // denom) & MAX_UINT256
    ctx.stack.push(result)

DIV = add_instruction(DIV, "DIV", div)
LT = add_instruction(LT, "LT", lambda ctx: ctx.stack.push(1 if ctx.stack.pop() < ctx.stack.pop() else 0))
GT = add_instruction(GT, "GT", lambda ctx: ctx.stack.push(1 if ctx.stack.pop() > ctx.stack.pop() else 0))
EQ = add_instruction(EQ, "EQ", lambda ctx: ctx.stack.push(1 if ctx.stack.pop() == ctx.stack.pop() else 0))
OR = add_instruction(OR, "OR", lambda ctx: ctx.stack.push(ctx.stack.pop() | ctx.stack.pop()))
XOR = add_instruction(XOR, "XOR", lambda ctx: ctx.stack.push(ctx.stack.pop() ^ ctx.stack.pop()))
NOT = add_instruction(NOT, "NOT", lambda ctx: ctx.stack.push(MAX_UINT256 - ctx.stack.pop()))
AND = add_instruction(AND, "AND", lambda ctx: ctx.stack.push(ctx.stack.pop() & ctx.stack.pop()))
ISZERO = add_instruction(ISZERO, "ISZERO", lambda ctx: ctx.stack.push(1 if ctx.stack.pop() == 0 else 0))
def sdiv(ctx):
    num, denom = map(unsigned_to_signed, (ctx.stack.pop(), ctx.stack.pop()))
    sign = -1 if num * denom < 0 else 1
    if denom == 0:
        res = 0
    else:
        res = (sign * (abs(num) // abs(denom)))
    ctx.stack.push(signed_to_unsigned(res))

def slt(ctx):
    l,r = map(unsigned_to_signed, (ctx.stack.pop(), ctx.stack.pop()))
    ctx.stack.push(1 if l < r else 0)

SLT = add_instruction(SLT, "SLT", slt)
SDIV = add_instruction(SDIV, "SDIV", sdiv)

PUSH1 = add_instruction(PUSH1, "PUSH1", lambda ctx: ctx.stack.push(ctx.read_code(1)))
PUSH2 = add_instruction(PUSH2, "PUSH2", lambda ctx: ctx.stack.push(ctx.read_code(2)))
PUSH3 = add_instruction(PUSH3, "PUSH3", lambda ctx: ctx.stack.push(ctx.read_code(3)))
PUSH4 = add_instruction(PUSH4, "PUSH4", lambda ctx: ctx.stack.push(ctx.read_code(4)))
PUSH5 = add_instruction(PUSH5, "PUSH5", lambda ctx: ctx.stack.push(ctx.read_code(5)))
PUSH6 = add_instruction(PUSH6, "PUSH6", lambda ctx: ctx.stack.push(ctx.read_code(6)))
PUSH18 = add_instruction(PUSH18, "PUSH18", lambda ctx: ctx.stack.push(ctx.read_code(18)))

POP = add_instruction(POP, "POP", lambda ctx: ctx.stack.pop())
STOP = add_instruction(STOP, "STOP", lambda ctx: ctx.stop())

DAMAGE = add_instruction(DAMAGE, "DAMAGE", lambda ctx: ctx.state.update({"damage": ctx.read_code(1)}))
DEFENSE = add_instruction(DEFENSE, "DEFENSE", lambda ctx: ctx.state.update({"defense": ctx.stack.pop()}))
SPEEDBOOST = add_instruction(SPEEDBOOST, "SPEEDBOOST", lambda ctx: ctx.state.update({"speedboost": ctx.stack.pop()}))

def mstore8(ctx):
    offset = ctx.stack.pop()
    value = bytes(ctx.stack.pop())

    padded_value = value.rjust(1, b'\x00')
    normalized_value = padded_value[-1:]
    ctx.memory.extend(offset, 1)
    ctx.memory.write(offset, 1, normalized_value)

MSTORE8 = add_instruction(MSTORE8, "MSTORE8", mstore8)

RETURN = add_instruction(RETURN, "RETURN", lambda ctx: ctx.return_data(ctx.stack.pop(), ctx.stack.pop()))

def jump(ctx) -> None:
    jdest = ctx.stack.pop()
    ctx.pc = jdest
    nextdest = ctx.peek_code()

    if nextdest != 91:
        raise Exception("Invalid jump destination", nextdest,)
    if not is_valid_opcode(jdest):
        raise Exception("Invalid jump instruction", jdest)
    
JUMP = add_instruction(JUMP, "JUMP", jump)

def jumpi(ctx) -> None:
    jdest = ctx.stack.pop()
    val = ctx.stack.pop()
    if val:
        ctx.pc = jdest
        nextdest = ctx.peek_code()
        if nextdest != 91:
            raise Exception("Invalid jump destination", nextdest)
        if not is_valid_opcode(jdest):
            raise Exception("Invalid jump instruction", jdest)

JUMPI = add_instruction(JUMPI, "JUMPI", jumpi)

def jumpdest(ctx) -> None:
    pass

JUMPDEST = add_instruction(JUMPDEST, "JUMPDEST", jumpdest)

def pc(ctx): 
    max_pc = max(ctx.pc - 1, 0)
    ctx.stack.push(max_pc)

PC = add_instruction(PC, "PC", pc)

DUP1 = add_instruction(DUP1, "DUP1", lambda ctx: ctx.stack.dup(1))
DUP2 = add_instruction(DUP2, "DUP2", lambda ctx: ctx.stack.dup(2))
DUP3 = add_instruction(DUP3, "DUP3", lambda ctx: ctx.stack.dup(3))
DUP4 = add_instruction(DUP4, "DUP4", lambda ctx: ctx.stack.dup(4))
DUP5 = add_instruction(DUP5, "DUP5", lambda ctx: ctx.stack.dup(5))
DUP6 = add_instruction(DUP6, "DUP6", lambda ctx: ctx.stack.dup(6))
DUP7 = add_instruction(DUP7, "DUP7", lambda ctx: ctx.stack.dup(7))
DUP8 = add_instruction(DUP8, "DUP8", lambda ctx: ctx.stack.dup(8))

SWAP1 = add_instruction(SWAP1, "SWAP1", lambda ctx: ctx.stack.swap(1))
SWAP2 = add_instruction(SWAP2, "SWAP2", lambda ctx: ctx.stack.swap(2))
SWAP3 = add_instruction(SWAP3, "SWAP3", lambda ctx: ctx.stack.swap(3))
SWAP4 = add_instruction(SWAP4, "SWAP4", lambda ctx: ctx.stack.swap(4))
SWAP5 = add_instruction(SWAP5, "SWAP5", lambda ctx: ctx.stack.swap(5))
SWAP6 = add_instruction(SWAP6, "SWAP6", lambda ctx: ctx.stack.swap(6))
SWAP7 = add_instruction(SWAP7, "SWAP7", lambda ctx: ctx.stack.swap(7))
SWAP8 = add_instruction(SWAP8, "SWAP8", lambda ctx: ctx.stack.swap(8))

def cdl(ctx):
    offset = ctx.stack.pop()
    val = ctx.message.data[offset:offset+32]
    padded_val = val.ljust(32, b'\x00')
    normalized_val = padded_val.lstrip(b'\x00')
    ctx.stack.push_bytes(normalized_val)

CALLDATALOAD = add_instruction(CALLDATALOAD, "CALLDATALOAD", cdl)
CALLDATASIZE = add_instruction(CALLDATASIZE, "CALLDATASIZE", lambda ctx: ctx.stack.push(len(ctx.message.data)))

def cdc(ctx):
    (memory_offset, message_offset, size) = ctx.stack.pop(), ctx.stack.pop(), ctx.stack.pop()
    ctx.memory.extend(memory_offset, size)
    val = ctx.message.data[message_offset: message_offset + size]
    padded_val = val.ljust(size, b'\x00')
    ctx.memory.write(memory_offset, size, padded_val)

CALLDATACOPY = add_instruction(CALLDATACOPY, "CALLDATACOPY", cdc )