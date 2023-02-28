class Memory:

    def __init__(self):
        self.memory = []

    def write(self, item):
        self.memory.append(item)

    def read(self):
        return self.memory.pop()

    def extend(self, size):
        self.memory.extend([0] * size)
    
