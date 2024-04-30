import random


class Board:
    board: list[list[int]]

    def __init__(self, board: list[list[int]]) -> None:
        self.board = board

    def __getitem__(self, at: tuple[int, int]) -> int:
        """Returns the value of the cell at the given coordinates (x, y)."""
        return self.board[at[1]][at[0]]

    def dims(self) -> tuple[int, int]:
        """Returns the dimensions of the board in the order x,y"""
        return len(self.board[0]), len(self.board)

    def is_blurred(self) -> bool:
        """Checks if the board is blurred. A blurred board means that it only contains
           number cells and unknown cells, but no traps or gems."""
        return any(cell in (-1, -2) for row in self.board for cell in row)

    def blur(self) -> 'Board':
        """Sets all traps and gems to unknown cells."""
        new_cells = [[-3 if cell in (-1, -2) else cell for cell in row]
                     for row in self.board]
        return Board(new_cells)

    def is_valid(self) -> bool:
        """Checks if the board is valid. A valid board means that it only contains
           number cells, no traps, no gems, and no unknown cells."""
        return all(cell >= 0 for row in self.board for cell in row)

    def matches(self, other: 'Board') -> bool:
        """Checks if the two boards match."""
        return self.board == other.board

    def fuzzy_matches(self, other: 'Board') -> bool:
        """Checks if the two boards match fuzzily. Which means that traps and gems are considered as unknown cells.
           As long as the cells are the same (number = number or unknown = unknown), the boards match."""
        return self.blur().matches(other.blur())

    def __eq__(self, other: object) -> bool:
        """Checks if the two boards are equal."""
        return isinstance(other, Board) and self.matches(other)
    
    def change_value(self, at: tuple[int, int], new_val: int):
        """"Assign new value to a specific position of the board"""
        self.board[at[1]][at[0]] = new_val


def randomize_board(height: int, width: int, traps: int, gems: int) -> Board:
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
    return Board(board)
