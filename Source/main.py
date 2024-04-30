import reader
import itertools
import time
import copy


# the standard way to import PySAT:
from pysat.formula import CNF
from pysat.solvers import Solver
from board import Board, randomize_board
import os


def get_valid_neighbors(board: Board, at: tuple[int, int]) -> list[int]:
    """Returns a list of valid neighbors of a cell at (x, y).
       A valid neighbor means that the cell is NOT KNOWN yet, and is in bounds."""
    height, width = board.dims()
    x, y = at

    valid_neighbors = []
    for dx, dy in itertools.product(range(-1, 2), range(-1, 2)):
        # Self case.
        if (dx, dy) == (0, 0):
            continue

        # Out of bounds case.
        if x + dx < 0 or x + dx >= width or y + dy < 0 or y + dy >= height:
            continue

        # Known cell case.
        if board[x + dx, y + dy] >= 0:
            continue

        valid_neighbors.append((y + dy) * width + (x + dx) + 1)
    return valid_neighbors


def generate_dnf(board: Board, at: tuple[int, int]) -> list[list[int]]:
    """Generates a DNF clause for the given cell at (x, y) in board.
       The DNF clause is a list of literals, where each literal is an integer.
       For example, returning [1, 2, 3] means that:
       (x1 ∧ x2 ∧ x3) v ..."""
    x, y = at
    neighbors = get_valid_neighbors(board, at)
    clauses: list[list[int]] = []

    # Current cell is NOT a number cell.
    if board[at] < 0:
        return []

    # Iterate through all combinations of neighbors, where each run is of length board[at].
    # For example, if board[at] is 3, and there are 5 unknown neighbors, then we have 5 choose 3 = 10 runs.
    # Each run is a combination of 3 neighbors, the ones chosen in the run are MINES
    # and the ones not chosen are GEMS. There are 5 choose 3 cases.
    for run in itertools.combinations(neighbors, board[at]):
        clause = [i if i in run else -i for i in neighbors]
        clauses.append(clause)

    return clauses  
                    
def convert_dnf_to_cnf(groups: list[list[int]]) -> list[list[int]]:
    # Initialize CNF with an empty clause
    cnf: list[list[int]] = [[]]

    # Iterate through each group in the DNF expression
    for group in groups:
        # Create a dictionary of new literals with their negations
        new_literals = {literal: -literal for literal in group}
        # Initialize an empty list to store new CNF clauses
        new_cnf = []
        
        # Iterate through each clause in the current CNF
        for clause in cnf:
            # Iterate through each new literal
            for literal, negation in new_literals.items():
                # Check if the negation of the current literal is not in the clause
                if negation not in clause:
                    # Create a new clause by adding the current literal to the current clause
                    new_clause = clause + [literal]
                    # Check if the new clause is not a subset of any existing clause in new CNF
                    if not any(set(new_clause).issubset(set(other)) for other in new_cnf):
                        # Add the new clause to new CNF
                        new_cnf.append(new_clause)
        
        # Update CNF with the new CNF clauses
        cnf = new_cnf
    
    return cnf

def flatten_list(init: list[int]) -> list[int]:
    """flatten a list to a lower dimension list"""
    new_list: list[int] = []
    for conjunction in init:
        new_list.extend(conjunction)
    return new_list


def generate_cnf(board: Board) -> list[list[int]]:
    """Generates a DNF formula for the given cell at (x, y) in board.
       The DNF formula is a list of clauses, where each clause is a list of literals.
       For example, returning [[1, 2, 3], [-4, -5, -6]] means that:
       (x1 v x2 v x3) ∧ (¬x4 v ¬x5 v ¬x6)"""

    cnf: list[list[int]] = []
    dims = board.dims()
   
    for x in range(dims[0]):
        for y in range(dims[1]):
            dnf = generate_dnf(board, (x, y))
            if not dnf:
                continue
            # change the dnf we get above to cnf
            cnf.append(convert_dnf_to_cnf(dnf))
            dnf.clear()

    return cnf

