from PySide6.QtWidgets import *
from PySide6.QtCore import QTimer, Qt, Slot
from PySide6.QtGui import QIntValidator, QColor, QAction
from dataclasses import dataclass
from itertools import product
import sys

from PySide6.QtWidgets import QWidget
from functools import partial

class Block:
    def __init__(self, name, sale_price, coord) -> None:
        self.name = name
        self.sale_price = sale_price
        self.coord = coord
        self.resource = {
            "red": 0,
            "green": 0,
            "blue": 0,
        }

    def sale_info(self) -> str:
        return f"{self.name}\n${self.sale_price}"

    def display_info(self) -> str:
        pass


class RedBlock(Block):
    def __init__(self, name, sale_price, coord) -> None:
        super().__init__(name, sale_price, coord)

    def update(self):
        self.resource["red"] += 1


class GameController:
    def __init__(self) -> None:
        self.gold = 0
        self.coords = product(range(5), range(5))
        self.grids = {coord: None for coord in self.coords}
        self.selected: tuple[int, int] = (-1, -1)

    def on_select(self, coord):
        if self.selected != coord:
            self.selected = coord
        else:
            self.selected = (-1, -1)

    def is_selected(self, coord):
        return coord == self.selected


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
                if (i, j) == (1, 1):
                    self.main_grid_items[(i, j)].setEnabled(False)
                self.main_grid_items[(i, j)].setMinimumSize(60, 60)
                self.main_grid_items[(i, j)].clicked.connect(partial(self.game.on_select, (i,j)))
                self.main_grid_layout.addWidget(self.main_grid_items[(i, j)], i, j)

        # 下方商店布局
        self.shop = QGroupBox("Shop")
        self.shop_layout = QHBoxLayout(self.shop)

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
        for i in range(5):
            for j in range(5):
                if self.game.is_selected((i, j)):
                    self.main_grid_items[(i, j)].setText("setted")
                    self.main_grid_items[(i, j)].setStyleSheet('QPushButton {background-color: #E0F0FC;}')
                else:
                    self.main_grid_items[(i, j)].setText("放置")
                    self.main_grid_items[(i, j)].setStyleSheet('')


if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = MyWidget()
    widget.show()
    sys.exit(app.exec())
