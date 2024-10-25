import tkinter as tk
import random
from itertools import product
from typing import Literal

# poker game
# Setup:
#   Get a deck of poker cards, remove all face cards (Jack, Queen, King), and jokers.
#   Take out all Ace cards as resources. Player 1 gets one Ace; Player 2 gets two Aces.
#   Shuffle the remaining 2-9 cards and place 36 of them face-up in a 6x6 grid.
#   Split the grid in the middle, creating two 3x6 sections, one for each player.
# Gameplay:
#   On each turn:
#       Swap Phase: Players may swap two adjacent cards within their own section of the grid.
#           swap can be done before and after capture but only once.
#       Capture Phase: Select one opponent’s card next to any of your card.
#           if your adjacent card is higher than the selected card, you own that card.
#   In the Capture Phase, a '2' is considered higher than '10'.
#   Special Rule: If one opponent’s card is fully surrounded by your cards, you own it immediately.
#   Using Aces: During Capture Phase, Aces can be used to force the capture of an opponent’s card,
#     provided that at least one of your cards that sums up to a value greater than or equal to the opponent’s card is given to the opponent.
#   Mandatory Action: If possible, players must make a Capture during the Capture Phase. Otherwise lose.
# Turn Order:
#   Player 1 starts first, followed by Player 2, alternating until the game ends.
# End of Game:
#   The game ends when a player cannot make any moves, or after 20 turns have passed.
#   The player with the most cards wins.


class Poker:
    def __init__(self, color: Literal["♠", "♥", "♣", "♦"], value: int) -> None:
        self.color: Literal["♠", "♥", "♣", "♦"] = color
        self.value: int = value

    def __str__(self) -> str:
        return f"{self.color}{'A' if self.value == 1 else self.value}"