def get_unknown_cells(board: Board) -> list[int]:
    """consider a 2D list: board as an list which has value form 1 to len(board)^2
       this function gets the value of this list of the unknown cells in board(-2, -1)
       and sorts them, this is suitable for the CNF model of pysat lib"""
    dims = board.dims() 

    unknown_cells: list[int] = []
    for x in range(dims[0]):
        for y in range(dims[1]):
            if board[x,y] < 0:  # unknown cell has value < 0
                unknown_cells.append(y * dims[0] + x + 1)
    unknown_cells.sort()
    return unknown_cells


def convert_to_increase_value(cnf: list[list[int]], unknown_cells: list[int]) -> None:
    """this function used to change the values of cnf from the smallest value to the 
        largest value, we assign from 1"""
    rows = len(cnf)
    for i in range(rows):
        for j in range(len(cnf[i])):
            temp = cnf[i][j]
            if cnf[i][j] < 0:
                temp = -temp
            temp = unknown_cells.index(temp) + 1

            if cnf[i][j] < 0:
                temp = -temp
            cnf[i][j] = temp


def convert_back_to_real_order(model: list[int], unknown_cells: list[int]) -> None:
    """"after we got the model of CNF, the value of this model has changed in the
        convert_to_increase_value function, so we have to convert back to the initial
        order of each value"""

    length = len(model)
    for i in range(length):
        if model[i] < 0:
            # value - 1 of model is the index of unknown_cell
            model[i] = unknown_cells[-model[i] - 1] * -1
            # and base on this index we can the real order of cell
        else:
            model[i] = unknown_cells[model[i] - 1]


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

    cnf_pysat = CNF(from_clauses=cnf)

    model: list[int]
    # create a SAT solver for this formula:
    with Solver(bootstrap_with=cnf_pysat) as solver:
        solver.solve()
        model = solver.get_model()

    convert_back_to_real_order(model, unknown_cells)

    model.sort()

    return model

def check(clause:list[int], model:list[int]):
    clause_symbol=set()
    for i in clause:
        clause_symbol.add(abs(i))
    model_symbol=set()
    for i in model:
        model_symbol.add(abs(i))
    if(len(model_symbol)<len(clause_symbol)):
        return True
    for i in clause_symbol:
        if  i not in model_symbol:
            return True
    for i in clause:
        if i in model:
            return True
    return False
def find_pure_symbol(symbols):
    p=list(symbols)[:]
    temp=[]
    for i in symbols:
        for j in symbols:
            if i!=j and i+j==0:
                temp.append(i)
    for i in temp:
        p.remove(i)
    if len(p)==0:
        return None
    return p

def find_unit_function(board):
    p=set()
    for i in board:
        if len(i)==1:
            p.add(i[0])
    if len(p)==0:
        return None
    return p        

def solve(board : list[list[int]],symbols, model:list[int],count,flag=0) -> list[int]:
    for i in range(0,len(board)):
        if check(board[i],model)==False:
            return False
        elif (i==len(board)-1 and len(model)==count):
            return model
    if flag==0:
        p=find_pure_symbol(symbols)
        if p!=None :
            for i in p:
                model.add(i)
                symbols.discard(i)
            return solve(board,symbols, model,count,1)
    if flag==0:
        p=find_unit_function(board)
        if p!=None :
            for i in p:
                model.add(i)
                symbols.discard(i)
                if -i in symbols:
                    symbols.discard(-i)
            return solve(board, symbols, model,count,1)
    q=symbols.pop()
    if -q in symbols:
        symbols.discard(-q)
    store1=model.copy()
    store2=symbols.copy()
    model.add(q)
    result=solve(board,symbols, model,count,1)
    if(result!=False):
        return result
    model=store1.copy()
    model.add(-q)
    symbols=store2.copy()
    result=solve(board,symbols, model,count,1)
    if(result!=False):
        return result
    return False


