from PySide6.QtWidgets import *
from PySide6.QtCore import QTimer, Qt, Signal
from PySide6.QtGui import QTextDocument, QPixmap, QPainter, QIcon
from itertools import product
import sys

from PySide6.QtWidgets import QWidget
from functools import partial
from collections import defaultdict
from copy import deepcopy
from typing import Callable, TypeAlias, Literal

Resource: TypeAlias = Literal["red", "green", "blue"]
Status: TypeAlias = dict[Resource, int]
Buff: TypeAlias = Callable[[Status], Status]
Coord: TypeAlias = tuple[int, int]


class Building:
    def __init__(self, name: str, coord: Coord) -> None:
        self.name: str = name
        self.coord: Coord = coord

    def display_info(self) -> tuple[QPixmap, QIcon]:
        return ""

    def offer_buff(self) -> dict[Coord, Buff]:
        return {}

    def update(self, buffs: list[Buff]): ...


# mine one resource per second.
class DefaultMiner(Building):
    def __init__(self, name, coord) -> None:
        super().__init__(name, coord)
        self.resource: dict[Resource, int] = {
            "red": 0,
            "green": 0,
            "blue": 0,
        }
        self.base_status: Status = {
            "red": 1,
            "green": 1,
            "blue": 1,
        }
        self.time = 0
        self.time_per_update = 25

    def display_info(self):
        document = QTextDocument()
        document.setDocumentMargin(0)
        document.setHtml(
            f"""<font color=red>{self.resource['red']}</font><br />
            <font color=green>{self.resource['green']}</font><br />
            <font color=blue>{self.resource['blue']}</font>"""
        )
        pixmap = QPixmap(document.size().toSize())
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        document.drawContents(painter)
        painter.end()
        icon = QIcon(pixmap)
        return pixmap, icon

    def update(self, buffs: list[Buff]):
        self.time += 1
        if self.time % self.time_per_update == 0:
            status = deepcopy(self.base_status)
            for buff in buffs:
                status = buff(status)
            for k, v in status.items():
                if k in self.resource:
                    self.resource[k] += v


# offer plus one buff to diagonal miner
class Booster(Building):
    def __init__(self, name, coord) -> None:
        super().__init__(name, coord)
        self.affact_range = list(
            map(
                lambda c: (c[0] + self.coord[0], c[1] + self.coord[1]),
                (product([1, -1], [1, -1])),
            )
        )

    def display_info(self):
        document = QTextDocument()
        document.setDocumentMargin(0)
        document.setHtml(f"""<b>Booster</b>""")
        pixmap = QPixmap(document.size().toSize())
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        document.drawContents(painter)
        painter.end()
        icon = QIcon(pixmap)
        return pixmap, icon

    def offer_buff(self) -> dict[Coord, Buff]:
        def callback(dictionary):
            dictionary["red"] += 1
            dictionary["green"] += 1
            dictionary["blue"] += 1
            return dictionary

        buffs: dict[Coord, Buff] = {}
        for c in self.affact_range:
            if c[0] >= 0 and c[0] <= 4 and c[1] >= 0 and c[1] <= 4:
                buffs[c] = callback
        return buffs


# use every related miner's 10% total resoure as learner mine speed.
class Learner(Building):
    def __init__(self, name, coord) -> None:
        super().__init__(name, coord)
        self.affact_range = list(
            map(
                lambda c: (c[0] + self._coord[0], c[1] + self._coord[1]),
                (product([1, -1], [1, -1])),
            )
        )
        self.resource: dict[Resource, int] = defaultdict(int)
        self.base_status: Status = defaultdict(int)


class ShopItem:
    info: dict[str, type[Building]] = {"Base": DefaultMiner, "Booster": Booster}
    tooltips: dict[str, str] = {
        "Base": "Mine every resource 1 per second.",
        "Booster": "Booster",
    }

    def __init__(self, name: str, sale_price: int) -> None:
        self.name: str = name
        self.sale_price: int = sale_price

    @property
    def sale_info(self) -> str:
        return f"{self.name}\n${self.sale_price}"

    @property
    def tooltip(self) -> str:
        return ShopItem.tooltips[self.name]

    def on_sale(self, coord) -> Building:
        m = ShopItem.info[self.name]
        return m(self.name, coord)


