import numpy as np

'''
Layout of the map:
+-------+
|c     c|
| (x,y) |
|c     c|
+-------+
0 <= x < width
0 <= y < depth
0 <= c < 4   (corner)

+-------+-------+-------+
|1     0|1     0|1     0|
| (0,2) | (1,2) | (2,2) |
|2     3|2     3|2     3|
+-------+-------+-------+
|1     0|1     0|1     0|
| (0,1) | (1,1) | (2,1) |
|2     3|2     3|2     3|
+-------+-------+-------+
|1     0|1     0|1     0|
| (0,0) | (1,0) | (2,0) |
|2     3|2     3|2     3|
+-------+-------+-------+
'''

class Terrain:
    def __init__(self, width, depth):
        self.width = width
        self.depth = depth
        self.vertex_height = np.zeros((width, depth, 4), dtype=np.int8)

    def move_corner(self, x, y, corner, amount):
        if not amount:
            return
        a,b,c,d = np.roll(self.vertex_height[x,y], -corner)
        a += amount
        if amount > 0:
            b = max(b, a-1)
            c = max(c, a-2)
            d = max(d, a-1)
        else:
            b = min(b, a+1)
            c = min(c, a+2)
            d = min(d, a+1)
        self.vertex_height[x,y] = np.roll(np.array([a,b,c,d]), corner)

    def debug(self):
        width = min(self.width, 10)
        for y in range(min(self.depth-1,9),-1,-1):
            print('+' + width*'-------+')
            print('|'
                + '|'.join('%-3d %3d' %
                 (self.vertex_height[x,y,1], self.vertex_height[x,y,0])
                 for x in range(width))
                + '|')
            print('|'
                + '|'.join(' (%d,%d) ' % (x,y) for x in range(width))
                + '|')
            print('|'
                + '|'.join('%-3d %3d' %
                 (self.vertex_height[x,y,2], self.vertex_height[x,y,3])
                 for x in range(width))
                + '|')
        print('+' + width*'-------+')

    def vertex_data(self):
        for x, col in enumerate(self.vertex_height):
            for y, tile in enumerate(col):
                yield x+1, y+1, tile[0]
                yield x, y+1, tile[1]
                yield x, y, tile[2]
                yield x+1, y, tile[3]
    def nb_vertices(self):
        return 4*self.width*self.depth

if __name__ == '__main__':
    t = Terrain(4,3)
    t.debug()
    t.move_corner(2,2,1,4)
    t.move_corner(2,2,0,-1)
    t.debug()
