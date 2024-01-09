class Cached_unit():
    def __init__(self):
        self.data=None
    def insert_data(self, data):
        self.data = data
    def get_data(self):
        return self.data