import numpy as np
from enum import IntEnum
from pynput.keyboard import Key, KeyCode, Listener, Controller
from rich.console import Console
from rich.style import Style


class T(IntEnum):
    W = 1  # wall
    B = 2  # box
    T = 4  # target
    P = 8  # player


board = np.array(
    [
        [1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 4, 0, 0, 8, 1],
        [1, 0, 0, 2, 2, 2, 0, 0, 1],
        [1, 4, 1, 1, 4, 1, 1, 4, 1],
        [1, 0, 0, 0, 2, 0, 0, 0, 1],
        [1, 0, 0, 2, 4, 1, 0, 1, 1],
        [1, 1, 1, 1, 0, 0, 0, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1],
    ]
)
assert ((board & T.P) == T.P).sum() == 1
assert ((board & T.B) == T.B).sum() == ((board & T.T) == T.T).sum()

controller = Controller()
console = Console()
console.clear()
colors = {
    T.W: Style(color="cyan", bgcolor="cyan"),
    T.B: Style(color="green", bgcolor="green"),
    T.T: Style(color="red", bgcolor="red"),
    T.P: Style(color="blue", bgcolor="blue"),
    T.B | T.T: Style(color="yellow", bgcolor="yellow"),
    T.P | T.T: Style(color="purple", bgcolor="purple"),
}


def rich_print(board: np.ndarray):
    for row in board:
        for value in row:
            if value in colors:
                styled_value = f"[{colors[value]}]  [/]"
            else:
                styled_value = "  "
            console.print(styled_value, end="")
        console.print()


def on_action(key: Key | KeyCode):
    p_pos = board.argmax()
    b = board.ravel()
    console.clear()
    if isinstance(key, KeyCode):
        btn = key.char
    elif isinstance(key, Key):
        btn = key.name
    match btn:
        case "w" | "up":
            step = -board.shape[1]
            n_in_front = p_pos // abs(step)
        case "s" | "down":
            step = board.shape[1]
            n_in_front = (board.shape[0] * board.shape[1] - 1 - p_pos) // abs(step)
        case "a" | "left":
            step = -1
            n_in_front = p_pos % board.shape[1]
        case "d" | "right":
            step = 1
            n_in_front = board.shape[1] - p_pos % board.shape[1] - 1
        case "q":
            return False
        case _:
            console.clear()
            rich_print(board)
            console.print("invalid")
            return
    sight = [b[p_pos + i * step] for i in range(1, n_in_front + 1)]
    if sight[0] & T.W == T.W:  # hit wall
        pass
    elif sight[0] & T.B == T.B:  # hit box
        if sight[1] & T.W != T.W and sight[1] & T.B != T.B:  # nothing block box
            b[p_pos] -= T.P
            b[p_pos + step] += T.P
            b[p_pos + step] -= T.B
            b[p_pos + 2 * step] += T.B
        else:  # something block the box
            pass
    else:  # hit nothing
        b[p_pos] -= T.P
        b[p_pos + step] += T.P
    rich_print(board)
    if (board == T.B).sum() == 0:
        console.print("WIN")
        return False


with Listener(on_press=on_action, suppress=True) as l:  # type: ignore
    rich_print(board)
    l.join()
