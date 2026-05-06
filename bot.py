import subprocess
import time
import sys
ROTATIONS = [
    # L
    [
        [[0,0],[0,1],[0,2],[1,2]],
        [[0,0],[1,0],[2,0],[0,1]],
        [[0,0],[1,0],[1,1],[1,2]],
        [[0,1],[1,1],[2,1],[2,0]],
    ],
    # J
    [
        [[1,0],[1,1],[1,2],[0,2]],
        [[0,0],[0,1],[1,1],[2,1]],
        [[0,0],[1,0],[0,1],[0,2]],
        [[0,0],[1,0],[2,0],[2,1]],
    ],
    # T
    [
        [[1,0],[0,1],[1,1],[2,1]],
        [[0,0],[0,1],[1,1],[0,2]],
        [[0,0],[1,0],[2,0],[1,1]],
        [[1,0],[0,1],[1,1],[1,2]],
    ],
    # S
    [
        [[0,1],[1,0],[1,1],[2,0]],
        [[0,0],[0,1],[1,1],[1,2]],
        [[0,1],[1,0],[1,1],[2,0]],
        [[0,0],[0,1],[1,1],[1,2]],
    ],
    # Z
    [
        [[0,0],[1,0],[1,1],[2,1]],
        [[1,0],[0,1],[1,1],[0,2]],
        [[0,0],[1,0],[1,1],[2,1]],
        [[1,0],[0,1],[1,1],[0,2]],
    ],
    # I
    [
        [[1,0],[1,1],[1,2],[1,3]],
        [[0,1],[1,1],[2,1],[3,1]],
        [[2,0],[2,1],[2,2],[2,3]],
        [[0,2],[1,2],[2,2],[3,2]],
    ],
    # O
    [
        [[0,0],[0,1],[1,0],[1,1]],
        [[0,0],[0,1],[1,0],[1,1]],
        [[0,0],[0,1],[1,0],[1,1]],
        [[0,0],[0,1],[1,0],[1,1]],
    ],
]

tetrominoStrings = ['L', 'J', 'T', 'S', 'Z', 'I', 'O']

class Tetromino:
    def __init__(self, piece_type, piece_rotation=0, column = 4):
        self.type = piece_type
        self.rotation = piece_rotation
        self.blocks = ROTATIONS[piece_type][piece_rotation]
        self.position = [column,0]

    def isValidPosition(self):
        for block in self.blocks:
            x = self.position[0] + block[0]
            if x < 0 or x >= 10:
                return False
        return True

class Game:
    def __init__(self, grid, currentPiece=None, storedPiece=None):
        self.grid = [row[:] for row in grid]
        self.currentPiece = currentPiece
        self.storedPiece = storedPiece

    def swap(self):
        sendAction("swap")
        if self.storedPiece is None:
            self.storedPiece = self.currentPiece
            readState(self)
        else:
            temp = self.currentPiece
            self.currentPiece = self.storedPiece
            self.storedPiece = temp
        # sys.stdout.write(f'swapppp\n')

    def canFall(self, t):
        newPos = [t.position[0], t.position[1] + 1]
        for i in range(4):
            new_x = newPos[0]+t.blocks[i][0]
            new_y = newPos[1]+t.blocks[i][1]

            if new_y >= 20:
                return False
            if new_x > 9 or new_x < 0:
                return False
            if self.grid[new_y][new_x] == 1:
                return False
        return True

    def getGhost(self, t):
        ghost = Tetromino(t.type, t.rotation, t.position[0])
        while self.canFall(ghost):
            ghost.position[1] += 1
        return ghost

    def lock(self, t):
        ghost = self.getGhost(t)
        for i in range(4):
            y = ghost.position[1] + ghost.blocks[i][1]
            x = ghost.position[0] + ghost.blocks[i][0]
            self.grid[y][x] = 1
        # print(self.grid)

    def checkGrid(self):
        lineCount = 0
        y = 19
        while y > 0:
            full = 1
            for x in range(10):
                if self.grid[y][x] == 0:
                    full = 0
                    y -= 1
                    break
            if not full:
                continue
            lineCount += 1
            for i in range(y, 0, -1):
                for x in range(10):
                    self.grid[i][x] = self.grid[i-1][x]
        return lineCount

