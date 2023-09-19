from threading import Thread

class Listener(Thread):
    def __init__(self, target: callable = None, name: str = "listener"):
        self.alive: bool = True
        self.func: callable = target
        
        Thread.__init__(self, name = name, daemon = True)
        # daemon = True is very important! makes the thread stop when the program stops.
    
    def run(self):
        try:
            while self.alive:
                self.func()
        except:
            print("Listener thread encountered exception.")
            self.close()
    
    def close(self):
        self.alive = False