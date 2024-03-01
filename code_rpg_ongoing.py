class P:
    def __init__(self) -> None:
        self.map = [
            ["↓", " ", "G"],
            [" ", "E", " "],
            [" ", " ", "P"],
        ]
        self.p_hp = 3
        self.p_atk = 3
        self.p_face = "left"

        self.e_hp = 5
        self.e_atk = 1
        self.e_face = "down"

        self._turn_start()

    @property
    def _p_coord(self) -> tuple[int, int]:
        for row_num, row in enumerate(self.map):
            for col_num, tile in enumerate(row):
                if tile == "P":
                    return (row_num, col_num)

    def _turn_start(self) -> None:
        self.can_turn = True
        self.can_observe = True

    def _turn_end(self) -> None:
        if self.e_hp >= 0:
            if self.map[2][1] == "P":
                self.p_hp -= 3
        self._turn_start()

    def _get_tile(self, row, col) -> str:
        try:
            return self.map[row][col]
        except:
            return "#"

    def _invalid_action(self, infor: str) -> None:
        print(infor)
        self._turn_end()

    def observe(self, side: str) -> tuple[str, str]:
        """由近及远返回两个单元格"""
        if self.can_observe:
            self.can_observe = False
            coord = self._p_coord
            if side == "up":
                close = self._get_tile(coord[0] - 1, coord[1])
                far = self._get_tile(coord[0] - 2, coord[1])
                return close, far
            elif side == "down":
                close = self._get_tile(coord[0] + 1, coord[1])
                far = self._get_tile(coord[0] + 2, coord[1])
                return close, far
            elif side == "left":
                close = self._get_tile(coord[0], coord[1] - 1)
                far = self._get_tile(coord[0], coord[1] - 2)
                return close, far
            elif side == "right":
                close = self._get_tile(coord[0], coord[1] + 1)
                far = self._get_tile(coord[0], coord[1] + 2)
                return close, far
            else:
                self._invalid_action("can only ob 4 dirs.")
        else:
            self._invalid_action("cant ob twice")

    def turn(self, side: str) -> None:
        if self.can_turn:
            self.can_turn = False
            if side == "left":
                pass
            elif side == "right":
                pass
            elif side == "back":
                pass
            else:
                self._invalid_action("invalid turn")
        else:
            self._invalid_action("cant turn twice")


print(P().observe("down"))
