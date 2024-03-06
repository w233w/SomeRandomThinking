import tkinter as tk
import random
from itertools import count, product
from collections import Counter
from typing import Union

# dice game adventure (Chinese ver.)
# There are total 10 abilities [a1-a10].
# Select dices that match the requirement of ability.
# Check ability requirement by hover your mouse on ability button.
# Watch out enemy's ability by hover mouse on enemy information.


class Dice:
    ids = count()

    def __init__(self, value: int = 0) -> None:
        self.faces: int = 6
        self.id: int = next(Dice.ids)
        self.values = list(range(1, 7))
        self.value: int = value
        self.last_roll: int = 0
        self.roll()

    def __str__(self) -> str:
        extra = self.value if self.value != 0 else ""
        middle = ""
        if self.value > 0:
            middle = "+"
        return f"{self.last_roll}{middle}{extra}"

    def __repr__(self) -> str:
        return f"<D-{self.faces}|{self.final}>"

    def roll(self) -> int:
        self.last_roll = random.choice(self.values)

    @property
    def final(self) -> int:
        return self.last_roll + self.value

    def value_change(self, change: int):
        self.value += change


class P:
    def __init__(self) -> None:
        self.hp = 50
        self.max_hp = 50

    def on_damage(self, val) -> None:
        self.hp += val

    def on_heal(self, val) -> None:
        self.hp += val
        self.hp = min(self.hp, self.max_hp)

    @property
    def die(self) -> bool:
        return self.hp <= 0


class E:
    def __init__(self) -> None:
        self.hp = 100
        self.skills: dict[str, str] = {
            "reverse": "e_1",
            "six hate": "e_2",
            "down*6": "e_3",
        }
        self.next_skill = random.choice(list(self.skills.keys()))

    def turn_end(self):
        self.next_skill = random.choice(list(self.skills.keys()))

    @property
    def skill_func_name(self) -> str:
        return self.skills[self.next_skill]

    @property
    def die(self):
        return self.hp <= 0


