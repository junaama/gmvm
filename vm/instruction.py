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