def brute_force(board: list[list[int]], symbols, model, count):
    symbols_copy = symbols.copy()
    for i in range(0, len(board)):
        if not check(board[i], model):
            return None
        elif i == len(board) - 1 and len(model) == count:
            return model.copy()

    if not symbols_copy:
        return None
    q = symbols_copy.pop()
    if q is not None and -q in symbols_copy:
        symbols_copy.discard(-q)

    if q is not None:
        model.add(q)
        result = brute_force(board, symbols_copy, model, count)
        if result:
            return result
        else:
            model.remove(q)

    if q is not None:
        model.add(-q)
        result = brute_force(board, symbols_copy, model, count)
        if result:
            return result
        else:
            model.remove(-q)

    return None

def run(board):
    model=set()
    symbols=set()
    temp=flatten_list(generate_cnf(board))
    for i in temp:
        for j in i:
            symbols.add(j)
    count=set()
    for i in symbols:
        count.add(abs(i))

    # backtracking
    start_time = time.time()
    model = list(solve(temp, copy.deepcopy(symbols), model, len(count)))
    model.sort()
    elapsed_time =  time.time() - start_time
    print("Model result by DPLL(backtrack): ", model)
    print("Backtracking solve time:", elapsed_time, "seconds")

    # brute-force
    model = set()
    start_time = time.time()
    brute_force_model = list(brute_force(temp, symbols, model, len(count)))
    brute_force_model.sort()
    elapsed_time = time.time() - start_time
    print("Model result by Brute-force:     ", brute_force_model)
    print("Brute-force solve time:", elapsed_time, "seconds")

def convert_board_to_write(board: Board, model: list[int]) -> None:
    """After we got the model by solving the CNF, we change
       the positive value to -1(trap), and the negative value
       to -2(gem) to write to the output.txt file"""
    
    dims = board.dims()

    for val in model:
        temp = abs(val)
        y = temp // dims[1]
        x = (temp - 1) % dims[1]
        if temp % dims[1] == 0:
            y -= 1
        if x == -1:
            x = dims[1] - 1 if temp != 0 else 0
        if val < 0: 
            board.change_value([x, y], -2)
        else:
            board.change_value([x, y], -1)
 

def get_board_from_file(file_name: str) -> Board: 
    """Create a board based the content in the file input"""
    # Get the directory of the current Python script
    current_dir = os.path.dirname(os.path.realpath(__file__))

    # Specify the path to the subfolder
    subfolder_path = os.path.join(current_dir, 'testcases')

    # Path to the file in the subfolder
    file_path = os.path.join(subfolder_path, file_name)

    board = reader.read_data(file_path)

    return board

def write_to_file(file_name: str, board: Board, model: list[int]) -> None:
    """Write the result to the output.txt file in testcases folder"""

    convert_board_to_write(board, model)
    # Get the directory of the current Python script
    current_dir = os.path.dirname(os.path.realpath(__file__))

    # Specify the path to the subfolder
    subfolder_path = os.path.join(current_dir, 'testcases')

    # Path to the file in the subfolder
    file_path = os.path.join(subfolder_path, file_name)
    reader.write_data(file_path, board)

def main():

    while(1):
        print("--------------------------------------")
        print("Welcome to gem hunter game!!!")
        print("Please enter your choice of size map:")
        print("1. 5x5\n2. 9x9\n3. 11x11\n4. 15x15\n5. 20x20\n0. Exit")
        print("Your choice: ", end="")
        choice = int(input())

        if (choice == 0): break

        name: str
        if choice == 1: name = "5x5"
        elif choice == 2: name = "9x9"
        elif choice == 3: name = "11x11"
        elif choice == 4: name = "15x15"
        elif choice == 5: name = "20x20"

        board = get_board_from_file(f"input{name}.txt")

        # find model by using pysat library
        model = find_trap_gem_cell(board)
        print("Model result by using pysat lib: ", model)
        run(board)

        # write to output.txt file 
        write_to_file(f"output{name}.txt", board, model)

if __name__ == "__main__":
    main()
