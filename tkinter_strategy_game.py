import tkinter as tk
import random
from itertools import count
from typing import Literal

# 恶魔轮盘赌pvp
# unfinished

# pvp 10hp vs 10hp
# 9-10hp no item, 6-8hp 2 items, 3-5hp 4 items.
# no handclif, once reach 2 hp, stop give smoke.
# switch side only by success shoot
# ammo from 4-6. once anyone reach 4 hp, ammo from 6-8.


class Gun:
    def __init__(self) -> None:
        self.capbility: int = 8
        self.loaded: list[bool] = []

    # 至少一空一实，其余随机。
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
    def out_of_ammo(self):
        return len(self.loaded) <= 0

    def shoot(self) -> bool:
        return self.loaded.pop()

    def show_next(self) -> bool:
        return self.loaded[-1]

    def __str__(self) -> str:
        return "Gun"

    def show_sorted(self) -> list[bool]:
        return sorted(self.loaded)


class ItemTab:
    # 1 2     5 6
    # 3 4     7 8
    def __init__(self) -> None:
        self.items = ["   "] * 8

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

    def to_gress(self):
        while "烟" in self.items:
            self.items[self.items.index("烟")] = "草"

    def to_toxin(self):
        while "烟" in self.items:
            self.items[self.items.index("烟")] = "毒"

    def to_last_stage(self):
        pass


class Character:
    def __init__(self) -> None:
        self.max_hp = 9
        self.hp = 8
        self.items = ItemTab()
        self.items.add("酒")

        self.last_chance_used = False
        self.locked = False
        self.purity = True

    def use_item(self, index: int):
        return self.items.use(index)

    def restore(self):
        if self.hp < self.max_hp:
            self.hp += 1

    def nerf(self, level: Literal[1, 2]):
        if level == 1:
            self.items.to_gress()
        elif level == 2:
            self.items.to_toxin()
        else:
            return

    @property
    def stage(self) -> Literal[1, 2, 3]:
        if self.hp <= 3:
            return 3
        elif 3 < self.hp <= 6:
            return 2
        else:
            return 1


class Controller:
    item_pool: dict[int, tuple[str]] = {
        1: ("烟", "酒", "观"),
        2: ("烟", "酒", "观", "刀"),
        3: ("烟", "酒", "观", "刀", "锁"),
        4: ("烟", "酒", "刀"),
    }
    item_num: dict[int, int] = {
        1: 1,
        2: 2,
        3: 4,
    }

    def __init__(self) -> None:
        self.gun: Gun = Gun()

        self.current_p: int = 1  # flag: 1 for p1, 2 for p2

        self.p1 = Character()
        self.p2 = Character()
        self.p_map: dict[int, Character] = {
            1: self.p1,
            2: self.p2,
        }

        self.gun_picked: bool = False
        self.last_shoot: Literal[True, False, "?"] = "?"
        self.doubled: bool = False
        self.start_giving_item: bool = False
        self.last_stage: bool = False

        self.new_round()

    def new_round(self) -> None:
        self.gun.reload(max(self.p1.stage, self.p2.stage))

        if self.p1.stage == self.p2.stage == 3:
            self.p1.max_hp = 3
            self.p1.items.to_last_stage()
            self.p2.max_hp = 3
            self.p2.items.to_last_stage()

        if not self.p_map[self.current_p].purity:
            self.p1.purity = True
            self.p2.purity = True
            self.new_turn()

        if not self.start_giving_item:
            if self.p1.stage > 1 or self.p2.stage > 1:
                self.start_giving_item = True

        if self.start_giving_item:
            if not self.last_stage:
                self.p1.items.add(
                    *random.sample(
                        Controller.item_pool[self.p1.stage],
                        Controller.item_num[self.p1.stage],
                    )
                )
                self.p2.items.add(
                    *random.sample(
                        Controller.item_pool[self.p2.stage],
                        Controller.item_num[self.p2.stage],
                    )
                )
            else:
                self.p1.items.add(*random.sample(Controller.item_pool[4], 4))
                self.p2.items.add(*random.sample(Controller.item_pool[4], 4))

        stronger = None
        if self.p1.stage < self.p2.stage:
            stronger = self.p1
        elif self.p2.stage < self.p1.stage:
            stronger = self.p2
        if stronger is not None:
            differ: Literal[1, 2] = abs(
                self.p_map[self.current_p].stage - self.p_map[3 - self.current_p].stage
            )
            stronger.nerf(differ)

    def new_turn(self) -> None:
        if self.p_map[3 - self.current_p].locked:
            self.p_map[3 - self.current_p].locked = False
        else:
            self.current_p = 3 - self.current_p

    # 全部三种行动： 拿枪，射击，用道具。拿起枪后就不能使用道具了。
    def pick_gun(self) -> None:
        self.last_shoot = "?"
        if not self.game_over:
            self.gun_picked = True

    def shoot(self, side: Literal["self", "opponent"]):
        self.last_shoot = self.gun.shoot()
        if self.last_shoot:
            if side == "self":
                self.p_map[self.current_p].hp -= 1 + self.doubled
            else:
                self.p_map[3 - self.current_p].hp -= 1 + self.doubled
            self.new_turn()
        else:
            if side == "opponent":
                self.new_turn()
        self.doubled = False
        self.gun_picked = False
        if self.gun.out_of_ammo:
            self.new_round()

    def use_item(self, index):
        print(index)
        item = self.p_map[self.current_p].use_item(index)
        match item:
            case "烟":
                self.p_map[self.current_p].restore()
            case "酒":
                self.last_shoot = self.gun.shoot()
            case "观":
                self.last_shoot = self.gun.show_next()
            case "刀":
                self.doubled = True
            case "锁":
                self.p_map[3 - self.current_p].locked = True
            case "草":
                if random.randint(0, 1) == 1:
                    self.p_map[self.current_p].restore()
            case "毒":
                if random.randint(0, 1) == 1:
                    self.p_map[self.current_p].restore()
                else:
                    self.p_map[self.current_p].hp -= 1

    def restart(self):
        self.__init__()

    @property
    def game_over(self) -> bool:
        return self.p1.hp <= 0 or self.p2.hp <= 0


