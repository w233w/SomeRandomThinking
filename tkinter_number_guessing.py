import random
import tkinter as tk

# number guessing game
# unfinished


class GameController:
    def __init__(self) -> None:
        self.pool: list[str] = list(map(str, range(10)))
        random.shuffle(self.pool)
        self.target = "".join(self.pool[:4])
        self.possible: list[list[str]] = [list(map(str, range(10))) for _ in range(4)]
        self.hist: list[list[str]] = []
        self.selected: list[str] = ["", "", "", ""]
        self.a = 0
        self.b = 0

    @property
    def win(self) -> bool:
        return self.a == 4

    @property
    def can_judge(self) -> bool:
        return not self.win and "" not in self.selected

    def judge(self) -> None:
        self.hist.append(self.selected)
        a, b = 0, 0
        for i, c in enumerate(self.selected):
            if c == self.target[i]:
                a += 1
            elif c in self.target:
                b += 1
        if a == 0:
            for i, c in enumerate(self.selected):
                try:
                    self.possible[i].remove(c)
                except:
                    pass
        self.a = a
        self.b = b
        self.selected = ["", "", "", ""]

    def on_select(self, index, val) -> None:
        self.selected[index] = val


class UI:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("fun")
        self.root.geometry("300x160")  # 15*8
        self.root.resizable(width=False, height=False)

        self.game = GameController()

        # 菜单
        self.menubar = tk.Menu(self.root)
        self.menu_start = tk.Menu(self.menubar, tearoff=0)
        self.menu_start.add_command(label="Restart", command=None)
        self.menu_start.add_separator()
        self.menu_start.add_command(label="Exit", command=self.root.destroy)
        self.menubar.add_cascade(label="Game", menu=self.menu_start)
        self.root.config(menu=self.menubar)

        # 左右两部分
        self.select_frame = tk.Frame(self.root)
        self.select_frame.place(relheight=1, relwidth=10 / 15, relx=0, rely=0)
        self.info_frame = tk.Frame(self.root)
        self.info_frame.place(relheight=1, relwidth=5 / 15, relx=10 / 15, rely=0)

        # 右上
        self.hist_frame = tk.Frame(self.info_frame)
        self.hist_frame.place(relheight=7 / 8, relwidth=1, relx=0, rely=0)
        self.hist_text = tk.Text(self.hist_frame, state="disabled", yscrollcommand=None)
        self.hist_text.pack(expand=True, fill="both", anchor="center")

        # 右下
        self.panel_frame = tk.Frame(self.info_frame)
        self.panel_frame.place(relheight=1 / 8, relwidth=1, relx=0, rely=7 / 8)
        self.confirm_button = tk.Button(
            self.panel_frame, text="confirm", state="disabled", command=lambda: []
        )
        self.confirm_button.pack(expand=True, fill="both", anchor="center")

        self.render()

    def render(self) -> None:
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
                    relheight=1 / 8,
                    relwidth=1 / 10,
                    relx=i / 10,
                    rely=(0.5 + 2 * index) / 8,
                )

    def run(self) -> None:
        self.root.mainloop()


UI().run()
