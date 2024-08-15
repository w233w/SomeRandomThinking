from PySide6.QtWidgets import *
from PySide6.QtCore import QTimer, Qt, Slot
from PySide6.QtGui import QIntValidator, QColor, QAction
from dataclasses import dataclass
from itertools import product
import sys

from PySide6.QtWidgets import QWidget
from functools import partial
from copy import deepcopy

class Miner:
    
    def __init__(self, name, sale_price, coord) -> None:
        self.name = name
        self.sale_price = sale_price
        self.coord = coord
        self.resource = {
            "red": 0,
            "green": 0,
            "blue": 0,
        }
        self.action_count = 0
        self.next_action = 10

    def sale_info(self) -> str:
        return f"{self.name}\n${self.sale_price}"

    def display_info(self) -> str:
        return f"{self.resource['red']}\n{self.resource['green']}\n{self.resource['blue']}"
    
    def update(self) -> None:
        pass
    
    def tooltip(self) -> str:
        return ""


class DefaultMiner(Miner):
    def __init__(self, name, sale_price, coord) -> None:
        super().__init__(name, sale_price, coord)
        self.red_speed = 1
        self.green_speed = 1
        self.blue_speed = 1
    
    def prepare(self, **kwargs):
        for k, v in kwargs:
            if k == 'red':
                self.red_speed += v
            if k == 'green':
                self.green_speed += v
            if k == 'blue':
                self.blue_speed += v

    def update(self):
        self.action_count += 1
        if self.action_count == self.next_action:
            self.resource["red"] += 1
            self.resource["green"] += 1
            self.resource["blue"] += 1
            self.action_count = 0
    
    def tooltip(self) -> str:
        return "Mine every resource 150 per minute."


class GameController:
    def __init__(self) -> None:
        self.gold = 0
        self.coords = product(range(5), range(5))
        self.grids: dict[tuple[int, int], Miner] = {coord: None for coord in self.coords}
        self.selected: tuple[int, int] = (-1, -1)
        
        self.shop_items: list[Miner] = [
            DefaultMiner('Base', 0, None),
            DefaultMiner('red', 0, (5, 1))
        ]
        
        self.update_queue: dict[int, callable] = {}
        
    def on_shop(self, index):
        if self.gold < self.shop_items[index].sale_price:
            return
        if self.selected == (-1, -1):
            return
        if self.grids[self.selected] is not None:
            return
        self.grids[self.selected] = deepcopy(self.shop_items[index])
        self.selected = (-1, -1)

    def on_select(self, coord):
        if self.selected != coord:
            self.selected = coord
        else:
            self.selected = (-1, -1)

    def is_selected(self, coord):
        return coord == self.selected
    
    def update(self):
        for v in self.grids.values():
            if v is not None:
                v.update()


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
        self.info_gold = QLabel(str(self.game.gold))

        self.info_group_layout = QGridLayout(self.info_group)
        self.info_group_layout.addWidget(self.info_gold_label, 0, 0)
        self.info_group_layout.addWidget(self.info_gold, 0, 1)

        # 中间主布局
        self.main_grid = QWidget()
        self.main_grid_layout = QGridLayout(self.main_grid)
        self.main_grid_items: dict[tuple[int, int], QPushButton] = {
            c: QPushButton() for c in product(range(5), range(5))
        }
        # define 空间
        for i in range(5):
            for j in range(5):
                self.main_grid_items[(i, j)] = QPushButton(self.main_grid)
                self.main_grid_items[(i, j)].setMinimumSize(60, 60)
                self.main_grid_items[(i, j)].clicked.connect(partial(self.game.on_select, (i,j)))
                self.main_grid_layout.addWidget(self.main_grid_items[(i, j)], i, j)

        # 下方商店布局
        self.shop = QGroupBox("Shop")
        self.shop.setMinimumHeight(100)
        self.shop_layout = QHBoxLayout(self.shop)
        
        self.shop_items: list[QPushButton] = []
        for i in range(len(self.game.shop_items)):
            self.shop_items.append(QPushButton())
            self.shop_items[-1].setMaximumSize(60, 60)
            self.shop_items[-1].clicked.connect(partial(self.game.on_shop, i))
            self.shop_items[-1].setText(self.game.shop_items[i].sale_info())
            self.shop_items[-1].setToolTip(self.game.shop_items[i].tooltip())
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
        for i in range(5):
            for j in range(5):
                if self.game.is_selected((i, j)):
                    self.main_grid_items[(i, j)].setStyleSheet('QPushButton {background-color: #E0F0FC;}')
                else:
                    self.main_grid_items[(i, j)].setStyleSheet('')
                if self.game.grids[(i, j)] is not None:
                    self.main_grid_items[(i, j)].setText(self.game.grids[(i, j)].display_info())
                else:
                    self.main_grid_items[(i, j)].setText("放置")
                    


if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = MyWidget()
    widget.show()
    sys.exit(app.exec())
