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
from abc import abstractmethod

Resource: TypeAlias = Literal["red", "green", "blue"]
Status: TypeAlias = dict[Resource, int]
Buff: TypeAlias = Callable[[Status], Status]
Coord: TypeAlias = tuple[int, int]

# Miner: 分颜色，每秒挖颜色矿物1个，储量上限为100
# Booster: 四角Miner/learner每次多挖一个矿
# AdvBooster: 四角Miner/learner每次多挖1倍的指定颜色的矿
# Learner: 四周矿机储量的10%作为自身挖掘速度，任意矿的自身储量大于仓库同类矿的储量时停产。
# Market: 每秒扣除仓库中各种矿1个，生产1gold
# Sender: 八方向生产者每秒上传所有矿一个至仓库

# 效果怎么做：
# Miner: 每帧向Controller发送{Coord:Buff}: Buff是10%的自身资源量
# *Boooster: 每帧向Controller发送{Coord：Buff}： Buff是全种类矿物+1
# Learner: 不发送Buff
# Market/Sender: 不发送Buff？？？

# Buff 通过设计优先级，实现先加减后乘除

class Building:
    def __init__(self, name: str, coord: Coord) -> None:
        self.name: str = name
        self.coord: Coord = coord

    def display_info(self) -> tuple[bool, str]:
        return ""

    def offer_buff(self) -> dict[Coord, Buff]:
        return {}
    
class Producer(Building):
    def __init__(self, name: str, coord: tuple[int, int]) -> None:
        super().__init__(name, coord)
    
    @abstractmethod
    def produce(self, buffs: list[Buff]): ...
    
    
class Buffer(Building):
    def __init__(self, name: str, coord: tuple[int, int]) -> None:
        super().__init__(name, coord)
    
    @abstractmethod
    def offer_buff(self) -> dict[Coord, Buff]: ...


class DefaultMiner(Producer):
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
        string = f"""<font color=red>{self.resource['red']}</font>
            <font color=green>{self.resource['green']}</font>
            <font color=blue>{self.resource['blue']}</font>"""
        return True, string

    def update(self, buffs: list[Buff]):
        self.time += 1
        if self.time % self.time_per_update == 0:
            status = deepcopy(self.base_status)
            for buff in buffs:
                status = buff(status)
            for k, v in status.items():
                if k in self.resource:
                    self.resource[k] += v


class Booster(Buffer):
    def __init__(self, name, coord) -> None:
        super().__init__(name, coord)
        self.affact_range = list(
            map(
                lambda c: (c[0] + self.coord[0], c[1] + self.coord[1]),
                (product([1, -1], [1, -1])),
            )
        )

    def display_info(self):
        return False, "Booster"

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


class Learner(Producer):
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
        self.resources = {
            "red": 1,
            "green": 1,
            "blue": 1
        }
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
        
    def on_sale(self):
        if self.selected == (-1, -1):
            return

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

        # 左上方资源栏
        self.info_group = QGroupBox("Resource")
        self.info_gold_label = QLabel("Gold:")
        self.info_gold_label.setStyleSheet("QLabel { color: gold;}")
        self.info_gold = QLabel()
        self.info_gold.setStyleSheet("QLabel { color: gold;}")
        self.info_red_label = QLabel("Red:")
        self.info_red_label.setStyleSheet("QLabel { color: red;}")
        self.info_red = QLabel()
        self.info_red.setStyleSheet("QLabel { color: red;}")
        self.info_green_label = QLabel("Green:")
        self.info_green_label.setStyleSheet("QLabel { color: green;}")
        self.info_green = QLabel()
        self.info_green.setStyleSheet("QLabel { color: green;}")
        self.info_blue_label = QLabel("Blue:")
        self.info_blue_label.setStyleSheet("QLabel { color: blue;}")
        self.info_blue = QLabel()
        self.info_blue.setStyleSheet("QLabel { color: blue;}")

        self.info_group_layout = QGridLayout(self.info_group)
        self.info_group_layout.addWidget(self.info_gold_label, 0, 0)
        self.info_group_layout.addWidget(self.info_gold, 0, 1)
        self.info_group_layout.addWidget(self.info_red_label, 0, 2)
        self.info_group_layout.addWidget(self.info_red, 0, 3)
        self.info_group_layout.addWidget(self.info_green_label, 0, 4)
        self.info_group_layout.addWidget(self.info_green, 0, 5)
        self.info_group_layout.addWidget(self.info_blue_label, 0, 6)
        self.info_group_layout.addWidget(self.info_blue, 0, 7)

        # 左中间主布局
        self.main_grid = QGroupBox("Mine Field")
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

        # 左下方商店布局
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
            
        # 右上方出售按钮
        self.sale = QGroupBox("Sale")
        self.sale_layout = QVBoxLayout(self.sale)
        self.sale_button = QPushButton("Sale\nSelected", self.sale)
        self.sale_layout.addWidget(self.sale_button)    
        
        # 右中下侧升级布局
        self.upgrade = QGroupBox("Upgrade")
        self.upgrade_layout = QVBoxLayout(self.upgrade)

        # 设置主布局
        self.global_layout = QGridLayout(self.global_widget)
        self.global_layout.addWidget(self.info_group, 0, 0)
        self.global_layout.addWidget(self.main_grid, 1, 0)
        self.global_layout.addWidget(self.shop, 2, 0)
        self.global_layout.addWidget(self.sale, 0, 1)
        self.global_layout.addWidget(self.upgrade, 1, 1, 2, 1)
        

        self.setCentralWidget(self.global_widget)

        # 创建并启动一个定时器
        self.global_timer = QTimer(self)
        self.global_timer.timeout.connect(self.global_update)
        self.global_timer.start(50)

    def global_update(self):
        self.game.update()
        self.info_gold.setText(str(self.game.gold))
        self.info_red.setText(str(self.game.resources['red']))
        self.info_green.setText(str(self.game.resources['green']))
        self.info_blue.setText(str(self.game.resources['blue']))
        for coord in product(range(5), range(5)):
            if self.game.is_selected(coord):
                self.main_grid_items[coord].setStyleSheet(
                    "QPushButton {background-color: #E0F0FC;}"
                )
            else:
                self.main_grid_items[coord].setStyleSheet("")
            if self.game.grids[coord] is not None:
                rich, text = self.game.grids[coord].display_info()
                if rich:
                    document = QTextDocument()
                    document.setDocumentMargin(0)
                    document.setHtml(text)
                    pixmap = QPixmap(document.size().toSize())
                    pixmap.fill(Qt.GlobalColor.transparent)
                    painter = QPainter(pixmap)
                    document.drawContents(painter)
                    painter.end()
                    icon = QIcon(pixmap)
                    self.main_grid_items[coord].setIcon(icon)
                    self.main_grid_items[coord].setIconSize(pixmap.size())
                    self.main_grid_items[coord].setText("")
                else:
                    self.main_grid_items[coord].setText(text)
            else:
                self.main_grid_items[coord].setText("放置")
                self.main_grid_items[coord].setIcon(QIcon())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = MyWidget()
    widget.show()
    sys.exit(app.exec())
