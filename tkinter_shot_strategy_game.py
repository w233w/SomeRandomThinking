import tkinter as tk
import random
from itertools import count
from typing import Literal

# g for gun game
# pve
# unfinished

# pvp 10hp vs 10hp
# 9-10hp no item, 6-8hp 2 items, 3-5hp 4 items.
# no handclif, once reach 2 hp, stop give smoke.
# switch side only by success shoot
# ammo from 4-6. once anyone reach 4 hp, ammo from 6-8.


class Gun:
    ids = count()

    def __init__(self) -> None:
        self.capbility: int = 8
        self.id: int = next(Gun.ids)
        self.loaded: list[bool] = []

    def reload(self, stage: int) -> None:
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
        self.loaded.extend(random.choices(pool, k=load_remain))
        random.shuffle(self.loaded)

    @property
    def run_out_ammo(self):
        return len(self.loaded) <= 0

    def shoot(self) -> bool:
        return self.loaded.pop()

    def __str__(self) -> str:
        return "Gun"

    def show(self) -> list[bool]:
        return sorted(self.loaded)


class ItemTab:
    # 1 2     5 6
    # 3 4     7 8
    def __init__(self) -> None:
        self.items = ["   "] * 8

    def __str__(self) -> str:
        return "|".join(self.items)

    def get(self, id: int) -> str:
        return self.items[id]

    def add(self, *items: str) -> None:
        for item in items:
            if "   " in self.items:
                self.items[self.items.index("   ")] = item

    def use(self, id: int) -> str:
        item = self.items[id]
        self.items[id] = "   "
        return item


