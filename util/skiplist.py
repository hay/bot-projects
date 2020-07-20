from pathlib import Path

class Skiplist:
    def __init__(self, path):
        self.path = path
        self.load()

    def add(self, item):
        if self.has(item):
            print(f"Skiplist already has {item}")
            return

        with open(self.path, "a") as f:
            f.write(item + "\n")
            print(f"Added {item} to skiplist")

        # Reload list
        self.load()

    def has(self, item):
        return item in self.list

    def load(self):
        # Do we have this file? If not, create it
        if not Path(self.path).exists():
            Path(self.path).touch()

        with open(self.path) as f:
            self.list = f.read().splitlines()