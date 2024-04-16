import tkinter as tk
import random
import numpy as np
from itertools import product


# Minesweeper-like game
# Number show how many bomb around in 8 neighbors.
# "+"， "➕", "x", "❌" help finding reward.
#   "+" meaning no reward in same row and col, "➕" meaning have reward.
#   "x" meaning no reward in cross "❌" meaning have reward in cross.
# "🎁", "👑" are reward, find them all to win.
# find any reward will expose one bomb without explode.
# maximum 2 bombs can explode before lose.
# first click must show a number.

# TODO: Win rate are low, need modify rule.


class Controller:
    def __init__(self) -> None:
        self.size: int = 6
        self.grid = np.zeros((self.size, self.size), dtype=np.str_)
        self.generated: bool = False
        self.exposed: set[tuple[int, int]] = set()
        self.exploded: set[tuple[int, int]] = set()
        self.reward_get: set[tuple[int, int]] = set()
        self.normal_reward: set[tuple[int, int]] = set()
        self.special_reward: set[tuple[int, int]] = set()
        self.bomb: set[tuple[int, int]] = set()
        self.number_hint: set[tuple[int, int]] = set()
        self.mark_hint: set[tuple[int, int]] = set()
        self.hp = 3

    def reset(self):
        self.__init__()

    @property
    def game_over(self):
        first = self.hp <= 0
        all_reward = self.normal_reward.union(self.special_reward)
        second = all_reward.intersection(self.exposed) == all_reward
        return self.generated and (first or second)

    def on_first_click(self, coord: tuple[int, int] = None):
        pool = list(product(range(self.size), range(self.size)))
        pool.remove(coord)
        self.normal_reward = self.normal_reward.union(random.sample(pool, k=3))
        pool = [p for p in pool if p not in self.normal_reward]
        self.special_reward = self.special_reward.union(random.sample(pool, k=1))
        pool = [p for p in pool if p not in self.special_reward]
        self.bomb = self.bomb.union(random.sample(pool, k=12))
        pool = [p for p in pool if p not in self.bomb]
        self.mark_hint = self.mark_hint.union(random.sample(pool, k=8))
        self.number_hint = set([p for p in pool if p not in self.mark_hint])
        self.number_hint.add(coord)

        for row, col in self.normal_reward:
            self.grid[row][col] = "🎁"
        for row, col in self.special_reward:
            self.grid[row][col] = "👑"
        for row, col in self.bomb:
            self.grid[row][col] = "💣"

        for row, col in self.number_hint:
            count = 0
            for del_r, del_c in product([-1, 0, 1], [-1, 0, 1]):
                if (del_r, del_c) != (0, 0):
                    new_r, new_c = row + del_r, col + del_c
                    if 0 <= new_r < 6 and 0 <= new_c < 6:
                        if self.grid[new_r][new_c] == "💣":
                            count += 1
            self.grid[row][col] = str(count)

        for row, col in self.mark_hint:
            cross = bool(random.randint(0, 1))
            if cross:
                collection = []
                for del_r, del_c in [(1, 1), (-1, -1), (1, -1), (-1, 1)]:
                    new_r, new_c = row + del_r, col + del_c
                    while 0 <= new_r < 6 and 0 <= new_c < 6:
                        collection.append(self.grid[new_r][new_c])
                        new_r, new_c = new_r + del_r, new_c + del_c
                if "🎁" in collection or "👑" in collection:
                    self.grid[row][col] = "❌"
                else:
                    self.grid[row][col] = "X"
            else:
                h = self.grid[:, col: col + 1]
                v = self.grid[row: row + 1, :]
                if "🎁" in h or "🎁" in v or "👑" in h or "👑" in v:
                    self.grid[row][col] = "➕"
                else:
                    self.grid[row][col] = "+"

        self.generated = True

    def on_click(self, coord: tuple[int, int]):
        if not self.generated:
            self.on_first_click(coord)
        self.exposed.add(coord)
        row, col = coord
        if self.grid[row][col] == "💣":
            self.hp -= 1
            self.exploded.add(coord)
        elif self.grid[row][col] in ["🎁", "👑"]:
            pool = list(self.bomb.difference(self.exposed))
            self.exposed.add(random.choice(pool))
            self.reward_get.add(coord)


class UI:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("mini")
        self.root.geometry("150x150")
        self.root.resizable(width=False, height=False)

        self.game = Controller()

        # 菜单
        self.menubar = tk.Menu(self.root)
        self.menu_start = tk.Menu(self.menubar, tearoff=0)
        self.menu_start.add_command(label="Restart", command=self.restart)
        self.menu_start.add_command(label="Heck", command=self.heck)
        self.menu_start.add_separator()
        self.menu_start.add_command(label="Exit", command=self.root.destroy)
        self.menubar.add_cascade(label="Game", menu=self.menu_start)
        self.root.config(menu=self.menubar)

        self.render()

    def render(self):
        for widget in self.root.winfo_children():
            if not isinstance(widget, tk.Menu):
                widget.destroy()
        for i, row in enumerate(self.game.grid):
            for j, _ in enumerate(row):
                coord = (i, j)
                color = None
                if coord in self.game.exposed:
                    if coord in self.game.exploded:
                        color = "pink"
                    elif coord in self.game.reward_get:
                        color = "gold1"
                tk.Button(
                    self.root,
                    text=(
                        ""
                        if coord not in self.game.exposed and not self.game.game_over
                        else self.game.grid[i][j]
                    ),
                    command=lambda c=coord: [
                        self.game.on_click(c),
                        self.render(),
                    ],
                    bg=color,
                    relief="ridge",
                    state=(
                        "disabled"
                        if coord in self.game.exposed or self.game.game_over
                        else "active"
                    ),
                ).place(
                    relheight=1 / self.game.size,
                    relwidth=1 / self.game.size,
                    relx=j * 1 / self.game.size,
                    rely=i * 1 / self.game.size,
                )

    def restart(self):
        self.game.reset()
        self.render()

    def heck(self):
        print(self.game.grid)

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    UI().run()
