import random
import tkinter as tk


# number guessing game
# Using classic rule, you need to guess a 4 digits non-repeat number. Leading 0 is allowed.
# Every guess require you select 4 different numbers.
# for every digit on the right position, you award 1 A.
# for every digit not on the right position but exist on rest of selected number, you award 1 B.
# your goal is to get 4 A, meaning selected number are the same as target.

# Guessing history will display on the right.
# impossible number will be disabled for you.

# GG on game menu will display the answer and end the round.


class GameController:
    def __init__(self) -> None:
        self.pool: list[str] = list(map(str, range(10)))
        random.shuffle(self.pool)
        self.target = "".join(self.pool[:4])
        self.possible: list[list[str]] = [list(map(str, range(10))) for _ in range(4)]
        self.hist: list[str] = ["Game Start:"]
        self.selected: list[str] = ["-", "-", "-", "-"]

    def restart(self) -> None:
        self.__init__()

    @property
    def win(self) -> bool:
        return "WIN" in self.hist[-1] or "GG" in self.hist[-1]

    @property
    def can_judge(self) -> bool:
        return (
                not self.win and "-" not in self.selected and len(set(self.selected)) == 4
        )

    def judge(self) -> None:
        a, b = 0, 0
        for i, c in enumerate(self.selected):
            if c == self.target[i]:
                a += 1
            elif c in self.target:
                b += 1
        if a == 0 and b == 0:
            for c in self.selected:
                for i in range(4):
                    try:
                        self.possible[i].remove(c)
                    except:
                        pass
        if a == 0:
            for i, c in enumerate(self.selected):
                try:
                    self.possible[i].remove(c)
                except:
                    pass
        if a + b == 4:
            for i in range(4):
                self.possible[i] = self.selected.copy()
        if a == 4:
            self.hist.append(f"{''.join(self.selected)}:WIN!")
            return
        self.hist.append(f"{''.join(self.selected)}:{a}A|{b}B")
        self.selected = ["-", "-", "-", "-"]

    def on_select(self, index, val) -> None:
        if self.selected[index] == "-":
            self.selected[index] = val
        elif self.selected[index] == val:
            self.selected[index] = "-"
        else:
            self.selected[index] = val

    def on_gg(self) -> None:
        self.hist.append(f"{self.target}:GG")


class UI:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("fun")
        self.root.geometry("240x300")  # 8 * 10
        self.root.resizable(width=False, height=False)

        self.game = GameController()

        # 菜单
        self.menubar = tk.Menu(self.root)
        self.menu_start = tk.Menu(self.menubar, tearoff=0)
        self.menu_start.add_command(
            label="Restart", command=lambda: [self.game.restart(), self.render()]
        )
        self.menu_start.add_command(
            label="GG", command=lambda: [self.game.on_gg(), self.render()]
        )
        self.menu_start.add_separator()
        self.menu_start.add_command(label="Exit", command=self.root.destroy)
        self.menubar.add_cascade(label="Game", menu=self.menu_start)
        self.root.config(menu=self.menubar)

        # 左右两部分
        self.select_frame = tk.Frame(self.root)
        self.select_frame.place(relheight=1, relwidth=1 / 2, relx=0, rely=0)
        self.info_frame = tk.Frame(self.root)
        self.info_frame.place(relheight=1, relwidth=1 / 2, relx=1 / 2, rely=0)

        # 右上
        self.selected_frame = tk.Frame(self.info_frame)
        self.selected_frame.place(relheight=1 / 10, relwidth=1, relx=0, rely=0)
        self.selected_number = tk.StringVar(value="".join(self.game.selected))
        self.selected_label = tk.Label(
            self.selected_frame, textvariable=self.selected_number
        )
        self.selected_label.place(relheight=1, relwidth=1, relx=0, rely=0)

        # 右中
        self.hist_frame = tk.Frame(self.info_frame)
        self.hist_frame.place(relheight=8 / 10, relwidth=1, relx=0, rely=1 / 10)
        self.hist_text = tk.Text(self.hist_frame, state="disabled", yscrollcommand=None)
        self.hist_text.pack(expand=True, fill="both", anchor="center")

        # 右下
        self.panel_frame = tk.Frame(self.info_frame)
        self.panel_frame.place(relheight=1 / 10, relwidth=1, relx=0, rely=9 / 10)
        self.confirm_button = tk.Button(
            self.panel_frame,
            text="confirm",
            state="disabled",
            command=lambda: [self.game.judge(), self.render()],
        )
        self.confirm_button.pack(expand=True, fill="both", anchor="center")

        self.render()

    def render(self) -> None:
        self.selected_number.set(" ".join(self.game.selected))
        self.confirm_button.config(
            state="normal" if self.game.can_judge else "disabled"
        )
        self.hist_text.config(state="normal")
        self.hist_text.delete("1.0", tk.END)
        for hist in self.game.hist:
            self.hist_text.insert(tk.END, f"{hist}\n")
        self.hist_text.config(state="disabled")
        for widget in self.select_frame.winfo_children():
            widget.destroy()
        for index, row in enumerate(self.game.possible):
            for i in range(10):
                tk.Button(
                    self.select_frame,
                    text=str(i),
                    state="active" if str(i) in row else "disable",
                    command=lambda index=index, val=str(i): [
                        self.game.on_select(index, val),
                        self.render(),
                    ],
                    bd=5 if str(i) == self.game.selected[index] else None,
                ).place(
                    relheight=1 / 10,
                    relwidth=1 / 4,
                    relx=index / 4,
                    rely=i / 10,
                )

    def run(self) -> None:
        self.root.mainloop()


if __name__ == "__main__":
    UI().run()
