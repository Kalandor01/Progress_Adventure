

class Tile:
    def __init__(self, x:int, y:int, content):
        x = int(x)
        y = int(y)
        if x > 9:
            x = 9
        if x < 0:
            x = 0
        if y > 9:
            y = 9
        if y < 0:
            y = 0
        self.x = x
        self.y = y
        self.content = content
        


class Chunk:
    # 10 x 10
    def __init__(self, base_x:int, base_y:int, tiles:list[Tile|None]=None):
        self.base_x = int(base_x)
        self.base_y = int(base_y)
        self.tiles = []
        for tile in tiles:
            self.tiles.append(tile)
    

    def to_json(self):
        chunk_json = {}