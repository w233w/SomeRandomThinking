import tkinter as tk
import random
from itertools import count
from typing import Literal

# unfinished
class Gun:
    ids = count()

    def __init__(self) -> None:
        self.capbility: int = 8
        self.id: int = next(Gun.ids)
        self.loaded: list[bool] = []

    def load(self, stage: int) -> None:
        pool: list[bool] = [True, False]
        self.loaded.clear()
        self.loaded.extend(pool)
        load_remain: int = 0
        if stage == 1:
            load_remain = random.randint(3, 4) - 2
        elif stage == 2:
            load_remain = random.randint(5, 6) - 2
        elif stage == 3:
            load_remain = random.randint(7, 8) - 2
        else:
            raise ValueError("Error on load")
        self.loaded.extend(random.sample(pool, load_remain))
        random.shuffle(self.loaded)

    @property
    def run_out_ammo(self):
        return len(self.loaded) <= 0

    def shoot(self) -> bool:
        return self.loaded.pop()

    def __str__(self) -> str:
        return "Gun"


class ItemTab:
    # 1 2     5 6
    # 3 4     7 8
    def __init__(self) -> None:
        self.items = ["空"] * 8

    def __str__(self) -> str:
        return "|".join(self.items)

    def get(self, id: int) -> str:
        return self.items[id]

    def add(self, *items: str) -> None:
        for item in items:
            if "空" in self.items:
                self.items[self.items.index("空")] = item

    def use(self, id: int) -> str:
        item = self.items[id]
        self.items[id] = "空"
        return item


class Controller:
    item_pool: tuple[str] = ("刀", "烟", "观", "酒", "锁")

    def __init__(self) -> None:
        self.stage: int = 1
        self.gun: Gun = Gun()

        self.turn: Literal["self", "enemy"] = "self"

        self.hp: int = 0
        self.items: ItemTab = ItemTab()

        self.e_hp: int = 0
        self.e_items: ItemTab = ItemTab()

        self.stage_start()

    def stage_start(self) -> None:
        if self.stage == 1:
            self.hp = 2
            self.e_hp = 2
        elif self.stage == 2:
            self.hp = 6
            self.hp = 6
        elif self.stage == 3:
            self.hp = 8
            self.hp = 8
        self.round_start()

    def round_start(self) -> None:
        self.gun.load(self.stage)
        # 0, 2, 4
        giving_item = 2 * (self.stage - 1)
        self.items.add(*random.sample(Controller.item_pool, giving_item))
        self.e_items.add(*random.sample(Controller.item_pool, giving_item))

    def turn_start(self) -> None:
        pass

    def use_item(self, id: int):
        pass

    def restart(self):
        self.__init__()

    def roll(self) -> None:
        pass

    def end_turn(self):
        self.turn += 1


class UI:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("mini")
        self.root.geometry("200x200")
        self.root.resizable(width=False, height=False)

        self.game = Controller()

        # 菜单
        self.menubar = tk.Menu(self.root)
        self.menu_start = tk.Menu(self.menubar, tearoff=0)
        self.menu_start.add_command(label="Restart", command=self.restart)
        self.menu_start.add_command(label="Help", command=None)
        self.menu_start.add_separator()
        self.menu_start.add_command(label="Exit", command=self.root.destroy)
        self.menubar.add_cascade(label="Game", menu=self.menu_start)
        self.root.config(menu=self.menubar)

        # 主界面，分上下两部分
        self.enemy_side = tk.Frame(self.root, bd=1, relief="raised")
        self.enemy_side.place(relheight=0.5, relwidth=1, relx=0, rely=0)
        self.self_side = tk.Frame(self.root, bd=1, relief="raised")
        self.self_side.place(relheight=0.5, relwidth=1, relx=0, rely=0.5)

        # 上部分，分左右两部分
        self.enemy_side_table = tk.Frame(self.enemy_side)
        self.enemy_side_table.place(relheight=1, relwidth=0.7, relx=0, rely=0)
        self.enemy_side_info = tk.Frame(self.enemy_side, bd=1, relief="raised")
        self.enemy_side_info.place(relheight=1, relwidth=0.3, relx=0.7, rely=0)

        # 上右部分
        self.enemy_info = tk.StringVar()
        self.enemy_info_label = tk.Label(self.enemy_side_info)
        self.enemy_info_label.pack(fill="both", expand=True)

        # 下部分，分左右两部分
        self.self_side_table = tk.Frame(self.self_side)
        self.self_side_table.place(relheight=1, relwidth=0.7, relx=0, rely=0)
        self.self_side_info = tk.Frame(self.self_side, bd=1, relief="raised")
        self.self_side_info.place(relheight=1, relwidth=0.3, relx=0.7, rely=0)

        # 下右部分
        self.self_info = tk.StringVar()
        self.self_info_label = tk.Label(self.self_side_info)
        self.self_info_label.pack(fill="both", expand=True)

        # 动态渲染
        self.render()

    def render(self):
        self_info_text = f"SELF\nHP: {self.game.hp}\n"
        self.self_info.set(self_info_text)
        enemy_info_text = f"ENEMY\nHP: {self.game.e_hp}\n"
        self.enemy_info.set(enemy_info_text)

        self.self_gun = tk.Button(self.self_side_table, text=self.game.gun)
        self.self_gun.place(relx=0.5, rely=0.5, anchor="center")
        self.self_gun_point_up = tk.Button(self.self_side_table, text="👆")
        self.self_gun_point_up.place(relx=0.5, rely=0, anchor="n")
        self.self_gun_point_down = tk.Button(self.self_side_table, text="👇")
        self.self_gun_point_down.place(relx=0.5, rely=1, anchor="s")

        self.self_items_left = tk.Frame(self.self_side_table)
        for i in range(4):
            tk.Button(
                self.self_items_left, text=self.game.items.get(i), command=None
            ).grid(row=i % 2, column=i // 2)
        self.self_items_left.place(relx=0, rely=0.5, anchor="w")
        self.self_items_right = tk.Frame(self.self_side_table)
        for i in range(4):
            tk.Button(
                self.self_items_right, text=self.game.items.get(i + 4), command=None
            ).grid(row=i % 2, column=i // 2)
        self.self_items_right.place(relx=1, rely=0.5, anchor="e")

    def restart(self):
        self.game.restart()
        self.render()

    def run(self) -> None:
        self.root.mainloop()


if __name__ == "__main__":
    UI().run()
