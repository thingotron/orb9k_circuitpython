import gc
from observable import Observer

class MemObserver(Observer):

    def __init__(self):
        pass

    def receive(self, msg):
        print("Mem: {0}".format(gc.mem_free(), ))
