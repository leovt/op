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
        u = [1,0,0,1]
        v = [1,1,0,0]
        for x, col in enumerate(self.vertex_height):
            for y, tile in enumerate(col):
                shape, level, corner = tile_shape(list(tile))
                for c in [corner-1, corner, corner+1]:
                    yield x, y, tile[c%4], c%4, u[c%4], v[c%4], (0.0, 0.5, 0.0, 1.0), shading.get(shape, [(0.8,0.8)]*4)[corner][0]
                for c in [corner+1, corner+2, corner+3]:
                    yield x, y, tile[c%4], c%4, u[c%4], v[c%4], (0.0, 0.5, 0.0, 1.0), shading.get(shape, [(0.8,0.8)]*4)[corner][1]

                if x == 0:
                    neighbour = (-10,-10,-10,-10)
                else:
                    neighbour = self.vertex_height[x-1, y]
                yield x, y, tile[2], None, u[2], v[2], (0.55, 0.38, 0.2, 1.0), 0.7
                yield x, y, tile[1], None, u[1], v[1], (0.55, 0.38, 0.2, 1.0), 0.7
                yield x-1, y, neighbour[0], None, u[0], v[0], (0.55, 0.38, 0.2, 1.0), 0.7
                yield x-1, y, neighbour[0], None, u[0], v[0], (0.55, 0.38, 0.2, 1.0), 0.7
                yield x-1, y, neighbour[3], None, u[3], v[3], (0.55, 0.38, 0.2, 1.0), 0.7
                yield x, y, tile[2], None, u[2], v[2], (0.55, 0.38, 0.2, 1.0), 0.7

                if y == 0:
                    neighbour = (-10,-10,-10,-10)
                else:
                    neighbour = self.vertex_height[x, y-1]
                yield x, y, tile[3], None, u[3], v[3], (0.55, 0.38, 0.2, 1.0), 0.9
                yield x, y, tile[2], None, u[2], v[2], (0.55, 0.38, 0.2, 1.0), 0.9
                yield x, y-1, neighbour[1], None, u[1], v[1], (0.55, 0.38, 0.2, 1.0), 0.9
                yield x, y-1, neighbour[1], None, u[1], v[1], (0.55, 0.38, 0.2, 1.0), 0.9
                yield x, y-1, neighbour[0], None, u[0], v[0], (0.55, 0.38, 0.2, 1.0), 0.9
                yield x, y, tile[3], None, u[3], v[3], (0.55, 0.38, 0.2, 1.0), 0.9



    def nb_vertices(self):
        return 18*self.width*self.depth

TILE_FLAT = 0     # 0000
TILE_ONE_UP = 1   # 1000
TILE_ONE_DOWN = 2 # 0111
TILE_PARALLEL = 3 # 1100
TILE_STEEP = 4    # 0121
TILE_FOLD = 5     # 1010

B = [.65, .60, .70, .75, .95, 1.0, .90, .85]
shading = {
    TILE_FLAT: [(0.8,0.8)]*4,
    TILE_ONE_UP: [(B[2*k-4], 0.8) for k in range(4)],
    TILE_ONE_DOWN: [(B[2*k], 0.8) for k in range(4)],
    TILE_PARALLEL: [(B[2*k+1], B[2*k+1]) for k in range(4)],
    TILE_STEEP: [(B[2*k], B[2*k]) for k in range(4)],
    TILE_FOLD: [(B[2*k-4], B[2*k]) for k in range(4)]
}

def tile_shape(tile):
    a,b,c,d = tile
    M = max(a,b,c,d)
    m = min(a,b,c,d)
    if m==M:
        return TILE_FLAT, a, 0
    if m==M-2:
        i = tile.index(m)
        assert tile[(i+2)%4] == M
        return TILE_STEEP, m+1, i
    assert m==M-1
    n = tile.count(m)
    if n==1:
        return TILE_ONE_DOWN, M, tile.index(m)
    if n==3:
        return TILE_ONE_UP, m, tile.index(M)
    assert n==2
    i = tile.index(m)
    if tile[(i+1)%4] == m:
        return TILE_PARALLEL, m, i
    if tile[(i-1)%4] == m:
        return TILE_PARALLEL, m, (i-1)%4
    return TILE_FOLD, m, i+1

if __name__ == '__main__':
    t = Terrain(4,3)
    t.debug()
    t.move_corner(2,2,1,4)
    t.move_corner(2,2,0,-1)
    t.debug()
