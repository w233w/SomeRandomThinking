import tkinter as tk
import random

# unfinished


class Dice:
    def __init__(self, faces: int = 6, temp: bool = False) -> None:
        self.faces = faces
        self.values = list(range(1, faces + 1))
        self.last_roll: int = 0
        self.temp = temp
        self.modifier: list[str] = []

    def __str__(self) -> str:
        return f"D{self.faces}"

    def roll(self) -> int:
        self.last_roll = random.choice(self.values)
        return self.last_roll


class Character:
    def __init__(self, init_hand: list[int], max_hp: int) -> None:
        self.available: list[Dice] = []
        self.on_board: list[Dice] = []
        self.rolled: list[Dice] = []
        self.resting: list[Dice] = []

        self.init_hand = init_hand
        for v in self.init_hand:
            self.available.append(Dice(v))
        self.hand_size = len(self.init_hand)
        self.init_max_hp = max_hp
        self.max_hp: int = max_hp
        self.hp: int = max_hp

        self.roll_hist: list[int] = []
        self.regen_hist: list[int] = []
        self.lose_hist: list[int] = []

    @property
    def die(self) -> bool:
        return self.hp <= 0

    def reset(self) -> None:
        self.__init__(self.init_hand, self.init_max_hp)

    def on_select(self, dice: Dice) -> None:
        self.on_board.append(dice)
        self.available.remove(dice)

    def on_unselect(self, dice: Dice) -> None:
        self.available.append(dice)
        self.on_board.remove(dice)

    def roll(self) -> None:
        self.values = [dice.roll() for dice in self.on_board]
        self.roll_hist.append(sum(self.values))
        self.regen_hist.append(
            max([v for v in self.values if self.values.count(v) > 1] + [0])
        )
        self.rolled.extend(self.on_board)
        self.on_board.clear()

    def lose(self, val) -> None:
        self.lose_hist.append(val)

    def end(self) -> None:
        self.hp += self.regen_hist[-1]
        self.hp -= self.lose_hist[-1]

        self.available.extend(self.resting)
        self.resting.clear()
        self.resting.extend(self.rolled)
        self.rolled.clear()


class P(Character):
    def __init__(
        self, init_hand: list[int] = [6, 6, 6, 6, 6], max_hp: int = 30
    ) -> None:
        super().__init__(init_hand=init_hand, max_hp=max_hp)


class E(Character):
    def __init__(self, init_hand: list[int], max_hp: int) -> None:
        super().__init__(init_hand, max_hp)

    def strategy(self):
        e_roll_num = len(self.available)
        if len(self.resting) == 0:
            e_roll_num = max(1, int(e_roll_num / 2))
        for _ in range(e_roll_num):
            self.on_board.append(self.available.pop())


class BattleController:
    def __init__(self, e: E) -> None:
        self.turn: int = 0
        self.p = P()
        self.e = e

        self.rolled: bool = False

    def restart(self):
        self.e.reset()
        self.__init__(self.e)

    @property
    def battle_end(self):
        return self.p.die or self.e.die

    @property
    def can_roll(self) -> bool:
        return not self.rolled and 4 >= len(self.p.on_board) >= 1

    def on_select(self, dice):
        if not self.battle_end:
            self.p.on_select(dice)

    def on_unselect(self, dice):
        if not self.battle_end:
            self.p.on_unselect(dice)

    def roll(self) -> None:
        self.p.roll()
        self.rolled = True

        self.e.strategy()
        self.e.roll()

        p_roll = self.p.roll_hist[-1]
        e_roll = self.e.roll_hist[-1]
        if p_roll == e_roll:
            self.p.lose(0)
            self.e.lose(0)
        elif p_roll > e_roll:
            self.e.lose(p_roll - e_roll)
            self.p.lose(0)
        elif p_roll < e_roll:
            self.p.lose(e_roll - p_roll)
            self.e.lose(0)

    def end_turn(self):
        self.turn += 1

        self.p.end()
        self.e.end()

        self.rolled = False


class GameController:
    def __init__(self) -> None:
        self.stage = 1
        self.enemys: list[E] = [
            E([6, 6, 6, 6, 6], 30),
        ]
        self.battle = BattleController(self.enemys[self.stage - 1])

    @property
    def battle_end(self) -> bool:
        return self.battle.game_end