class UI:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("mini")
        self.root.geometry("300x200")
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
        self.table.place(relheight=1, relwidth=0.6, relx=0, rely=0)
        self.panel = tk.Frame(self.root, bd=1, relief="raised")
        self.panel.place(relheight=1, relwidth=0.4, relx=0.6, rely=0)

        # 左部分，分上下两部分
        self.p2_side_table = tk.Frame(self.table, bd=1, relief="raised")
        self.p2_side_table.place(relheight=0.5, relwidth=1, relx=0, rely=0)
        self.p1_side_table = tk.Frame(self.table, bd=1, relief="raised")
        self.p1_side_table.place(relheight=0.5, relwidth=1, relx=0, rely=0.5)

        # 左上部分
        self.p2_gun_button = tk.Button(
            self.p2_side_table,
            text="Gun",
            command=lambda: [self.game.pick_gun(), self.render()],
        )
        self.p2_gun_button.place(relx=0.5, rely=0.5, anchor="center")

        self.p2_gun_point_up = tk.Button(
            self.p2_side_table,
            text="👆",
            command=lambda: [self.game.shoot("self"), self.render()],
        )
        self.p2_gun_point_up.place(relx=0.5, rely=0, anchor="n")
        self.p2_gun_point_down = tk.Button(
            self.p2_side_table,
            text="👇",
            command=lambda: [self.game.shoot("opponent"), self.render()],
        )
        self.p2_gun_point_down.place(relx=0.5, rely=1, anchor="s")

        self.p2_items_left = tk.Frame(self.p2_side_table)
        for i in range(4):
            tk.Button(
                self.p2_items_left,
                text=self.game.p2.items.get(i),
                state="disabled",
            ).grid(row=i // 2, column=i % 2)
        self.p2_items_left.place(relx=0, rely=0.5, anchor="w")

        self.p2_items_right = tk.Frame(self.p2_side_table)
        for i in range(4):
            tk.Button(
                self.p2_items_right,
                text=self.game.p2.items.get(i + 4),
                state="disabled",
            ).grid(row=i % 2, column=i // 2)
        self.p2_items_right.place(relx=1, rely=0.5, anchor="e")

        # 左下部分
        self.p1_gun_button = tk.Button(
            self.p1_side_table,
            text="Gun",
            command=lambda: [self.game.pick_gun(), self.render()],
        )
        self.p1_gun_button.place(relx=0.5, rely=0.5, anchor="center")

        self.p1_gun_point_up = tk.Button(
            self.p1_side_table,
            text="👆",
            command=lambda: [self.game.shoot("opponent"), self.render()],
        )
        self.p1_gun_point_up.place(relx=0.5, rely=0, anchor="n")
        self.p1_gun_point_down = tk.Button(
            self.p1_side_table,
            text="👇",
            command=lambda: [self.game.shoot("self"), self.render()],
        )
        self.p1_gun_point_down.place(relx=0.5, rely=1, anchor="s")

        self.p1_items_left = tk.Frame(self.p1_side_table)
        self.p1_items_left.place(relx=0, rely=0.5, anchor="w")
        self.p1_items_right = tk.Frame(self.p1_side_table)
        self.p1_items_right.place(relx=1, rely=0.5, anchor="e")

        # 右部分，分上中下三部分
        self.p2_side_panel = tk.Frame(self.panel, bd=1, relief="raised")
        self.p2_side_panel.place(relheight=0.4, relwidth=1, relx=0, rely=0)
        self.gun_panel = tk.Frame(self.panel, bd=1, relief="raised")
        self.gun_panel.place(relheight=0.2, relwidth=1, relx=0, rely=0.4)
        self.p1_side_panel = tk.Frame(self.panel, bd=1, relief="raised")
        self.p1_side_panel.place(relheight=0.4, relwidth=1, relx=0, rely=0.6)

        # 右上部分
        self.p2_info = tk.StringVar()
        self.p2_info_label = tk.Label(self.p2_side_panel, textvariable=self.p2_info)
        self.p2_info_label.pack(fill="both", expand=True)

        # 右中部分, 分左右两部分
        self.last_shoot_frame = tk.Frame(self.gun_panel, bd=2, relief="solid")
        self.last_shoot_frame.place(relheight=1, relwidth=2 / 10, relx=0, rely=0)
        self.last_shoot = tk.Label(self.last_shoot_frame)
        self.last_shoot.pack(fill="both", expand=True)
        self.ammo_pannal = tk.Frame(self.gun_panel)
        self.ammo_pannal.place(relheight=1, relwidth=8 / 10, relx=2 / 10, rely=0)

        # 右下部分
        self.p1_info = tk.StringVar()
        self.p1_info_label = tk.Label(self.p1_side_panel, textvariable=self.p1_info)
        self.p1_info_label.pack(fill="both", expand=True)

        # 动态渲染
        self.render()

    def render(self):
        # 更新双方信息
        p1_info_text = f"SELF\nHP: {self.game.p1.hp}\nSTAGE: {self.game.p1.stage}\n"
        if self.game.p1.locked:
            p1_info_text += "LOCKED"
        self.p1_info.set(p1_info_text)
        p2_info_text = f"ENEMY\nHP: {self.game.p2.hp}\nSTAGE: {self.game.p2.stage}\n"
        if self.game.p2.locked:
            p2_info_text += "LOCKED"
        self.p2_info.set(p2_info_text)
        # 重绘弹药信息
        if self.game.last_shoot == "?":
            self.last_shoot.config(bg=self.root.cget("bg"), text="?")
        else:
            self.last_shoot.config(
                text="", bg="pink" if self.game.last_shoot else "lightgreen"
            )
        for widget in self.ammo_pannal.winfo_children():
            widget.destroy()
        for i, b in enumerate(self.game.gun.show_sorted()):
            tk.Label(
                self.ammo_pannal,
                bg="pink" if b else "lightgreen",
                bd=0.5,
                relief="solid",
            ).place(relheight=1, relwidth=1 / 8, relx=i / 8, rely=0)
        # 重绘玩家物品
        for widget in self.p1_items_left.winfo_children():
            widget.destroy()
        for i in range(4):
            tk.Button(
                self.p1_items_left,
                text=self.game.p1.items.get(i),
                command=lambda id=i: [self.game.use_item(id), self.render()],
                state=(
                    ("disabled" if self.game.gun_picked else "active")
                    if self.game.current_p == 1
                    else "disabled"
                ),
            ).grid(row=i // 2, column=i % 2)
        for widget in self.p1_items_right.winfo_children():
            widget.destroy()
        for i in range(4):
            tk.Button(
                self.p1_items_right,
                text=self.game.p1.items.get(i + 4),
                command=lambda id=i + 4: [self.game.use_item(id), self.render()],
                state=(
                    ("disabled" if self.game.gun_picked else "active")
                    if self.game.current_p == 1
                    else "disabled"
                ),
            ).grid(row=i // 2, column=i % 2)
        for widget in self.p2_items_left.winfo_children():
            widget.destroy()
        for i in range(4):
            tk.Button(
                self.p2_items_left,
                text=self.game.p2.items.get(i),
                command=lambda id=i: [self.game.use_item(id), self.render()],
                state=(
                    ("disabled" if self.game.gun_picked else "active")
                    if self.game.current_p == 2
                    else "disabled"
                ),
            ).grid(row=i // 2, column=i % 2)
        for widget in self.p2_items_right.winfo_children():
            widget.destroy()
        for i in range(4):
            tk.Button(
                self.p2_items_right,
                text=self.game.p2.items.get(i + 4),
                command=lambda id=i + 4: [self.game.use_item(id), self.render()],
                state=(
                    ("disabled" if self.game.gun_picked else "active")
                    if self.game.current_p == 2
                    else "disabled"
                ),
            ).grid(row=i // 2, column=i % 2)
        # 改变玩家按钮状态
        self.p1_gun_button.config(
            state=(
                ("disabled" if self.game.gun_picked else "active")
                if self.game.current_p == 1
                else "disabled"
            )
        )
        self.p1_gun_point_up.config(
            state=(
                ("active" if self.game.gun_picked else "disabled")
                if self.game.current_p == 1
                else "disabled"
            )
        )
        self.p1_gun_point_down.config(
            state=(
                ("active" if self.game.gun_picked else "disabled")
                if self.game.current_p == 1
                else "disabled"
            )
        )
        self.p2_gun_button.config(
            state=(
                ("disabled" if self.game.gun_picked else "active")
                if self.game.current_p == 2
                else "disabled"
            )
        )
        self.p2_gun_point_up.config(
            state=(
                ("active" if self.game.gun_picked else "disabled")
                if self.game.current_p == 2
                else "disabled"
            )
        )
        self.p2_gun_point_down.config(
            state=(
                ("active" if self.game.gun_picked else "disabled")
                if self.game.current_p == 2
                else "disabled"
            )
        )

    def restart(self):
        self.game.restart()
        self.render()

    def run(self) -> None:
        self.root.mainloop()


if __name__ == "__main__":
    UI().run()
