from execution_context import ExecutionContext
from opcode_values import *
from constants import MAX_UINT256

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

PUSH1 = add_instruction(PUSH1, "PUSH1", lambda ctx: ctx.stack.push(ctx.read_code(1)))
PUSH2 = add_instruction(PUSH2, "PUSH2", lambda ctx: ctx.stack.push(ctx.read_code(2)))

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