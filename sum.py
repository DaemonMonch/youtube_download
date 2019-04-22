import threading
class Sum:
    def __init__(self):
        self.sum = 0
        self.lock = threading.RLock()
    def incr(self,count):
        with self.lock:
            self.sum += count
    def get(self):
        return self.sum            