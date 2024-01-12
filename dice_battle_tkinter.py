import tkinter as tk
import random
from itertools import count


class Dice:
    ids = count()

    def __init__(self, faces: int = 6) -> None:
        self.faces = faces
        self.id: int = next(Dice.ids)
        self.values = list(range(1, faces + 1))
        self.last_roll: int = None

    def __str__(self) -> str:
        return f"D{self.faces}"

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, Dice):
            raise TypeError(f"Can't compare dice with {o.__class__}")
        return self.faces == o.faces

    def __lt__(self, o: object) -> bool:
        if not isinstance(o, Dice):
            raise TypeError(f"Can't compare dice with {o.__class__}")
        return self.faces < o.faces

    def roll(self) -> int:
        self.last_roll = random.choice(self.values)
        return self.last_roll


class Controller:
    def __init__(self) -> None:
        self.turn: int = 0

        self.dices: int = [6, 6, 5, 4, 4]
        self.available: list[Dice] = []
        for d_face in self.dices:
            self.available.append(Dice(d_face))
        self.on_board: list[Dice] = []
        self.rolleded: list[Dice] = []
        self.resting: list[Dice] = []
        self.hp: int = 20

        self.can_roll: bool = False
        self.rolled: bool = False

        self.e_dices: int = [6, 6, 6, 6, 6]
        self.e_available: list[Dice] = []
        for e_d_face in self.e_dices:
            self.e_available.append(Dice(e_d_face))
        self.e_on_board: list[Dice] = []
        self.e_rolleded: list[Dice] = []
        self.e_resting: list[Dice] = []
        self.e_hp: int = 20

        self.self_last_roll: list[int] = []
        self.self_last_regen: list[int] = []
        self.self_last_lose: list[int] = []
        self.enemy_last_roll: list[int] = []
        self.enemy_last_regen: list[int] = []
        self.enemy_last_lose: list[int] = []

    def restart(self):
        self.__init__()

    @property
    def game_end(self):
        return self.hp <= 0 or self.e_hp <= 0

    def on_select(self, dice):
        if not self.game_end:
            self.on_board.append(dice)
            self.available.remove(dice)
            self.can_roll = 4 >= len(self.on_board) >= 1

    def on_unselect(self, dice):
        if not self.game_end:
            self.available.append(dice)
            self.on_board.remove(dice)
            self.can_roll = 4 >= len(self.on_board) >= 1

    def enemy_strat(self) -> None:
        e_roll_num = random.randint(1, min(4, len(self.e_available)))
        for _ in range(e_roll_num):
            self.e_on_board.append(self.e_available.pop())

    def roll(self) -> None:
        values = [dice.roll() for dice in self.on_board]
        regen = max([v for v in values if values.count(v) > 1] + [0])
        self.rolleded.extend(self.on_board)
        self.on_board.clear()
        self.can_roll = False
        self.rolled = True

        self.enemy_strat()

        e_values = [dice.roll() for dice in self.e_on_board]
        e_regen = max([v for v in e_values if e_values.count(v) > 1] + [0])
        self.e_rolleded.extend(self.e_on_board)
        self.e_on_board.clear()

        self.self_last_roll.append(sum(values))
        self.self_last_regen.append(regen)
        self.enemy_last_roll.append(sum(e_values))
        self.enemy_last_regen.append(e_regen)

        if self.self_last_roll[-1] == self.enemy_last_roll[-1]:
            self.self_last_lose.append(0)
            self.enemy_last_lose.append(0)
        elif self.self_last_roll[-1] > self.enemy_last_roll[-1]:
            self.enemy_last_lose.append(
                self.self_last_roll[-1] - self.enemy_last_roll[-1]
            )
            self.self_last_lose.append(0)
        elif self.self_last_roll[-1] < self.enemy_last_roll[-1]:
            self.self_last_lose.append(
                self.enemy_last_roll[-1] - self.self_last_roll[-1]
            )
            self.enemy_last_lose.append(0)

    def end_turn(self):
        self.turn += 1

        self.hp += self.self_last_regen[-1]
        self.hp -= self.self_last_lose[-1]
        self.e_hp += self.enemy_last_regen[-1]
        self.e_hp -= self.enemy_last_lose[-1]

        self.rolled = False
        self.available.extend(self.resting)
        self.resting.clear()
        self.resting.extend(self.rolleded)
        self.rolleded.clear()

        self.e_available.extend(self.e_resting)
        self.e_resting.clear()
        self.e_resting.extend(self.e_rolleded)
        self.e_rolleded.clear()


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
        self.upframe = tk.Frame(self.root, bd=1, relief="raised")
        self.upframe.place(relheight=0.4, relwidth=1, relx=0, rely=0)
        self.downframe = tk.Frame(self.root, bd=1, relief="raised")
        self.downframe.place(relheight=0.6, relwidth=1, relx=0, rely=0.4)

        # 上部分-enemy，分左右两部分
        self.enemy_field = tk.Frame(self.upframe)
        self.enemy_field.place(relheight=1, relwidth=0.7, relx=0, rely=0)
        self.enemy_info = tk.Frame(self.upframe, bd=1, relief="raised")
        self.enemy_info.place(relheight=1, relwidth=0.3, relx=0.7, rely=0)

        # enemy左部分，分上下两部分
        self.enemy_field_available = tk.Frame(self.enemy_field)
        self.enemy_field_available.place(relheight=0.5, relwidth=1, relx=0, rely=0)
        self.enemy_field_onboard = tk.Frame(self.enemy_field)
        self.enemy_field_onboard.place(relheight=0.5, relwidth=1, relx=0, rely=0.5)

        # enemy右部分-enemyinfo,hp
        self.enemy_info_text = tk.StringVar()
        self.enemy_info_text_label = tk.Label(
            self.enemy_info, textvariable=self.enemy_info_text
        )
        self.enemy_info_text_label.pack(fill="both", expand=True)

        # 下部分-self， 分左右下三部分
        self.self_field = tk.Frame(self.downframe)
        self.self_field.place(relheight=2 / 3, relwidth=0.7, relx=0, rely=0)
        self.self_info = tk.Frame(self.downframe, bd=1, relief="raised")
        self.self_info.place(relheight=2 / 3, relwidth=0.3, relx=0.7, rely=0)
        self.self_action_button = tk.Frame(self.downframe)
        self.self_action_button.place(relheight=1 / 3, relwidth=1, relx=0, rely=2 / 3)

        # self左部分-self台面，分上下两部分
        self.self_field_onboard = tk.Frame(self.self_field)
        self.self_field_onboard.place(relheight=0.5, relwidth=1, relx=0, rely=0)
        self.self_field_available = tk.Frame(self.self_field)
        self.self_field_available.place(relheight=0.5, relwidth=1, relx=0, rely=0.5)

        # self右部分-selfinfo，hp
        self.self_info_text = tk.StringVar()
        self.self_info_text_label = tk.Label(
            self.self_info, textvariable=self.self_info_text
        )
        self.self_info_text_label.pack(fill="both", expand=True)

        # self下部分，action
        self.roll_bottom = tk.Button(
            self.self_action_button,
            text="Roll",
            state="disabled",
            command=lambda: [self.game.roll(), self.render()],
        )
        self.roll_bottom.place(relheight=1, relwidth=0.5, relx=0, rely=0)
        self.end_bottom = tk.Button(
            self.self_action_button,
            text="Turn End",
            state="disabled",
            command=lambda: [self.game.end_turn(), self.render()],
        )
        self.end_bottom.place(relheight=1, relwidth=0.5, relx=0.5, rely=0)

        # 动态渲染
        self.render()

    def render(self):
        hp_text = f"You\nHP: {self.game.hp}\n"
        e_hp_text = f"Enemy\nHP: {self.game.e_hp}\n"
        if self.game.game_end:
            if self.game.hp > 0:
                hp_text += "Win!"
                e_hp_text += "Lose~"
            else:
                hp_text += "Lose~"
                e_hp_text += "Win!"
        elif self.game.rolled:
            hp_text += (
                f"-{self.game.self_last_lose[-1]}|+{self.game.self_last_regen[-1]}"
            )
            e_hp_text += (
                f"-{self.game.enemy_last_lose[-1]}|+{self.game.enemy_last_regen[-1]}"
            )
        self.self_info_text.set(hp_text)
        self.enemy_info_text.set(e_hp_text)
        self.roll_bottom.config(state="normal" if self.game.can_roll else "disabled")
        self.end_bottom.config(state="normal" if self.game.rolled else "disabled")
        for widget in self.self_field_available.winfo_children():
            widget.destroy()
        for i, dice in enumerate(self.game.available):
            tk.Button(
                self.self_field_available,
                text=dice,
                command=lambda d=dice: [self.game.on_select(d), self.render()],
                state="disabled" if self.game.rolled else "normal",
                font=("simhei", 8, "bold"),
            ).pack(side="left")
        for i, dice in enumerate(self.game.resting):
            tk.Button(
                self.self_field_available,
                text=dice,
                state="disabled",
                font=("simhei", 8, "bold"),
            ).pack(side="left")
        for widget in self.self_field_onboard.winfo_children():
            widget.destroy()
        for i, dice in enumerate(self.game.on_board):
            tk.Button(
                self.self_field_onboard,
                text=dice,
                command=lambda d=dice: [self.game.on_unselect(d), self.render()],
                font=("simhei", 8, "bold"),
            ).pack(side="left", anchor="center")
        for i, dice in enumerate(self.game.rolleded):
            tk.Button(
                self.self_field_onboard,
                text=dice.last_roll,
                state="disabled",
                font=("simhei", 8, "bold"),
            ).pack(side="left")

        for widget in self.enemy_field_onboard.winfo_children():
            widget.destroy()
        for i, dice in enumerate(self.game.e_rolleded):
            tk.Button(
                self.enemy_field_onboard,
                text=dice.last_roll,
                font=("simhei", 8, "bold"),
            ).pack(side="left", anchor="center")

        for widget in self.enemy_field_available.winfo_children():
            widget.destroy()
        for i, dice in enumerate(self.game.e_available):
            tk.Button(
                self.enemy_field_available,
                text=dice,
                font=("simhei", 8, "bold"),
            ).pack(side="left", anchor="center")
        for i, dice in enumerate(self.game.e_resting):
            tk.Button(
                self.enemy_field_available,
                text=dice,
                state="disabled",
                font=("simhei", 8, "bold"),
            ).pack(side="left", anchor="center")

    def restart(self):
        self.game.restart()
        self.render()

    def run(self) -> None:
        self.root.mainloop()


if __name__ == "__main__":
    UI().run()