class Controller:
    def __init__(self) -> None:
        self.deck: list[Poker] = [
            Poker(color, value)
            for color, value in product(("♠", "♥", "♣", "♦"), range(2, 11))
        ]
        random.shuffle(self.deck)
        self.grids: dict[tuple[int, int], Poker] = {
            i: self.deck.pop() for i in product(range(6), range(6))
        }
        if self.deck != []:
            raise ValueError("Error")
        self.turn = 0  # 0 for p1, 1 for p2
        self.phase = 0  # 0 for swap, 1 for capture, 2 for swap if skipped in p0
        self.on_A = tk.IntVar()  # is A card used
        self.remain_A = {0: 1, 1: 2}
        self.skip_token = False
        self.board_range = set(product(range(6), range(6)))
        self.p1: set[tuple[int, int]] = set(product(range(6), range(3, 6)))  # top half
        self.p2: set[tuple[int, int]] = set(product(range(6), range(3)))  # another
        self.p_board = {0: self.p1, 1: self.p2}
        self.selected: set[tuple[int, int]] = set()
        self.gg = False

    @property
    def available(self) -> set[tuple[int, int]]:
        if self.gg:
            return set()
        """确保可选卡正确，后面不在做判断"""
        if len(self.p_board[0]) + len(self.p_board[1]) != 36:
            raise ValueError("!")
        if self.phase in [0, 2]:  # swap阶段只能选自己的牌
            if len(self.selected) > 1:  # 如果已经选了
                return self.selected
            elif len(self.selected) > 0:
                coord = list(self.selected)[0]
                neis = self.get_neighbor(coord, 4)
                return neis.intersection(self.p_board[self.turn]).union(self.selected)
            else:
                return self.p_board[self.turn]
        # capture阶段,如果有A, 则能选任意我方牌和对方与我相邻的牌
        # 特殊的，这段代码在call_status里处理，这里只返回所有可能性。
        elif self.phase == 1 and self.on_A.get():
            return set(self.grids)
        else:  # capture阶段,如果没A,能选所有相邻且我方大于对方的牌
            if len(self.selected) > 1:
                return self.selected
            elif len(self.selected) > 0:  # 如果已经选了，就只显示另一方的牌
                coord = list(self.selected)[0]
                neis = self.get_neighbor(coord, 4)
                if coord in self.p_board[self.turn]:  # 选的是我方的
                    possible = neis.intersection(self.p_board[1 - self.turn])  # 对方的
                    res = set()
                    for other_coord in possible:  # 对方小于我方的
                        if self.grids[other_coord].value < self.grids[coord].value:
                            res.add(other_coord)
                        elif (
                            self.grids[other_coord].value == 10
                            and self.grids[coord].value == 2
                        ):
                            res.add(other_coord)
                    return res.union(self.selected)
                else:  # 选的是对方的
                    possible = neis.intersection(self.p_board[self.turn])  # 我方的
                    res = set()
                    for other_coord in possible:  # 我方大于对方的
                        if self.grids[other_coord].value > self.grids[coord].value:
                            res.add(other_coord)
                        elif (
                            self.grids[other_coord].value == 2
                            and self.grids[coord].value == 10
                        ):
                            res.add(other_coord)
                    return res.union(self.selected)
            else:  # 如果没有就全显示出来
                res = set()
                for coord in self.p_board[self.turn]:  # 检查每一个自己的牌
                    for nei in self.get_neighbor(coord, 4):  # 的邻居
                        if nei in self.p_board[1 - self.turn]:  # 如果它是对手牌
                            if self.grids[coord].value > self.grids[nei].value:
                                res.add(coord)
                                res.add(nei)
                            elif (
                                self.grids[nei].value == 10
                                and self.grids[coord].value == 2
                            ):
                                res.add(coord)
                                res.add(nei)
                return res

    def on_select(self, coord: tuple[int, int]) -> None:
        if coord in self.selected:
            self.selected.remove(coord)
        else:
            self.selected.add(coord)

    def checK_A(self):
        self.selected.clear()

    @property
    def call_status(self) -> str:
        """明确阶段"""
        if self.phase in [0, 2]:
            if len(self.selected) == 2:
                return "Swap"
            return "Skip"
        elif self.phase == 1 and self.on_A.get():
            if len(self.selected) >= 2:
                c1 = self.selected.intersection(self.p_board[self.turn])
                c2 = self.selected.intersection(self.p_board[1 - self.turn])
                v1 = sum([self.grids[c].value for c in c1])
                v2 = sum([self.grids[c].value for c in c2])
                if c1 and len(c2) == 1 and v1 >= v2:  # 用A时允许大于等于
                    return "Own"
            return "GG"
        else:
            if len(self.selected) == 2:
                return "Own"
            return "GG"

    def on_call(self) -> None:
        if self.phase == 0:
            if self.call_status == "Swap":
                c1, c2 = list(self.selected)
                self.grids[c1], self.grids[c2] = self.grids[c2], self.grids[c1]
            elif self.call_status == "Skip":
                self.skip_token = True
            self.phase = 1
        elif self.phase == 2:
            if self.call_status == "Swap":
                c1, c2 = list(self.selected)
                self.grids[c1], self.grids[c2] = self.grids[c2], self.grids[c1]
            self.phase = 0
            self.turn = 1 - self.turn
            self.skip_token = False
        elif self.phase == 1:
            if self.call_status == "Own" and self.on_A.get():
                c1 = self.selected.intersection(self.p_board[self.turn])
                c2 = self.selected.intersection(self.p_board[1 - self.turn])
                self.p_board[self.turn] = (
                    self.p_board[self.turn].union(c2).difference(c1)
                )
                self.p_board[1 - self.turn] = (
                    self.p_board[1 - self.turn].union(c1).difference(c2)
                )
            elif self.call_status == "Own" and not self.on_A.get():
                c2 = self.selected.intersection(self.p_board[1 - self.turn])
                self.p_board[self.turn] = self.p_board[self.turn].union(c2)
                self.p_board[1 - self.turn] = self.p_board[1 - self.turn].difference(c2)
                if len(c2) != 1:
                    raise ValueError("123")
                self.surround_check(list(c2)[0])
            elif self.call_status == "GG":
                self.gg = True

            if self.skip_token:
                self.phase = 2
            else:
                self.phase = 0
                self.turn = 1 - self.turn

            if self.on_A.get():
                self.remain_A[self.turn] -= 1
            self.on_A.set(0)
        self.selected.clear()

    def surround_check(self, coord: tuple[int, int]):
        neis = self.get_neighbor(coord, 4)
        res = set()
        for coord in neis:
            neiss = self.get_neighbor(coord, 4)
            lenss = len(neiss)
            p1 = neis.intersection(self.p_board[self.turn])
            if len(p1) == lenss:
                res.add(coord)
        self.p_board[self.turn] = self.p_board[self.turn].union(res)
        self.p_board[1 - self.turn] = self.p_board[1 - self.turn].difference(res)

    def get_neighbor(
        self, coord: tuple[int, int], num: int = 4
    ) -> set[tuple[int, int]]:
        four_nei = {(0, 1), (0, -1), (1, 0), (-1, 0)}
        eight_nei = set(product(range(-1, 2), range(-1, 2)))
        eight_nei.remove((0, 0))
        neighbors = []
        if num == 4:
            for delta in four_nei:
                new_coord = coord[0] + delta[0], coord[1] + delta[1]
                neighbors.append(new_coord)
        else:
            for delta in eight_nei:
                new_coord = coord[0] + delta[0], coord[1] + delta[1]
                neighbors.append(new_coord)
        return set(neighbors).intersection(self.board_range)