class GameController:
    def __init__(self) -> None:
        self.gold = 10000
        self.coords = product(range(5), range(5))
        self.grids: dict[Coord, Building] = {coord: None for coord in self.coords}
        self.selected: Coord = (-1, -1)

        self.shop_items: list[ShopItem] = [
            ShopItem("Base", 0),
            ShopItem("Booster", 10),
        ]

        self.global_buff_collection: dict[Coord, list[Buff]] = defaultdict(list)

    @property
    def grid_not_None(self) -> list[Coord]:
        return [c[0] for c in self.grids.items() if c[1] is not None]

    def on_shop(self, index: int):
        if self.gold < self.shop_items[index].sale_price:
            return
        if self.selected == (-1, -1):
            return
        if self.grids[self.selected] is not None:
            return
        self.grids[self.selected] = self.shop_items[index].on_sale(self.selected)
        self.gold -= self.shop_items[index].sale_price
        self.selected = (-1, -1)

    def on_select(self, coord):
        if self.selected != coord:
            self.selected = coord
        else:
            self.selected = (-1, -1)

    def is_selected(self, coord):
        return coord == self.selected

    def update(self):
        self.global_buff_collection.clear()
        for c in self.grid_not_None:
            buffs = self.grids[c].offer_buff()
            for c1, buff in buffs.items():
                if c1 in self.grid_not_None:
                    self.global_buff_collection[c1].append(buff)
        for c in self.grid_not_None:
            self.grids[c].update(self.global_buff_collection[c])


class MyWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test")
        self.statusBar().clearMessage()

        # load key data
        self.game = GameController()

        # 主体组件
        self.global_widget = QWidget()

        # 上方资源栏
        self.info_group = QGroupBox(f"Resource")
        self.info_gold_label = QLabel("Gold:")
        self.info_gold = QLabel()

        self.info_group_layout = QGridLayout(self.info_group)
        self.info_group_layout.addWidget(self.info_gold_label, 0, 0)
        self.info_group_layout.addWidget(self.info_gold, 0, 1)

        # 中间主布局
        self.main_grid = QWidget()
        self.main_grid_layout = QGridLayout(self.main_grid)
        self.main_grid_items: dict[Coord, QPushButton] = {
            c: QPushButton() for c in product(range(5), range(5))
        }
        # define 空间
        for i in range(5):
            for j in range(5):
                self.main_grid_items[(i, j)] = QPushButton(self.main_grid)
                self.main_grid_items[(i, j)].setMinimumSize(60, 60)
                self.main_grid_items[(i, j)].clicked.connect(
                    partial(self.game.on_select, (i, j))
                )
                self.main_grid_layout.addWidget(self.main_grid_items[(i, j)], i, j)

        # 下方商店布局
        self.shop = QGroupBox("Shop")
        self.shop.setMinimumHeight(100)
        self.shop_layout = QHBoxLayout(self.shop)

        self.shop_items: list[QPushButton] = []
        for i in range(len(self.game.shop_items)):
            self.shop_items.append(QPushButton())
            self.shop_items[-1].setMaximumHeight(60)
            self.shop_items[-1].clicked.connect(partial(self.game.on_shop, i))
            self.shop_items[-1].setText(self.game.shop_items[i].sale_info)
            self.shop_items[-1].setToolTip(self.game.shop_items[i].tooltip)
            self.shop_layout.addWidget(self.shop_items[-1])

        # 设置主布局
        self.global_layout = QVBoxLayout(self.global_widget)
        self.global_layout.addWidget(self.info_group)
        self.global_layout.addWidget(self.main_grid)
        self.global_layout.addWidget(self.shop)

        self.setCentralWidget(self.global_widget)

        # 创建并启动一个定时器
        self.global_timer = QTimer(self)
        self.global_timer.timeout.connect(self.global_update)
        self.global_timer.start(50)

    def global_update(self):
        self.game.update()
        self.info_gold.setText(str(self.game.gold))
        for i in range(5):
            for j in range(5):
                if self.game.is_selected((i, j)):
                    self.main_grid_items[(i, j)].setStyleSheet(
                        "QPushButton {background-color: #E0F0FC;}"
                    )
                else:
                    self.main_grid_items[(i, j)].setStyleSheet("")
                if self.game.grids[(i, j)] is not None:
                    pixmap, icon = self.game.grids[(i, j)].display_info()
                    self.main_grid_items[(i, j)].setIcon(icon)
                    self.main_grid_items[(i, j)].setIconSize(pixmap.size())
                    self.main_grid_items[(i, j)].setText("")
                else:
                    self.main_grid_items[(i, j)].setText("放置")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = MyWidget()
    widget.show()
    sys.exit(app.exec())
