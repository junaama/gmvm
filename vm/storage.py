class Storage:

    def __init__(self):
        self.storage = {}

    def store(self, key, value):
        if key not in self.storage:
            self.storage[key] = value
        else:
            raise Exception("Key already exists")
    
    def load(self, key):
        if key in self.storage:
            return self.storage[key]
        else:
            raise Exception("Key does not exist")
