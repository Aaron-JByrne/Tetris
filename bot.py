import subprocess
import time
import copy

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

class Tetromino:
    def __init__(self, piece_type, piece_rotation=0):
        self.type = piece_type
        self.rotation = piece_rotation
        self.blocks = ROTATIONS[piece_type][piece_rotation]
        self.position = [4,0]

class Board:
    def __init__(self, grid):
        self.grid = [row[:] for row in grid]
    def canFall(self, t):
        newPos = [t.position[0], t.position[1] + 1]
        for i in range(4):
            if newPos[1]+t.blocks[i][1] >= 20:
                return False
            if self.grid[newPos[0]+t.blocks[i][0]][newPos[1]+t.blocks[i][1]] == 1:
                return False
        return True
    def getGhost(self, t):
        ghost = copy.copy(t)
        while self.canFall(self, t):
            ghost.position[1] += 1
        return ghost

    def lock(self, t):
        ghost = self.getGhost(self, t)
        for i in range(4):
            self.grid[ghost.position[0]+ghost.blocks[i][0]][ghost.position[1]+ghost.blocks[i][1]] = 1


proc = subprocess.Popen(
    ["./cmake-build-debug/tetris", "--bot"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    text=True
)

actions = ["left","left", "left", "left", "drop"]
def readState():
    board = []
    while True:
        line = proc.stdout.readline().strip()
        if line == "END":
            break
        elif line.startswith("T"):
            piece_type = int(line[1])
            piece_rotation = int(line[2])
        else:
            row = list(map(int, line.split(",")))
            board.append(row)
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

def evaluateBoard(board):
    heights = getColumnHeights(board)
    holes = countHoles(board, heights)
    bumpiness = getBumpiness(heights)
    summedHeights = sum(heights)
    return (-0.5 * summedHeights) + (-0.35 * holes) + (-0.18 * bumpiness)


def simulate(board, t):
    simulatedBoard = board.copy()
    for block in range(4):




def getActions(piece_type, piece_rotation, best_rotation, best_column):

def decideAction(board, t):
    best_score = float('-inf')
    best_rotation = 0
    best_column = 0

    for rotation in range(4):
        for column in range(10):
            simulated_board = simulate(board, piece_type, piece_rotation)
            score = evaluateBoard(simulated_board)
            if score > best_score:
                best_score = score
                best_rotation = rotation
                best_column = column

    return getActions(piece_type, piece_rotation, best_rotation, best_column)


while True:
    board, tetromino = readState()
    action = decideAction(board)
    sendAction(action)


