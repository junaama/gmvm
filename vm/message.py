class Message:

    def __init__(self, data=bytes()):
        self.data = data
    
    def __len__(self):
        return len(self.data)
    
    
