import numpy as np
from enum import IntEnum
import keyboard
import os


class T(IntEnum):
    N = 0  # none
    W = 1  # wall
    B = 2  # box
    T = 4  # target
    P = 8  # player


board = np.array(
    [
        [1, 1, 1, 1, 1, 1],
        [1, 8, 0, 0, 0, 1],
        [1, 0, 2, 0, 4, 1],
        [1, 0, 1, 2, 4, 1],
        [1, 0, 2, 0, 4, 1],
        [1, 1, 1, 1, 1, 1],
    ]
)
assert ((board & T.P) == T.P).sum() == 1
assert ((board & T.B) == T.B).sum() == ((board & T.T) == T.T).sum()
os.system("cls")


def on_action(press_event: keyboard.KeyboardEvent):
    # os.system("cls")
    p_pos = board.argmax()
    b = board.ravel()
    match press_event.name:
        case "w":
            step = -board.shape[1]
            n_in_front = p_pos // abs(step)
        case "s":
            step = board.shape[1]
            n_in_front = (board.shape[0] * board.shape[1] - 1 - p_pos) // abs(step)
        case "a":
            step = -1
            n_in_front = p_pos % board.shape[1]
        case "d":
            step = 1
            n_in_front = board.shape[1] - p_pos % board.shape[1] - 1
        case "q":
            return
        case _:
            print("invalid")
            return
    sight = [b[p_pos + i * step] for i in range(1, n_in_front + 1)]
    if sight[0] & T.W == T.W:  # hit wall
        pass
    elif sight[0] & T.B == T.B:  # hit box
        if sight[1] & T.W != T.W and sight[1] & T.B != T.B:  # nothing behind box
            b[p_pos] -= T.P
            b[p_pos + step] += T.P
            b[p_pos + step] -= T.B
            b[p_pos + 2 * step] += T.B
        else:  # sonething behind the box
            pass
    else:  # hit nothing
        b[p_pos] -= T.P
        b[p_pos + step] += T.P
    print(board)
    if ((board & (T.B | T.T)) == (T.B | T.T)).sum() == ((board & T.B) == T.B).sum():
        print("WIN")
        return


if __name__ == f"__main__":
    print(board)
    keyboard.on_press(on_action)
    keyboard.wait("q", True)
    os.system("cls")
