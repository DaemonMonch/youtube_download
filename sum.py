import threading
class Sum:
    def __init__(self,total):
        self.sum = 0
        self.total = total
        self.lock = threading.RLock()
    def incr(self,count):
        with self.lock:
            self.sum += count
    def get(self):
        return self.sum   
    def get_ratio(self):
        with self.lock:
            return self.sum * 100 / self.total