class Controller:
    item_pool: tuple[str] = ("刀", "烟", "观", "酒", "锁")

    def __init__(self) -> None:
        self.stage: int = 1
        self.gun: Gun = Gun()

        self.turn: bool = False  # flag: 0 for self, 1 for enemy

        self.hp: int = 0
        self.items: ItemTab = ItemTab()

        self.e_hp: int = 0
        self.e_items: ItemTab = ItemTab()

        self.gun_picked: bool = False
        self.last_shoot: bool = False
        self.doubled: bool = False

        self.stage_start()

    def pick_gun(self) -> None:
        if not self.game_over:
            self.gun_picked = True

    def stage_start(self) -> None:
        if self.stage == 1:
            self.hp = 3
            self.e_hp = 3
        elif self.stage == 2:
            self.hp = 6
            self.e_hp = 6
        elif self.stage == 3:
            self.hp = 8
            self.e_hp = 8
        self.round_start()

    def round_start(self) -> None:
        self.gun.reload(self.stage)
        # 0, 2, 4
        giving_item = 2 * (self.stage - 1)
        self.items.add(*random.sample(Controller.item_pool, giving_item))
        self.e_items.add(*random.sample(Controller.item_pool, giving_item))
        self.turn_start()

    def turn_start(self) -> None:
        self.turn = False

    def shoot(self, side: Literal["player", "enemy"]):
        self.last_shoot: bool = self.gun.shoot()
        if side == "player":
            self.hp -= self.last_shoot * (1 + self.doubled)
        elif side == "enemy":
            self.e_hp -= self.last_shoot * (1 + self.doubled)
        self.doubled = False
        self.gun_picked = False
        self.end_turn()

    def use_item(self, id: int):
        item = self.items.use(id)
        match item:
            case "刀":
                self.doubled = True
            case "烟":
                pass
            case "观":
                pass
            case "酒":
                pass
            case "锁":
                pass
            case "   ":
                pass
            case _:
                raise ValueError("Item Error")

    def restart(self):
        self.__init__()

    @property
    def stage_over(self) -> bool:
        return self.e_hp <= 0

    @property
    def game_over(self) -> bool:
        return self.hp <= 0

    def end_turn(self):
        self.turn = not self.turn
        if self.gun.run_out_ammo:
            self.gun.reload(self.stage)
        if self.stage_over:
            self.stage += 1
            if self.game_over:
                pass
            self.stage_start()
            print(self.e_hp)


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

        # 主界面，分左右两部分
        self.table = tk.Frame(self.root, bd=1, relief="raised")
        self.table.place(relheight=1, relwidth=0.7, relx=0, rely=0)
        self.panel = tk.Frame(self.root, bd=1, relief="raised")
        self.panel.place(relheight=1, relwidth=0.3, relx=0.7, rely=0)

        # 左部分，分上下两部分
        self.enemy_side_table = tk.Frame(self.table, bd=1, relief="raised")
        self.enemy_side_table.place(relheight=0.5, relwidth=1, relx=0, rely=0)
        self.player_side_table = tk.Frame(self.table, bd=1, relief="raised")
        self.player_side_table.place(relheight=0.5, relwidth=1, relx=0, rely=0.5)

        # 左上部分
        self.enemy_gun_button = tk.Button(
            self.enemy_side_table,
            text=self.game.gun,
            state="disabled",
        )
        self.enemy_gun_button.place(relx=0.5, rely=0.5, anchor="center")

        self.enemy_gun_point_up = tk.Button(
            self.enemy_side_table,
            text="👆",
            state="disabled",
        )
        self.enemy_gun_point_up.place(relx=0.5, rely=0, anchor="n")
        self.enemy_gun_point_down = tk.Button(
            self.enemy_side_table,
            text="👇",
            state="disabled",
        )
        self.enemy_gun_point_down.place(relx=0.5, rely=1, anchor="s")

        self.enemy_items_left = tk.Frame(self.enemy_side_table)
        for i in range(4):
            tk.Button(
                self.enemy_items_left,
                text=self.game.e_items.get(i),
                state="disabled",
            ).grid(row=i // 2, column=i % 2)
        self.enemy_items_left.place(relx=0, rely=0.5, anchor="w")

        self.enemy_items_right = tk.Frame(self.enemy_side_table)
        for i in range(4):
            tk.Button(
                self.enemy_items_right,
                text=self.game.e_items.get(i + 4),
                state="disabled",
            ).grid(row=i % 2, column=i // 2)
        self.enemy_items_right.place(relx=1, rely=0.5, anchor="e")

        # 左下部分
        self.player_gun_button = tk.Button(
            self.player_side_table,
            text=self.game.gun,
            command=lambda: [self.game.pick_gun(), self.render()],
        )
        self.player_gun_button.place(relx=0.5, rely=0.5, anchor="center")

        self.player_gun_point_up = tk.Button(
            self.player_side_table,
            text="👆",
            command=lambda: [self.game.shoot("enemy"), self.render()],
            state="active" if self.game.gun_picked else "disabled",
        )
        self.player_gun_point_up.place(relx=0.5, rely=0, anchor="n")
        self.player_gun_point_down = tk.Button(
            self.player_side_table,
            text="👇",
            command=lambda: [self.game.shoot("player"), self.render()],
            state="active" if self.game.gun_picked else "disabled",
        )
        self.player_gun_point_down.place(relx=0.5, rely=1, anchor="s")

        self.player_items_left = tk.Frame(self.player_side_table)
        for i in range(4):
            tk.Button(
                self.player_items_left,
                text=self.game.items.get(i),
                command=lambda id=i: [self.game.use_item(id), self.render()],
            ).grid(row=i // 2, column=i % 2)
        self.player_items_left.place(relx=0, rely=0.5, anchor="w")
        self.player_items_right = tk.Frame(self.player_side_table)
        for i in range(4):
            tk.Button(
                self.player_items_right,
                text=self.game.items.get(i + 4),
                command=lambda id=i + 4: [self.game.use_item(id), self.render()],
            ).grid(row=i % 2, column=i // 2)
        self.player_items_right.place(relx=1, rely=0.5, anchor="e")

        # 右部分，分上中下三部分
        self.enemy_side_panel = tk.Frame(self.panel, bd=1, relief="raised")
        self.enemy_side_panel.place(relheight=0.4, relwidth=1, relx=0, rely=0)
        self.gun_panel = tk.Frame(self.panel, bd=1, relief="raised")
        self.gun_panel.place(relheight=0.2, relwidth=1, relx=0, rely=0.4)
        self.player_side_panel = tk.Frame(self.panel, bd=1, relief="raised")
        self.player_side_panel.place(relheight=0.4, relwidth=1, relx=0, rely=0.6)

        # 右上部分
        self.enemy_info = tk.StringVar()
        self.enemy_info_label = tk.Label(
            self.enemy_side_panel, textvariable=self.enemy_info
        )
        self.enemy_info_label.pack(fill="both", expand=True)

        # 右中部分

        # 右下部分
        self.player_info = tk.StringVar()
        self.player_info_label = tk.Label(
            self.player_side_panel, textvariable=self.player_info
        )
        self.player_info_label.pack(fill="both", expand=True)

        # 动态渲染
        self.render()

    def render(self):
        # 更新双方信息
        player_info_text = f"SELF\nHP: {self.game.hp}\n"
        self.player_info.set(player_info_text)
        enemy_info_text = f"ENEMY\nHP: {self.game.e_hp}\n"
        self.enemy_info.set(enemy_info_text)
        # 重绘弹药信息
        for widget in self.gun_panel.winfo_children():
            widget.destroy()
        for i, b in enumerate(self.game.gun.show()):
            tk.Label(
                self.gun_panel,
                bg="pink" if b else "lightgreen",
                bd=0.5,
                relief="solid",
            ).place(relheight=1, relwidth=1 / 8, relx=i / 8, rely=0)
        # 重绘玩家物品
        for widget in self.player_items_left.winfo_children():
            widget.destroy()
        for i in range(4):
            tk.Button(
                self.player_items_left,
                text=self.game.items.get(i),
                command=lambda id=i: [self.game.use_item(id), self.render()],
            ).grid(row=i // 2, column=i % 2)
        for widget in self.player_items_right.winfo_children():
            widget.destroy()
        for i in range(4):
            tk.Button(
                self.player_items_right,
                text=self.game.items.get(i + 4),
                command=lambda id=i + 4: [self.game.use_item(id), self.render()],
            ).grid(row=i % 2, column=i // 2)
        # 改变玩家按钮状态
        self.player_gun_button.config(
            state="disabled" if self.game.gun_picked else "active"
        )
        self.player_gun_point_up.config(
            state="active" if self.game.gun_picked else "disabled"
        )
        self.player_gun_point_down.config(
            state="active" if self.game.gun_picked else "disabled"
        )

    def restart(self):
        self.game.restart()
        self.render()

    def run(self) -> None:
        self.root.mainloop()


if __name__ == "__main__":
    UI().run()