class Controller:
    def __init__(self) -> None:
        self.size: int = 6
        self.grid: list[list[Dice]] = [
            [Dice() for i in range(self.size)] for j in range(self.size)
        ]
        self.selected: list[tuple[int, int]] = []
        self.do_eight = False
        self.turn = True  # True for P, False for E
        self.p = P()
        self.e = E()

    def p_info(self) -> str:
        return f"P:{self.p.hp}/{self.p.max_hp}"

    def e_info(self) -> str:
        return f"E:{self.e.hp}/100\nNext: {self.e.next_skill}"

    @property
    def end(self) -> bool:
        return self.p.die or self.e.die

    def action(self, dmg, reg):
        if self.turn:
            self.e.hp -= dmg
            self.p.hp += reg
        else:
            self.p.hp -= dmg
            self.e.hp += reg
        self.turn = not self.turn

    def reset(self):
        self.__init__()

    def on_select(self, coord):
        if coord in self.selected:
            self.selected.remove(coord)
        else:
            self.selected.append(coord)

    def check_select(self, coord):
        return coord in self.selected

    def roll(self):
        for i, row in enumerate(self.grid):
            for j, dice in enumerate(row):
                if (j, i) in self.selected:
                    dice.roll()
        self.selected.clear()

    def dfs(self, col, row):
        self.selected.remove((col, row))
        for dir in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            y, x = col + dir[0], row + dir[1]
            if 0 <= y < self.size and 0 <= x < self.size and (y, x) in self.selected:
                self.dfs(y, x)
        return

    def help_info(self, index: Union[str, int]) -> str:
        match index:
            case 1:
                return "两相邻列/行。重掷后统计1到6点,重复越多dmg越高。"
            case 2:
                return "1骰。纵向奇数->reg,横向偶数->dmg。重掷横纵。"
            case 3:
                return "4骰/矩形四角。内部多样性+角+重掷后矩形多样性。"
            case 4:
                return "不选。消除最下行，最上方新增 +2 Value 的dice。"
            case 5:
                return "6骰/大于4。重掷。2骰 +4 Value, 4骰 -1 Value."
            case 6:
                return "至多18骰。重掷。无结算。"
            case 7:
                return "6骰/互连/必有1-6。10点伤害。"
            case 8:
                return "不选。重掷全部。无结算。"
            case 9:
                return "同面/互连/任意数量。roll前统计长度+值."
            case 10:
                return "选2*2骰子。重掷前求和->伤害。-1 Value."
            case "e_1":
                return "倒转所有数。6->伤害。"
            case "e_2":
                return "统计6点数量->伤害。"
            case "e_3":
                return "随机6个骰子。value-1。"

    # 操作
    # value不影响选择,影响计算。最大幅度+-6。
    # 格式：选择的要求。计算的方式。额外的后果（可选）。

    # 1. 选择两列/行。reroll后统计1到6点,出现一对加1分,三个加3分,四个6分,五个10分,...,sum->伤害。
    # oeis A161680=A000217(n-1)
    @property
    def can_1(self):
        if not self.turn:
            return False
        if len(self.selected) != 12:
            return False
        self.selected.sort()
        # 行
        row_list = set([coord[1] for coord in self.selected])
        col_list = set([coord[0] for coord in self.selected])
        if len(row_list) == 2 and len(col_list) == 6:
            if abs(row_list.pop() - row_list.pop()) == 1:
                return True
        if len(row_list) == 6 and len(col_list) == 2:
            if abs(col_list.pop() - col_list.pop()) == 1:
                return True
        return False

    def do_1(self):
        temp = self.selected.copy()
        self.roll()
        res: list[int] = []
        for col, row in temp:
            res.append(self.grid[row][col].final)
        c = Counter(res)
        point = 0
        for i in range(1, self.size + 1):
            n = c[i] - 1
            point += n * (n + 1) // 2
        self.action(point, 0)

    # 2. 选择一个点,reroll所在行列。roll前统计纵向奇数,横向偶数,奇数num->回复,偶数num->伤害。
    @property
    def can_2(self):
        if not self.turn:
            return False
        return len(self.selected) == 1

    def do_2(self):
        center = self.selected[0]
        col, row = center
        col_odd, row_even = 0, 0
        for i in range(self.size):
            self.selected.append((i, row))
            row_even += self.grid[row][i].last_roll % 2 == 0
            self.selected.append((col, i))
            col_odd += self.grid[i][col].last_roll % 2 == 1
        self.selected = list(set(self.selected))
        self.roll()
        self.action(row_even, col_odd)

    # 3. 选择值相同的四个点,必须是矩形四个角。roll前统计内部矩形多样性,再加上角点数值,roll后统计整个矩形的多样性。
    @property
    def can_3(self):
        if not self.turn:
            return False
        if len(self.selected) != 4:
            return False
        res = set()
        for coord in self.selected:
            col, row = coord
            res.add(self.grid[row][col].last_roll)
        if len(res) != 1:
            return False
        rows = [coord[0] for coord in self.selected]
        cols = [coord[1] for coord in self.selected]
        if len(set(rows)) == len(set(cols)) == 2:
            return True
        return False

    def do_3(self):
        coords = sorted(self.selected)
        left_up = coords[0]
        right_but = coords[-1]
        # inner
        inner = product(
            range(left_up[0] + 1, right_but[0]), range(left_up[1] + 1, right_but[1])
        )
        inner_var = set()
        for coord in inner:
            col, row = coord
            inner_var.add(self.grid[row][col].final)
        inner_score = len(inner_var)
        # cornor
        cornor_score = self.grid[left_up[1]][left_up[0]].last_roll
        # full
        full = list(
            product(
                range(left_up[0], right_but[0] + 1), range(left_up[1], right_but[1] + 1)
            )
        )
        self.selected = full
        self.roll()
        full_var = set()
        for coord in full:
            col, row = coord
            full_var.add(self.grid[row][col].final)
        full_score = len(full_var)
        final_sum = inner_score + cornor_score + full_score
        self.action(final_sum, 0)

    # 4. 不选择任何点,消除最下一行,整体矩阵下降,最上方填充的dice。无。value+2。
    @property
    def can_4(self):
        if not self.turn:
            return False
        return len(self.selected) == 0

    def do_4(self):
        self.grid.pop()
        new_row = [Dice(value=2) for _ in range(self.size)]
        self.grid.insert(0, new_row)
        self.action(0, 0)

    # 5. 选择6个大于4的点。无。选两个value+4,其余value-1,reroll。
    @property
    def can_5(self):
        if not self.turn:
            return False
        if len(self.selected) != 6:
            return False
        for coord in self.selected:
            col, row = coord
            if self.grid[row][col].last_roll <= 4:
                return False
        return True

    def do_5(self):
        ups = random.sample(self.selected, 2)
        for up in ups:
            col, row = up
            self.grid[row][col].value_change(4)
        for down in self.selected:
            if down in ups:
                continue
            col, row = down
            self.grid[row][col].value_change(-1)
        self.roll()
        self.action(0, 0)

    # 6. 任意至多18个点,reroll。无。
    @property
    def can_6(self):
        if not self.turn:
            return False
        return 18 >= len(self.selected) >= 1

    def do_6(self):
        self.roll()
        self.action(0, 0)

    # 7. 选择6个两两相接的点,必须包含1-6所有值。固定10->伤害。
    @property
    def can_7(self):
        if not self.turn:
            return False
        if len(self.selected) != 6:
            return False
        res = set()
        for coord in self.selected:
            col, row = coord
            res.add(self.grid[row][col].last_roll)
        if len(res) != 6:
            return False
        temp = self.selected.copy()
        row = col = self.size
        counter = 0
        for i in range(col):
            for j in range(row):
                if (i, j) in self.selected:
                    counter += 1
                    self.dfs(i, j)
        self.selected = temp
        if counter == 1:
            return True
        return False

    def do_7(self):
        self.roll()
        self.action(10, 0)

    # 8. 不选择任何点,全reroll。无。仅一次。
    @property
    def can_8(self):
        if not self.turn:
            return False
        return not self.do_eight and len(self.selected) == 0

    def do_8(self):
        self.do_eight = True
        for row in self.grid:
            for dice in row:
                dice.roll()
        self.action(0, 0)

    # 9. 选择任意点,必须两两相连and值相同。roll前的长度*值。
    @property
    def can_9(self):
        if not self.turn:
            return False
        res = set()
        for coord in self.selected:
            col, row = coord
            res.add(self.grid[row][col].last_roll)
        if len(res) != 1:
            return False
        temp = self.selected.copy()
        row = col = self.size
        counter = 0
        for i in range(col):
            for j in range(row):
                if (i, j) in self.selected:
                    counter += 1
                    self.dfs(i, j)
        self.selected = temp
        if counter == 1:
            return True
        return False

    def do_9(self):
        col, row = self.selected[0]
        val = self.grid[row][col].last_roll
        lens = len(self.selected)
        self.roll()
        self.action(val + lens, 0)

    # 10.选择2*2的4个点。value-1,roll后求和。
    @property
    def can_10(self):
        if not self.turn:
            return False
        if len(self.selected) != 4:
            return False
        coords = sorted(self.selected)
        coord = coords[0]
        if [
            coord,
            (coord[0], coord[1] + 1),
            (coord[0] + 1, coord[1]),
            (coord[0] + 1, coord[1] + 1),
        ] == coords:
            return True
        return False

    def do_10(self):
        res = []
        temp = self.selected.copy()
        self.roll()
        for coord in temp:
            col, row = coord
            self.grid[row][col].value_change(-1)
            res.append(self.grid[row][col].final)
        self.action(sum(res), 0)

    # 敌
    # 格式：形式。结果
    # 1. 倒转所有数。6->伤害。
    def e_1(self):
        for i in range(self.size):
            for j in range(self.size):
                self.grid[i][j].last_roll = 7 - self.grid[i][j].last_roll
        self.action(6, 0)
        self.e.turn_end()

    # 2. 所有的6点。6点num->伤害。
    def e_2(self):
        count = 0
        for i in range(self.size):
            for j in range(self.size):
                if self.grid[i][j].last_roll == 6:
                    count += 1
        self.action(count, 0)
        self.e.turn_end()

    # 3.随机6个Dice。value-1。
    def e_3(self):
        rand = random.choices(list(product(range(6), range(6))), k=6)
        for col, row in rand:
            self.grid[row][col].value_change(-1)
        self.action(0, 0)
        self.e.turn_end()


