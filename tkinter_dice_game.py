import tkinter as tk
import random
from itertools import count, product

# dice game 1
# Total 36 random rolled D6s are placed in 6*6 grid.
# Click to select a dice, then click "reroll button" to reroll them.
# You only have total 6 Rounds(T) and 36 Rerolls(R). Before any of them run out:
# Your goal is to make any row, column, diagonal have the same number.
# S stand for the number of dice you selected.

# You can change the parameter at buttom of this file to change the game.
# d_face is dice's faces in [1, d_face], g_size is grid size in [3, 6].
# Rounds(T) will change to d_face, the Rerolls(R) will change to g_size ^ 2.


class Dice:
    ids = count()

    def __init__(self, faces: int = 6) -> None:
        self.faces: int = faces
        self.id: int = next(Dice.ids)
        self.values = list(range(1, faces + 1))
        self.last_roll: int = self.roll()

    def __str__(self) -> str:
        return f"{self.last_roll}"

    def __repr__(self) -> str:
        return f"<D-{self.faces}|{self.last_roll}>"

    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, Dice):
            return self.last_roll == __value.last_roll
        elif isinstance(__value, int):
            return self.last_roll == __value
        else:
            raise ValueError()

    def roll(self) -> None:
        self.last_roll: int = random.choice(self.values)

    @property
    def color(self) -> str:
        if self.last_roll == 1:
            return "#a3ffb4"
        elif self.last_roll == 2:
            return "#fef65b"
        elif self.last_roll == 3:
            return "#66cdaa"
        elif self.last_roll == 4:
            return "#4a8bad"
        elif self.last_roll == 5:
            return "#a3b8c8"
        elif self.last_roll == 6:
            return "#d7b4ae"


class Controller:
    def __init__(self, d_face: int = 6, size: int = 6) -> None:
        if size < 3 or size > 6:
            raise ValueError(r"size can only in [3, 6]")
        self.size: int = size
        self.d_face: int = d_face
        self.grid: list[list[Dice]] = [
            [Dice(d_face) for i in range(size)] for j in range(size)
        ]
        self.selected: list[tuple[int]] = list(product(range(size), range(size)))
        self.max_roll: int = 2 * (size**2)
        self.max_turn: int = d_face + 1
        self.roll()

    def reset(self):
        self.__init__(self.d_face, self.size)

    def roll(self):
        if self.max_turn > 0:
            self.max_turn -= 1
            for i, row in enumerate(self.grid):
                for j, dice in enumerate(row):
                    if (j, i) in self.selected:
                        dice.roll()
            self.max_roll -= len(self.selected)
            self.selected = []

    def on_select(self, coord):
        if coord in self.selected:
            self.selected.remove(coord)
        else:
            self.selected.append(coord)

    def check_select(self, coord):
        return coord in self.selected

    @property
    def can_roll(self):
        return (
            1 <= len(self.selected) <= self.max_roll
            and self.max_roll > 0
            and self.max_turn > 0
        )

    @property
    def win(self):
        for i in range(self.size):
            # by row
            for j in self.grid:
                if j == [i + 1] * self.size:
                    return "WIN"
            # by col
            ls = [self.grid[j][i].last_roll for j in range(self.size)]
            if len(set(ls)) == 1:
                return "WIN"
        # down slope
        down = [self.grid[i][i].last_roll for i in range(self.size)]
        if len(set(down)) == 1:
            return "WIN"
        # up slope
        up = [self.grid[i][self.size - 1 - i].last_roll for i in range(self.size)]
        if len(set(up)) == 1:
            return "WIN"
        if not (self.max_roll > 0 and self.max_turn > 0):
            return "LOSE"
        return ""


class UI:
    def __init__(self, **kwarg) -> None:
        self.root = tk.Tk()
        self.root.title("mini")
        self.root.geometry("200x150")
        self.root.resizable(width=False, height=False)

        d_face = kwarg.get("d_face", 6)
        size = kwarg.get("size", 6)
        self.game = Controller(d_face=d_face, size=size)

        # 菜单
        self.menubar = tk.Menu(self.root)
        self.menu_start = tk.Menu(self.menubar, tearoff=0)
        self.menu_start.add_command(label="Restart", command=self.restart)
        self.menu_start.add_separator()
        self.menu_start.add_command(label="Exit", command=self.root.destroy)
        self.menubar.add_cascade(label="Game", menu=self.menu_start)
        self.root.config(menu=self.menubar)

        self.field = tk.Frame(self.root, bd=1, relief="raised")
        self.field.place(relheight=1, relwidth=3 / 4, relx=0, rely=0)
        self.pannel = tk.Frame(self.root)
        self.pannel.place(relheight=1, relwidth=1 / 4, relx=3 / 4, rely=0)

        self.info = tk.StringVar()
        self.info_label = tk.Label(self.pannel, textvariable=self.info)
        self.info_label.place(relheight=0.5, relwidth=1, relx=0, rely=0)
        self.action_button = tk.Button(
            self.pannel,
            text="Reroll",
            state="disabled",
            command=lambda: [self.game.roll(), self.render()],
        )
        self.action_button.place(relheight=0.5, relwidth=1, relx=0, rely=0.5)

        self.render()

    def render(self):
        info = f"R:{self.game.max_roll}\nT:{self.game.max_turn}\nS:{len(self.game.selected)}\n{self.game.win}"
        self.info.set(info)
        for widget in self.field.winfo_children():
            widget.destroy()
        for i, row in enumerate(self.game.grid):
            for j, dice in enumerate(row):
                tk.Button(
                    self.field,
                    text=dice,
                    command=lambda coord=(j, i): [
                        self.game.on_select(coord),
                        self.render(),
                    ],
                    bg=dice.color,
                    bd=5 if self.game.check_select((j, i)) else 1,
                    relief="ridge",
                ).place(
                    relheight=1 / self.game.size,
                    relwidth=1 / self.game.size,
                    relx=j * 1 / self.game.size,
                    rely=i * 1 / self.game.size,
                )
        self.action_button.config(
            state=(
                "disabled"
                if self.game.win != ""
                else ("active" if self.game.can_roll else "disabled")
            )
        )

    def restart(self):
        self.game.reset()
        self.render()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    d_face = 6
    g_size = 6
    UI(d_face=d_face, size=g_size).run()
