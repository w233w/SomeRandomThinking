import tkinter as tk
import random
from itertools import product
from typing import Literal

# poker game
# 36 poker cards from 4 colors and A to 9. THey are face down and randomly placed in a 6*6 girds.
# for every round:
# click any face down poker to flip.
# but next card is this round can only be previous poker's 4 neighbor.

# Goal is to make the sum of flipped card's value exactly match to target. You can flip any number of card in a round
# until: sum equal to target, all flipped card this round will keep face up, and you win score equal to target. sum
# larger than target, all flipped card in this round will become face down again, and you lose 2 score. Specially,
# if no available neighbor after flip, you lose the round no matter the sum.

# since the poker card placed randomly, There is chance for some card can never be flipped. click "call button"
# before start round will end the game, program will check the rest poker for you. if all face down poker truly
# can't make any match, you win score equal to number of face down poker. Otherwise, you lost double score.


class Poker:
    def __init__(self, color: Literal["♠", "♥", "♣", "♦"], value: int) -> None:
        self.color: Literal["♠", "♥", "♣", "♦"] = color
        self.value: int = value

    def __str__(self) -> str:
        return f"{self.color}{'A' if self.value == 1 else self.value}"


class Controller:
    def __init__(self) -> None:
        self.deck: list[Poker] = [
            Poker(color, value)
            for color, value in product(("♠", "♥", "♣", "♦"), range(1, 10))
        ]
        random.shuffle(self.deck)
        self.grids: list[list[Poker]] = [
            [self.deck[i + j * 6] for i in range(6)] for j in range(6)
        ]
        self.fliped: set[tuple[int, int]] = set()
        self.fliping: set[tuple[int, int]] = set()
        self.available: set[tuple[int, int]] = set(product(range(6), range(6)))
        self.warning: list[tuple[int, int]] = []
        self.score = 0
        self.target = random.randint(10, 16)
        self.failed = False

    def on_flip(self, coord: tuple[int, int]) -> None:
        if self.failed:
            self.fliping.clear()
            self.available = set(product(range(6), range(6))).difference(self.fliped)
            self.failed = False
            return
        self.available.clear()
        self.fliping.add(coord)
        values = [self.grids[row][col].value for col, row in self.fliping]
        sums = sum(values)
        if sums < self.target:
            col, row = coord
            for direction in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                y, x = col + direction[0], row + direction[1]
                if (
                    0 <= y < 6
                    and 0 <= x < 6
                    and (y, x) not in self.fliping
                    and (y, x) not in self.fliped
                ):
                    self.available.add((y, x))
            if len(self.available) == 0:
                self.available = {coord}
                self.score -= 2
                self.failed = True
        elif sums == self.target:
            self.fliped = self.fliped.union(self.fliping)
            self.fliping.clear()
            self.score += self.target
            self.available = set(product(range(6), range(6))).difference(self.fliped)
        elif sums > self.target:
            self.available = {coord}
            self.score -= 2
            self.failed = True

    def can_call(self) -> bool:
        return len(self.fliping) == 0

    def on_call(self) -> None:
        rest = 36 - len(self.fliped)
        self.available.clear()
        self.fliping = set(product(range(6), range(6))).difference(self.fliped)
        res = set()
        for col, row in self.fliping:
            res = res.union(self.dfs(col, row, 0, [], set()))
            if len(res) >= 1:
                self.warning.extend(res.pop())
                self.score -= rest * 2
                break
        else:
            self.score += rest

    def dfs(
        self,
        col: int,
        row: int,
        val: int,
        hist: list[tuple[int, int]],
        res: set[tuple[tuple[int, int]]],
    ) -> set[tuple[tuple[int, int]]]:
        val += self.grids[row][col].value
        hist.append((col, row))
        if val == self.target:
            return {tuple(hist)}
        elif val > self.target:
            hist.remove((col, row))
            val -= self.grids[row][col].value
            return set()
        for direction in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            y, x = col + direction[0], row + direction[1]
            if (
                0 <= y < 6
                and 0 <= x < 6
                and (y, x) not in hist
                and (y, x) not in self.fliped
            ):
                res = res.union(self.dfs(y, x, val, hist, res))
                if len(res) >= 1:
                    return res
        hist.remove((col, row))
        val -= self.grids[row][col].value
        return set()


class UI:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("")
        self.root.geometry("180x216")
        self.root.resizable(width=False, height=False)
        self.game = Controller()

        self.menubar = tk.Menu(self.root)
        self.menu_start = tk.Menu(self.menubar, tearoff=0)
        self.menu_start.add_command(label="Restart", command=self.restart)
        self.menu_start.add_separator()
        self.menu_start.add_command(label="Exit", command=self.root.destroy)
        self.menubar.add_cascade(label="Game", menu=self.menu_start)
        self.root.config(menu=self.menubar)

        # 主界面
        self.score_frame = tk.Frame(self.root)
        self.score_frame.place(relheight=1 / 6, relwidth=1, relx=0, rely=0)
        self.card_frame = tk.Frame(self.root)
        self.card_frame.place(relheight=5 / 6, relwidth=1, relx=0, rely=1 / 6)

        # 上边
        self.score = tk.StringVar(value=f"Score: {self.game.score}")
        self.score_label = tk.Label(self.score_frame, textvariable=self.score)
        self.score_label.place(relheight=1, relwidth=0.4, relx=0, rely=0)
        self.call_button = tk.Button(
            self.score_frame,
            text="Call",
            command=lambda: [self.game.on_call(), self.render()],
        )
        self.call_button.place(relheight=1, relwidth=0.2, relx=0.4, rely=0)
        self.target = tk.StringVar(value=f"Target: {self.game.target}")
        self.target_label = tk.Label(self.score_frame, textvariable=self.target)
        self.target_label.place(relheight=1, relwidth=0.4, relx=0.6, rely=0)

        self.render()

    def restart(self) -> None:
        self.game = Controller()
        self.render()

    def render(self) -> None:
        self.score.set(f"Score: {self.game.score}")
        self.target.set(f"Target: {self.game.target}")
        self.call_button.config(state="active" if self.game.can_call() else "disabled")
        for widget in self.card_frame.winfo_children():
            widget.destroy()
        for i, row in enumerate(self.game.grids):
            for j, poker in enumerate(row):
                coord = (j, i)
                tk.Button(
                    self.card_frame,
                    text=(
                        poker
                        if coord in self.game.fliped or coord in self.game.fliping
                        else "?"
                    ),
                    command=lambda c=coord: [
                        self.game.on_flip(c),
                        self.render(),
                    ],
                    state="active" if coord in self.game.available else "disable",
                    bg=(
                        "pink"
                        if coord in self.game.warning
                        else ("yellow" if coord in self.game.fliped else None)
                    ),
                ).place(relheight=1 / 6, relwidth=1 / 6, relx=j / 6, rely=i / 6)

    def run(self) -> None:
        self.root.mainloop()


if __name__ == "__main__":
    UI().run()