proc = subprocess.Popen(
    ["./cmake-build-debug/tetris", "--bot"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    text=True
)


actions = ["left"]

# def waitForNewPiece():
#     while True:
#         line = proc.stdout.readline().strip()
#         if line.startswith("T"):
#             piece_type = int(line[1])
#             piece_rotation = int(line[2])
#             return Tetromino(piece_type, piece_rotation)

def readState(game):
    grid = []
    while True:
        line = proc.stdout.readline().strip()
        if line.startswith("T"):
            piece_type = int(line[1])
            piece_rotation = int(line[2])
            game.currentPiece = Tetromino(piece_type, piece_rotation)
        elif line == "END":
            if grid:
                game.grid = grid
            return
        elif line:
            grid.append(list(map(int, line.split(','))))



def sendAction(action):
    proc.stdin.write(f"{action}\n")
    proc.stdin.flush()


def getColumnHeights(g):
    heights = [0] * 10
    for x in range(10):
        for y in range(20):
            if g.grid[y][x] == 1:
                heights[x] = 20 - y
                break
    return heights

def countHoles(g, heights):
    holes = 0
    for x in range(10):
        top = 20 - heights[x]
        for y in range(top, 20):
            if g.grid[y][x] == 0:
                holes += 1
    return holes

def getBumpiness(heights):
    bumpiness = 0
    for i in range(9):
        bumpiness += abs(heights[i] - heights[i+1])
    return bumpiness

# def printBoard(board):
#     for row in board.grid:
#         sys.stderr.write(''.join(['#' if c else '.' for c in row]) + '\n')

def countLinesCleared(g):
    return sum(1 for row in g.grid if all(cell == 1 for cell in row))
def evaluateBoard(g):
    lines = g.checkGrid()
    heights = getColumnHeights(g)
    holes = countHoles(g, heights)
    bumpiness = getBumpiness(heights)
    summedHeights = sum(heights)
    return (-0.51 * summedHeights) + (-0.36 * holes) + (-0.18 * bumpiness) + (0.76*lines)

def simulate(g, t):
    simulatedBoard = Game(g.grid)
    simulatedBoard.lock(t)
    return simulatedBoard

def getActions(g, best_rotation, best_column, swap=False):
    actions = []
    if swap:
        g.swap()

    t = g.currentPiece

    rotations = (best_rotation - t.rotation) % 4
    for _ in range(rotations):
        actions.append('rotate_right')

    diff = best_column - t.position[0]
    if diff < 0:
        for _ in range(abs(diff)):
            actions.append('left')
    else:
        for _ in range(diff):
            actions.append('right')
    actions.append('drop')

    return actions

def decideAction(g):
    best_score = float('-inf')
    best_rotation = 0
    best_column = 0
    best_piece = g.currentPiece.type

    scores = []

    for piece in [g.currentPiece, g.storedPiece]:
        if piece is None:
            continue
        for rotation in range(4):
            for column in range(10):
                sim_t = Tetromino(piece.type, rotation, column)
                if not sim_t.isValidPosition():
                    continue
                simulated_board = simulate(g, sim_t)
                score = evaluateBoard(simulated_board)
                scores.append(score)
                if score >= best_score:
                    best_score = score
                    best_rotation = rotation
                    best_column = column
                    best_piece = piece.type

    # sys.stderr.write(str(scores) + '\n')
    # sys.stdout.write("performing move for piece: " + tetrominoStrings[best_piece] + '\n')
    # return getActions(g, best_rotation, best_column, False)
    return getActions(g, best_rotation, best_column, (best_piece != g.currentPiece.type))

# def decideAction(g):
#     return getActions(g.currentPiece, 0, 1)





currentBlock = Tetromino(0,0)
game = Game([[0] * 10 for _ in range(20)], currentBlock)
# readState(game)

game.swap()
# sys.stdout.write(f'Current piece: {tetrominoStrings[game.currentPiece.type]}\n')
# game.storedPiece = Tetromino(storedType)

# actions = decideAction(game)
# for action in actions:
#     sendAction(action)


while True:
    # if any(game.grid[0]):
    #     sendAction('reset')
    actions = decideAction(game)
    for action in actions:
        sendAction(action)
    readState(game)






