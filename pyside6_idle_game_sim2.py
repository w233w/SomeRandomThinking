from __future__ import annotations
import enum
from functools import partial
import sys
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QStackedLayout,
    QGridLayout,
    QProgressBar,
    QTabWidget,
    QGroupBox,
    QPushButton,
    QToolButton,
    QMenu,
    QTabBar,
    QStylePainter,
    QStyleOptionTab,
    QStyle,
    QDialog,
    QDialogButtonBox,
    QMessageBox,
    QCheckBox,
)
from PySide6.QtCore import QEvent, QSize, QTimer, Qt, Slot, Signal, QObject
from PySide6.QtGui import QAction, QPaintEvent, QPixmap, QIcon

import random


class Land(QObject):
    """
    template example:
    #####
    #000#
    #010#
    #003#
    #####
    0 for normal land.
    1 for palace, only for first land. otherwise for normal land.
    2 for mountain.
    3 for plain-waterbody.
    4 for salt-waterbody.
    5 for 盆地
    """

    SRC: dict[int, dict[str, str]] = {
        0: {"name": "normal", "src": "g.png"},
        1: {"name": "palace", "src": "p.png"},
        2: {"name": "mountain", "src": ""},
        3: {"name": "normal-water", "src": ""},
        4: {"name": "salt-water", "src": ""},
        5: {"name": "盆地", "src": ""},
        6: {"name": "麦田", "src": "c.png"},
    }

    def __init__(self, size: int) -> None:
        super().__init__(None)
        self.grain: int = 0
        self.meat: int = 0
        self.wood: int = 0
        self.stone: int = 0
        self.metal: int = 0

        self.land_size = size
        self.land = self.gen_lend(self.land_size)

    def gen_lend(self, size: int) -> list:
        land = [[0 for _ in range(size)] for _ in range(size)]
        palace_x = random.randint(1, self.land_size - 2)
        palace_y = random.randint(1, self.land_size - 2)
        land[palace_x][palace_y] = 1
        sea_level = int(random.random() * 10)
        return land

    def do(self, coord):
        md = MyDialog([123])
        md.exec()


class MyDialog(QDialog):
    def __init__(self, info) -> None:
        super().__init__()
        self.info = info

        self.bbox = QDialogButtonBox(QDialogButtonBox.StandardButton.Cancel)
        self.bbox.setOrientation(Qt.Orientation.Vertical)

        self.btn = QToolButton()
        self.btn.setIcon(QIcon("c.png"))
        self.btn.setIconSize(QSize(30, 30))
        self.bbox.addButton(self.btn, QDialogButtonBox.ButtonRole.ActionRole)

        self.btn.clicked.connect(self.do)

        self.l = QLabel()
        self.l.setPixmap(QPixmap("c.png"))

        self.bbox.rejected.connect(self.reject)

        layout = QHBoxLayout(self)
        layout.addWidget(self.l)
        layout.addWidget(self.bbox)
        self.setLayout(layout)

    def do(self):
        print(self.info)


class MyTabBar(QTabBar):
    def paintEvent(self, event: QPaintEvent):
        painter = QStylePainter(self)
        option = QStyleOptionTab()
        for index in range(self.count()):
            self.initStyleOption(option, index)
            painter.drawControl(QStyle.ControlElement.CE_TabBarTabShape, option)
            painter.drawText(
                self.tabRect(index),
                Qt.AlignmentFlag.AlignCenter | Qt.TextFlag.TextDontClip,
                self.tabText(index),
            )

    def tabSizeHint(self, index):
        size = QTabBar.tabSizeHint(self, index)
        if size.width() < size.height():
            size.transpose()
        return size


class Application(QMainWindow):
    def __init__(self) -> None:
        super().__init__(None)
        self.setWindowTitle("Test")
        self.statusBar().clearMessage()

        self.land = Land(4)

        # set menu
        game_menu = QMenu("Game", self)
        save = QAction("save", game_menu)
        save.triggered.connect(self.save)
        game_menu.addAction(save)
        ext = QAction("Exit", game_menu)
        ext.triggered.connect(self.close)
        game_menu.addAction(ext)
        self.menuBar().addMenu(game_menu)

        # 创建标签页控件
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabBar(MyTabBar())
        self.tab_widget.setTabPosition(QTabWidget.TabPosition.West)

        # map tab
        self.map_tab = QWidget()
        self.define_space_tab()
        self.tab_widget.addTab(self.map_tab, "地图")

        # policy
        self.policy_tab = QWidget()
        self.define_space_tab()
        self.tab_widget.addTab(self.policy_tab, "行政")

        self.global_widget = QWidget()
        global_layout = QVBoxLayout(self.global_widget)
        global_layout.addWidget(self.tab_widget)

        self.setCentralWidget(self.global_widget)

    def define_space_tab(self):
        self.map_tab_layout = QGridLayout(self.map_tab)
        self.tests: list[list[QToolButton]] = []
        for i, row in enumerate(self.land.land):
            temp = []
            for j, land in enumerate(row):
                btn = QToolButton()
                icon = QIcon(Land.SRC[land]["src"])
                btn.setIcon(icon)
                btn.setIconSize(btn.sizeHint())
                btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
                btn.clicked.connect(partial(self.land.do, (i, j)))
                self.map_tab_layout.addWidget(btn, i, j)
                temp.append(btn)
            self.tests.append(temp)

    def save(self):
        self.statusBar().showMessage("123", 3000)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Application()
    window.show()
    app.exec()