class UI:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("")
        self.root.geometry("180x216")
        self.root.resizable(width=False, height=False)
        self.game = Controller()

        self.menubar = tk.Menu(self.root)
        self.menu_start = tk.Menu(self.menubar, tearoff=0)
        self.menu_start.add_command(label="Restart", command=self.restart)
        self.menu_start.add_separator()
        self.menu_start.add_command(label="Exit", command=self.root.destroy)
        self.menubar.add_cascade(label="Game", menu=self.menu_start)
        self.root.config(menu=self.menubar)

        # 主界面
        self.info_frame = tk.Frame(self.root)
        self.info_frame.place(relheight=1 / 6, relwidth=1, relx=0, rely=0)
        self.card_frame = tk.Frame(self.root)
        self.card_frame.place(relheight=5 / 6, relwidth=1, relx=0, rely=1 / 6)

        # 上边
        self.turn = tk.StringVar(value=f"Score: {self.game.turn}")
        self.turn_label = tk.Label(self.info_frame, textvariable=self.turn)
        self.turn_label.place(relheight=0.5, relwidth=0.45, relx=0, rely=0)
        self.phase = tk.StringVar(value=f"Target: {self.game.phase}")
        self.phase_label = tk.Label(self.info_frame, textvariable=self.phase)
        self.phase_label.place(relheight=0.5, relwidth=0.45, relx=0, rely=0.5)
        self.call_button = tk.Button(
            self.info_frame,
            command=lambda: [self.game.on_call(), self.render()],
        )
        self.call_button.place(relheight=1, relwidth=0.2, relx=0.45, rely=0)
        self.A = tk.StringVar(value=f"A: {self.game.remain_A[self.game.turn]}")
        self.A_Label = tk.Label(self.info_frame, textvariable=self.A)
        self.A_Label.place(relheight=0.5, relwidth=0.4, relx=0.65, rely=0)
        self.A_check = tk.Checkbutton(
            self.info_frame,
            text="Use?",
            variable=self.game.on_A,
            command=lambda: [self.game.checK_A(), self.render()],
        )
        self.A_check.place(relheight=0.5, relwidth=0.4, relx=0.65, rely=0.5)

        self.render()

    def restart(self) -> None:
        self.game = Controller()
        self.render()

    def render(self) -> None:
        turn = "blue" if self.game.turn else "red"
        self.turn.set(f"Turn: {turn}")
        phase_map = {0: "swap1", 1: "capture", 2: "swap2"}
        phase = "win" if self.game.gg else phase_map[self.game.phase]
        self.phase.set(f"Phase: {phase}")
        self.A.set(f"A: {self.game.remain_A[self.game.turn]}")
        self.call_button.config(
            text=self.game.call_status, state="disabled" if self.game.gg else "normal"
        )
        self.A_check.config(
            state=(
                "normal"
                if self.game.remain_A[self.game.turn] and phase == "capture"
                else "disabled"
            )
        )
        available = self.game.available
        for widget in self.card_frame.winfo_children():
            widget.destroy()
        for coord, poker in self.game.grids.items():
            j, i = coord
            tk.Button(
                self.card_frame,
                text=str(poker),
                command=lambda c=coord: [
                    self.game.on_select(c),
                    self.render(),
                ],
                state="normal" if coord in available else "disable",
                bg="peachpuff" if coord in self.game.p_board[0] else "lightblue",
                bd=3 if coord in self.game.selected else 1,
                disabledforeground="gray",
            ).place(relheight=1 / 6, relwidth=1 / 6, relx=j / 6, rely=i / 6)

    def run(self) -> None:
        self.root.mainloop()


if __name__ == "__main__":
    UI().run()
