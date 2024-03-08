import threading


class CustomEvent(threading.Event):
    def __init__(self, value = None):
        super().__init__()
        self.value = value

    def set_value(self, value):
        self.value = value
        self.set()

    def clear_value(self):
        self.value = None
        self.clear()

    def wait_for_value(self, timeout=None):
        self.wait(timeout)
        return self.value