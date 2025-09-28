class Tile:
    position: tuple
    description: str #Just a basic string
    def __init__(self, description: str):
        self.description = description