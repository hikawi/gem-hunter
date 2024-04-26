import reader
import itertools
import randomizer

# the standard way to import PySAT:
from pysat.formula import CNF
from pysat.solvers import Solver


def get_valid_neighbors(board: list[list[int]], at: tuple[int, int]) -> list[int]:
    """Returns a list of valid neighbors of the given cell."""
    height, width = len(board), len(board[0])
    x, y = at

    valid_neighbors = []
    for dx, dy in itertools.product(range(-1, 2), range(-1, 2)):
        if (x == dx and y == dy) or y + dy < 0 or y + dy >= height or x + dx < 0 or x + dx >= width or (dx, dy) == (0, 0) or board[dy + y][dx + x] >= 0:
            continue
        valid_neighbors.append((y + dy) * width + (x + dx) + 1)
    return valid_neighbors

def convert_dnf_to_cnf(groups: list[list[int]]) -> list[list[int]]:
    cnf = [set()]
    for group in groups:
        new_literals = {frozenset([literal]): -literal for literal in group}
        new_cnf = []
        for clause in cnf:
            for literal in new_literals:
                if -new_literals[literal] not in clause:
                    new_clause = set(clause).union({literal})
                    if not any(new_clause.issubset(other) for other in new_cnf):
                        new_cnf.append(new_clause)
        cnf = new_cnf
    return [[int(next(iter(lit))) for lit in clause] for clause in cnf]      
                    
def flatten_list(init: list[int]) -> list[int]:
    """flattem a list to a lower dimension list"""
    new_list = []
    for conjunction in init:
        new_list.extend(conjunction)
    return new_list

def generate_cnf(board: list[list[int]]) -> list[list[list[int]]]:
    """Generates a CNF formula for the given board.
       The CNF formula is a list of clauses, where each clause is a list of literals.
       For example, returning [[1, 2, 3], [-4, -5, -6]] means that:
       (x1 v x2 v x3) ∧ (¬x4 v ¬x5 v ¬x6)"""
   
    cnf: list[list[int]] = []
    # reader.print_data(board)

    # Loop through all cells in (x, y) form.
    for (x, y) in itertools.product(range(len(board[0])), range(len(board))):
        # Unknown cell (-3). If it's -1 or -2, the input board is invalid.
        if board[y][x] < 0:
            continue

        dnf: list[list[int]] = []
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
            if not clause: continue
            dnf.append(clause)

        if not dnf: continue
        print(dnf)
        # change the dnf we get above to cnf
        cnf.append(convert_dnf_to_cnf(dnf))
        dnf.clear()

    return cnf

def get_unknown_cells(board: list[list[int]]) -> list[int]:
    """consider a 2D list: board as an list which has value form 1 to len(board)^2
       this function gets the value of this list of the unknown cells in board(-2, -1)
       and sorts them, this is suitable for the CNF model of pysat lib"""
    rows = len(board)
    cols = len(board[0])

    unknown_cells: list[int] = []
    for i in range(rows):
        for j in range(cols):
            if board[i][j] < 0: # unknown cell has value < 0
                unknown_cells.append(i * rows + j + 1)
    unknown_cells.sort()
    return unknown_cells


def convert_to_increase_value(cnf: list[list[int]], unknown_cells: list[int]) -> None:
    """this function used to change the values of cnf from the smallest value to the 
        largest value, we assign from 1"""
    rows = len(cnf)
    for i in range(rows):
        for j in range(len(cnf[i])):
            temp = cnf[i][j]
            if cnf[i][j]< 0: temp = -temp
            temp = unknown_cells.index(temp) + 1

            if cnf[i][j] < 0: temp = -temp
            cnf[i][j] = temp            

def convert_back_to_real_order(model: list[int], unknown_cells: list[int]) -> None:
    """"after we got the model of CNF, the value of this model has changed in the
        convert_to_increase_value function, so we have to convert back to the initial
        order of each value"""

    length = len(model)
    for i in range(length):     
        if model[i] < 0:
            model[i] = unknown_cells[-model[i] - 1] * -1 # value - 1 of model is the index of unknown_cell
                                                    # and base on this index we can the real order of cell
        else: model[i] = unknown_cells[model[i] - 1]


def find_trap_gem_cell(board: list[list[int]]) -> list[int]:
    """"Get the CNF of the board and use the CNF of the pysat lib to find
        the trap and gemm, the cell with a positive value in the list means 
        that this cell is a trap, otherwise it's a gem"""
    
    three_dim_cnf = generate_cnf(board)
    unknown_cells = get_unknown_cells(board)

    #  The CNF we got above is a 3D list, which is not suitable for the CNF model of 
    #  pysat lib so we need to flatten it to 2D list
    cnf = flatten_list(three_dim_cnf)
    convert_to_increase_value(cnf, unknown_cells)

    cnf_pysat= CNF(from_clauses=cnf)

    model : list[int]
    # create a SAT solver for this formula:
    with Solver(bootstrap_with=cnf_pysat) as solver:
        solver.solve()
        model = solver.get_model()

    convert_back_to_real_order(model, unknown_cells)

    return model


board = randomizer.randomize_board(3, 3, 2, 2)
print("Board")
reader.print_data(board)

print("Traps and gems: ", find_trap_gem_cell(board))

