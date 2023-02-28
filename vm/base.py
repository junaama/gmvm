#!/usr/bin/env python3

from execution_context import ExecutionContext
from instruction import decode_opcode
import sys

def run(code: bytes) -> None:

    context = ExecutionContext(code=code)

    while not context.stopped:
        pc_b = context.pc
        instruction = decode_opcode(context)
        instruction.execute(context)

        print(f"{pc_b:04x} {instruction.name}")
        print(f"stack, {context.stack.stack}")
        print(f"state, {context.state}")
        print(f"memory, {context.memory.memory}")
    print(f"returndata, 0x{context.returndata.hex()}")


def main():
    if len(sys.argv) != 2:
        print("Usage: {} <hexdata>".format(sys.argv[0]))
        sys.exit(1)
    
    data = sys.argv[1]
    run(bytes.fromhex(data))

if __name__ == "__main__":
    main()