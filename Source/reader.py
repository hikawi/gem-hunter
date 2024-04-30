from board import Board


def read_data(file_path: str) -> Board:
    """Reads data from a file and returns it as a numpy array."""
    return Board([[-3 if (arg == ' _') or (arg == '_') else int(arg) for arg in s.strip().split(",")]
                  for s in open(file_path, "r").readlines()])


def print_data(data: Board) -> None:
    """Prints the data in a readable format."""
    for row in data.board:
        for elem in row:
            print(f"{elem:>4}", end=" ")
        print()


def match_data_element(value: int) -> str:
    """Converts a value to a string.
       -3 is an unknown cell.
       -2 is a gem cell.
       -1 is a trap cell."""
    match value:
        case -3:
            return "_"
        case -2:
            return "G"
        case -1:
            return "T"
        case _:
            return str(value)


def write_data(file_path: str, data: Board) -> None:
    """Writes data to a file."""
    with open(file_path, "w") as file:
        for row in data.board:
            file.write(", ".join(map(match_data_element, row)) + "\n")
