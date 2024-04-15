import numpy as np
import numpy.typing as npt


def read_data(file_path: str) -> npt.ArrayLike:
    """Reads data from a file and returns it as a numpy array."""
    lines: list[list[str]] = [s.strip().split(",")
                              for s in open(file_path, "r").readlines()]
    return np.array([-3 if arg == "_" else int(arg) for line in lines for arg in line]).reshape(len(lines), len(lines[0]))


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


def write_data(file_path: str, data: npt.ArrayLike) -> None:
    """Writes data to a file."""
    with open(file_path, "w") as file:
        for row in data:
            file.write(",".join(map(match_data_element, row)) + "\n")


data = read_data("./test/input.txt")
print(data)
write_data("./test/output.txt", data)
