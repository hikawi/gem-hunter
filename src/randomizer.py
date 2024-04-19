"""
A module for generating random boards with a specified number of traps and gems.
"""

import random


def randomize_board(height: int, width: int, traps: int, gems: int) -> list[list[int]]:
    """Generates a random board with the given dimensions and number of traps and gems."""
    if height * width < traps + gems:
        raise ValueError("Too many traps and gems for the given board size.")
    if height < 1 or width < 1 or traps < 0 or gems < 0:
        raise ValueError("Invalid parameters, all must be > 0.")

    board = [[0 for _ in range(width)] for _ in range(height)]

    # Generate traps, by randomly generating (x, y) until it matches an empty cell.
    for _ in range(traps):
        x, y = random.randint(0, width - 1), random.randint(0, height - 1)
        while board[y][x] != 0:
            x, y = random.randint(0, width - 1), random.randint(0, height - 1)
        board[y][x] = -1

    # Generate gems, by randomly generating (x, y) until it matches an empty cell.
    for _ in range(gems):
        x, y = random.randint(0, width - 1), random.randint(0, height - 1)
        while board[y][x] != 0:
            x, y = random.randint(0, width - 1), random.randint(0, height - 1)
        board[y][x] = -2

    # Now we fill with numbers, in the remaining empty cells, that indicate how many traps
    # around that cell.
    for y in range(height):
        for x in range(width):
            if board[y][x] == 0:
                board[y][x] = sum(1 for dy in range(-1, 2) for dx in range(-1, 2)
                                  if 0 <= y + dy < height and 0 <= x + dx < width and board[y + dy][x + dx] == -1)
    return board


def match_board(left: list[list[int]], right: list[list[int]]) -> bool:
    """Checks if the two boards provided MATCH."""
    return all(left[y][x] == right[y][x] for y in range(len(left)) for x in range(len(left[0])))


def fuzzy_match_board(left: list[list[int]], right: list[list[int]]) -> bool:
    """Checks if the two boards provided match fuzzily. Which means that traps and gems are considered as unknown cells.
       As long as the cells are the same (number = number or unknown = unknown), the boards match."""
    return match_board(blur_board(left), blur_board(right))


def blur_board(board: list[list[int]]) -> list[list[int]]:
    """Sets all traps and gems to unknown cells."""
    return [[-3 if arg in (-1, -2) else arg for arg in row] for row in board]