class UI:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("mini")
        self.root.geometry("200x200")
        self.root.resizable(width=False, height=False)

        self.game = GameController()
        self.game = self.game.battle

        # 菜单
        self.menubar = tk.Menu(self.root)
        self.menu_start = tk.Menu(self.menubar, tearoff=0)
        self.menu_start.add_command(label="Restart", command=self.restart)
        self.menu_start.add_command(label="Help", command="")
        self.menu_start.add_separator()
        self.menu_start.add_command(label="Exit", command=self.root.destroy)
        self.menubar.add_cascade(label="Game", menu=self.menu_start)
        self.root.config(menu=self.menubar)

        # 主界面，分上下两部分
        self.up_frame = tk.Frame(self.root, bd=1, relief="raised")
        self.up_frame.place(relheight=0.4, relwidth=1, relx=0, rely=0)
        self.down_frame = tk.Frame(self.root, bd=1, relief="raised")
        self.down_frame.place(relheight=0.6, relwidth=1, relx=0, rely=0.4)

        # 上部分-enemy，分左右两部分
        self.enemy_field = tk.Frame(self.up_frame)
        self.enemy_field.place(relheight=1, relwidth=0.7, relx=0, rely=0)
        self.enemy_info = tk.Frame(self.up_frame, bd=1, relief="raised")
        self.enemy_info.place(relheight=1, relwidth=0.3, relx=0.7, rely=0)

        # enemy左部分，分上下两部分
        self.enemy_field_available = tk.Frame(self.enemy_field)
        self.enemy_field_available.place(relheight=0.5, relwidth=1, relx=0, rely=0)
        self.enemy_field_onboard = tk.Frame(self.enemy_field)
        self.enemy_field_onboard.place(relheight=0.5, relwidth=1, relx=0, rely=0.5)

        # enemy右部分-enemy_info,hp
        self.enemy_info_text = tk.StringVar()
        self.enemy_info_text_label = tk.Label(
            self.enemy_info, textvariable=self.enemy_info_text
        )
        self.enemy_info_text_label.pack(fill="both", expand=True)

        # 下部分-self， 分左右下三部分
        self.self_field = tk.Frame(self.down_frame)
        self.self_field.place(relheight=2 / 3, relwidth=0.7, relx=0, rely=0)
        self.self_info = tk.Frame(self.down_frame, bd=1, relief="raised")
        self.self_info.place(relheight=2 / 3, relwidth=0.3, relx=0.7, rely=0)
        self.self_action_button = tk.Frame(self.down_frame)
        self.self_action_button.place(relheight=1 / 3, relwidth=1, relx=0, rely=2 / 3)

        # self左部分-self台面，分上下两部分
        self.self_field_onboard = tk.Frame(self.self_field)
        self.self_field_onboard.place(relheight=0.5, relwidth=1, relx=0, rely=0)
        self.self_field_available = tk.Frame(self.self_field)
        self.self_field_available.place(relheight=0.5, relwidth=1, relx=0, rely=0.5)

        # self右部分-self_info，hp
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
            command=lambda: [self.game.end_turn(), self.render()],
        )
        self.end_bottom.place(relheight=1, relwidth=0.5, relx=0.5, rely=0)

        # 动态渲染
        self.render()

    def render(self):
        hp_text = f"You\nHP: {self.game.p.hp}\n"
        e_hp_text = f"Enemy\nHP: {self.game.e.hp}\n"
        if self.game.battle_end:
            if self.game.p.hp > 0:
                hp_text += "Win!"
                e_hp_text += "Lose~"
            else:
                hp_text += "Lose~"
                e_hp_text += "Win!"
        elif self.game.rolled:
            hp_text += f"-{self.game.p.lose_hist[-1]}|+{self.game.p.regen_hist[-1]}"
            e_hp_text += f"-{self.game.e.lose_hist[-1]}|+{self.game.e.regen_hist[-1]}"
        self.self_info_text.set(hp_text)
        self.enemy_info_text.set(e_hp_text)
        self.roll_bottom.config(state=tk.NORMAL if self.game.can_roll else tk.DISABLED)
        self.end_bottom.config(state=tk.NORMAL if self.game.rolled else tk.DISABLED)
        for widget in self.self_field_available.winfo_children():
            widget.destroy()
        for dice in self.game.p.available:
            tk.Button(
                self.self_field_available,
                text=str(dice),
                command=lambda d=dice: [self.game.on_select(d), self.render()],
                state=tk.DISABLED if self.game.rolled else tk.NORMAL,
                font=("simhei", 8, "bold"),
                bg=("yellow" if dice.temp else None),
            ).pack(side="left")
        for dice in self.game.p.resting:
            tk.Button(
                self.self_field_available,
                text=str(dice),
                state="disabled",
                font=("simhei", 8, "bold"),
                bg="yellow" if dice.temp else None,
            ).pack(side="left")
        for widget in self.self_field_onboard.winfo_children():
            widget.destroy()
        for dice in self.game.p.on_board:
            tk.Button(
                self.self_field_onboard,
                text=str(dice),
                command=lambda d=dice: [self.game.on_unselect(d), self.render()],
                font=("simhei", 8, "bold"),
                bg="yellow" if dice.temp else None,
            ).pack(side="left", anchor="center")
        for dice in self.game.p.rolled:
            tk.Button(
                self.self_field_onboard,
                text=dice.last_roll,
                state="disabled",
                font=("simhei", 8, "bold"),
                bg="yellow" if dice.temp else None,
            ).pack(side="left")

        for widget in self.enemy_field_onboard.winfo_children():
            widget.destroy()
        for dice in self.game.e.rolled:
            tk.Button(
                self.enemy_field_onboard,
                text=dice.last_roll,
                font=("simhei", 8, "bold"),
            ).pack(side="left", anchor="center")

        for widget in self.enemy_field_available.winfo_children():
            widget.destroy()
        for dice in self.game.e.available:
            tk.Button(
                self.enemy_field_available,
                text=str(dice),
                font=("simhei", 8, "bold"),
            ).pack(side="left", anchor="center")
        for dice in self.game.e.resting:
            tk.Button(
                self.enemy_field_available,
                text=str(dice),
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
