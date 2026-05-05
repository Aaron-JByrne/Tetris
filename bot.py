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

class Board:
    def __init__(self, grid):
        self.grid = [row[:] for row in grid]

    def canFall(self, t):
        newPos = [t.position[0], t.position[1] + 1]
        for i in range(4):
            if newPos[1]+t.blocks[i][1] >= 20:
                return False
            print(newPos[1]+t.blocks[i][1],newPos[0]+t.blocks[i][0])
            print(self.grid[newPos[1]+t.blocks[i][1]])
            if newPos[0]+t.blocks[i][0] > 9:
                return False
            if self.grid[newPos[1]+t.blocks[i][1]][newPos[0]+t.blocks[i][0]] == 1:
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


proc = subprocess.Popen(
    ["./cmake-build-debug/tetris", "--bot"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    text=True
)

actions = ["left"]
def readState():
    board = []
    piece_type = None
    piece_rotation = None
    while True:
        line = proc.stdout.readline().strip()
        if line == "END":
            break
        elif line == "":
            continue
        elif line.startswith("T"):
            piece_type = int(line[1])
            piece_rotation = int(line[2])
        else:
            row = list(map(int, line.split(",")))
            board.append(row)

    if piece_type is None:
        return Board(board), None

    print(f'new piece is {tetrominoStrings[piece_type]}-block')
    return Board(board), Tetromino(piece_type, piece_rotation)

def sendAction(action):
    proc.stdin.write(f"{action}\n")
    proc.stdin.flush()


def getColumnHeights(board):
    heights = [0] * 10
    for x in range(10):
        for y in range(20):
            if board.grid[y][x] == 1:
                heights[x] = 20 - y
                break
    return heights

def countHoles(board, heights):
    holes = 0
    for x in range(10):
        top = 20 - heights[x]
        for y in range(top, 20):
            if board.grid[y][x] == 0:
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


def countLinesCleared(board):
    return sum(1 for row in board.grid if all(cell == 1 for cell in row))
def evaluateBoard(board):
    heights = getColumnHeights(board)
    holes = countHoles(board, heights)
    bumpiness = getBumpiness(heights)
    summedHeights = sum(heights)
    lines = countLinesCleared(board)
    return (-0.5 * summedHeights) + (-0.35 * holes) + (-0.18 * bumpiness) + (1.0 * lines)


def simulate(board, t):
    simulatedBoard = Board(board.grid)
    simulatedBoard.lock(t)
    return simulatedBoard




def getActions(t, best_rotation, best_column):
    actions = []

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

def decideAction(board, t):
    best_score = float('-inf')
    best_rotation = 0
    best_column = 0

    for rotation in range(4):
        for column in range(10):
            sim_t = Tetromino(t.type, rotation, column)
            if not sim_t.isValidPosition():
                continue
            simulated_board = simulate(board, sim_t)
            score = evaluateBoard(simulated_board)
            if score > best_score:
                best_score = score
                best_rotation = rotation
                best_column = column

    return getActions(t, best_rotation, best_column)

# def decideAction(board, t):
#     return getActions(t, 0, 0)


while True:
    board, tetromino = readState()
    if tetromino is None:
        continue
    if any(board.grid[0]):
        sendAction('reset')
    actions = decideAction(board, tetromino)
    for action in actions:
        sendAction(action)





