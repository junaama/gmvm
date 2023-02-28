class Stack:
    
    def __init__(self, max_depth=1024) -> None:
        self.stack = []
        self.max_depth = max_depth

    def push(self, item):
        if len(self.stack) >= self.max_depth:
            raise Exception("Stack overflow")
        self.stack.append(item)

    def pop(self):
        if len(self.stack) == 0:
            raise Exception("Stack underflow")
        return self.stack.pop()
