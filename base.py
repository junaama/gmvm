# temp context runner

from execution_context import ExecutionContext
from instruction import decode_opcode

def run(code: bytes) -> None:

    context = ExecutionContext(code=code)

    while not context.stopped:
        pc_b = context.pc
        instruction = decode_opcode(context)
        instruction.execute(context)

        print(f"{pc_b:04x} {instruction.name} {context.stack}")


