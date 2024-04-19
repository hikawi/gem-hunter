import reader
import itertools


def get_valid_neighbors(board: list[list[int]], at: tuple[int, int]) -> list[int]:
    """Returns a list of valid neighbors of the given cell."""
    height, width = len(board), len(board[0])
    x, y = at

    valid_neighbors = []
    for dx, dy in itertools.product(range(-1, 2), range(-1, 2)):
        if y + dy < 0 or y + dy >= height or x + dx < 0 or x + dx >= width or (dx, dy) == (0, 0):
            continue
        valid_neighbors.append((y + dy) * width + (x + dx) + 1)
    return valid_neighbors


def generate_dnf(board: list[list[int]]) -> list[list[int]]:
    """Generates a DNF formula for the given board.
       The DNF formula is a list of clauses, where each clause is a list of literals.
       For example, returning [[1, 2, 3], [-4, -5, -6]] means that:
       (x1 ∧ x2 ∧ x3) ∨ (¬x4 ∧ ¬x5 ∧ ¬x6)"""
    dnf: list[list[int]] = []
    reader.print_data(board)

    # Loop through all cells in (x, y) form.
    for (x, y) in itertools.product(range(len(board[0])), range(len(board))):
        # Unknown cell (-3). If it's -1 or -2, the input board is invalid.
        if board[y][x] < 0:
            continue

        # Basically, the idea is, if there are 5 unknown cells around it.
        # And the number says there are 3 traps.
        # This will have to spit out a clause that says:
        # (x1 ∧ x2 ∧ x3 ∧ ¬x4 ∧ ¬x5) ∨ (x1 ∧ x2 ∧ ¬x3 ∧ x4 ∧ ¬x5) ∨ (x1 ∧ x2 ∧ ¬x3 ∧ ¬x4 ∧ x5) ∨ ...
        neighbors = get_valid_neighbors(board, (x, y))

        # Now, we generate the clauses.
        # As there are board[y][x] traps in len(neighbors) cells.
        # This is just a combination of the neighbors.
        for run in itertools.combinations(neighbors, board[y][x]):
            clause = [i if i in run else -
                      i for i in neighbors]
            dnf.append(clause)
    return dnf