class UI:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("mini")
        self.root.geometry("300x200")  # 3:2, 2处必须是60的倍数。
        self.root.resizable(width=False, height=False)
        self.game = Controller()

        # 菜单
        self.menubar = tk.Menu(self.root)
        self.menu_start = tk.Menu(self.menubar, tearoff=0)
        self.menu_start.add_command(label="Restart", command=self.restart)
        self.menu_start.add_separator()
        self.menu_start.add_command(label="Exit", command=self.root.destroy)
        self.menubar.add_cascade(label="Game", menu=self.menu_start)
        self.root.config(menu=self.menubar)

        self.field = tk.Frame(self.root, bd=1, relief="raised")
        self.field.place(relheight=9 / 10, relwidth=6 / 10, relx=0, rely=0)
        self.pannel = tk.Frame(self.root)
        self.pannel.place(relheight=9 / 10, relwidth=4 / 10, relx=6 / 10, rely=0)
        self.helper = tk.Frame(self.root)
        self.helper.place(relheight=1 / 10, relwidth=1, relx=0, rely=9 / 10)

        self.pannel.bind("<Leave>", lambda e: [self.helper_info.set("Helper Bar")])

        self.p_info = tk.StringVar()
        self.p_info_label = tk.Label(self.pannel, textvariable=self.p_info)
        self.p_info_label.place(relheight=1 / 4, relwidth=1, relx=0, rely=0)
        self.p_info_label.bind(
            "<Enter>", lambda e: [self.helper_info.set("You. lose if hp < 0.")]
        )

        self.e_info = tk.StringVar()
        self.e_info_label = tk.Label(self.pannel, textvariable=self.e_info)
        self.e_info_label.place(relheight=1 / 4, relwidth=1, relx=0, rely=1 / 4)
        self.e_info_label.bind(
            "<Enter>",
            lambda e: [
                self.helper_info.set(
                    "敌人行动: " + self.game.help_info(self.game.e.skill_func_name())
                )
            ],
        )

        for i in range(1, 11):
            setattr(
                self,
                f"ability{i}_button",
                tk.Button(
                    self.pannel,
                    text=f"a{i}",
                    command=lambda i=i: [
                        getattr(self.game, f"do_{i}")(),
                        self.render(),
                    ],
                ),
            )
            getattr(self, f"ability{i}_button").place(
                relheight=1 / 6,
                relwidth=1 / 4,
                relx=((i - 1) % 4) / 4,
                rely=(3 + ((i - 1) // 4)) / 6,
            )
            getattr(self, f"ability{i}_button").bind(
                "<Enter>", lambda e, i=i: [self.helper_info.set(self.game.help_info(i))]
            )

        self.confirm_button = tk.Button(
            self.pannel,
            text="confirm",
            command=lambda: [
                getattr(self.game, self.game.e.skill_func_name())(),
                self.render(),
            ],
        )
        self.confirm_button.place(
            relheight=1 / 6, relwidth=2 / 4, relx=2 / 4, rely=5 / 6
        )
        self.confirm_button.bind(
            "<Enter>", lambda e: [self.helper_info.set("Enemy Turn")]
        )

        self.helper_info = tk.StringVar(value="Helper Bar")
        self.helper_info_label = tk.Label(self.helper, textvariable=self.helper_info)
        self.helper_info_label.place(relheight=1, relwidth=1, relx=0, rely=0)

        self.render()

    def render(self):
        self.p_info.set(self.game.p_info())
        self.p_info_label.config(fg="red" if self.game.turn else "black")
        self.e_info.set(self.game.e_info())
        self.e_info_label.config(fg="red" if not self.game.turn else "black")
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
                    bd=4 if self.game.check_select((j, i)) else 1,
                    relief="sunken",
                ).place(
                    relheight=1 / self.game.size,
                    relwidth=1 / self.game.size,
                    relx=j * 1 / self.game.size,
                    rely=i * 1 / self.game.size,
                )
        for i in range(1, 11):
            getattr(self, f"ability{i}_button").config(
                state=(
                    "disabled"
                    if self.game.end
                    else ("active" if getattr(self.game, f"can_{i}") else "disabled")
                )
            )
        self.confirm_button.config(
            state=(
                "disabled"
                if self.game.end
                else ("active" if not self.game.turn else "disabled")
            ),
        )

    def restart(self):
        self.game.reset()
        self.render()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    UI().run()
