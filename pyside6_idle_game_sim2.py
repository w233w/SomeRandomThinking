from __future__ import annotations
from dataclasses import dataclass
import enum
from functools import partial
import sys
from tokenize import Single
from typing import Any, Literal, Optional
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
from PySide6.QtGui import QAction, QCloseEvent, QPaintEvent, QPixmap, QIcon

import random


@dataclass
class LandType:
    uid: int
    name: str
    src: str
    desc: str
    can_build: list[Building]


@dataclass
class Building:
    uid: int
    name: str
    src: str
    desc: str
    level: int
    cost: dict[str, int]


@dataclass
class LandPic:
    land_type: LandType
    building: Optional[Building]

    @property
    def has_building(self) -> bool:
        return self.building is not None


class Land(QObject):
    updated = Signal()
    day_passed = Signal()

    SRC: dict[int, LandType | Building] = {
        0: LandType(0, "normal", "g.png", "", []),
        1: LandType(1, "palace", "p.png", "", []),
        2: LandType(2, "mountain", "m.png", "", []),
        3: LandType(3, "normal-water", "w.png", "", []),
        4: LandType(4, "salt-water", "nw.png", "", []),
        5: LandType(5, "盆地", "nw.png", "", []),
        6: Building(6, "麦田", "c.png", "", 1, {}),
        7: Building(7, "民宅", "", "", 1, {"Food": 20}),
    }

    def __init__(self, size: int) -> None:
        super().__init__()
        self.grain: int = 0
        self.meat: int = 0
        self.wood: int = 0
        self.stone: int = 0
        self.metal: int = 0
        self.population: int = 0

        self.land_size = size
        self.land: list[list[int]] = self.gen_lend(self.land_size)

        for a in self.land:
            for b in a:
                if b == 0:
                    pass
                if b == 1:
                    self.population += 100

    def gen_lend(self, size: int) -> list:
        land = [[0 for _ in range(size)] for _ in range(size)]
        palace_x = random.randint(1, self.land_size - 2)
        palace_y = random.randint(1, self.land_size - 2)
        land[palace_x][palace_y] = 1
        return land

    def do(self, coord):
        menu_info: list[LandType | Building] = []
        if self.land[coord[0]][coord[1]] == 0:
            menu_info = [Land.SRC[6], Land.SRC[7]]
        md = MyDialog(menu_info)
        md.selected.connect(partial(self.update, coord))
        self.day_passed.connect(md.refresh)
        md.exec()

    def update(self, coord, a: int):
        self.land[coord[0]][coord[1]] = a
        self.updated.emit()

    def day_pass(self):
        for i, row in enumerate(self.land):
            for j, land in enumerate(row):
                if land == 6:
                    self.grain += 10
        self.day_passed.emit()


class MyDialog(QDialog):
    selected = Signal(int)

    def __init__(self, info: list[LandType | Building]) -> None:
        super().__init__()
        self.setWindowTitle("Detail")
        self.info = info

        self.bbox = QDialogButtonBox(QDialogButtonBox.StandardButton.Cancel, self)
        self.bbox.rejected.connect(self.reject)

        self.main_widget = QWidget(self)
        self.main_layout = QGridLayout(self.main_widget)

        for i, land in enumerate(self.info):
            image = QLabel()
            image.setPixmap(QPixmap(land.src))
            label = QLabel(land.name)
            btn = QPushButton("buy")
            btn.clicked.connect(partial(self.do, land.uid))
            self.main_layout.addWidget(image, i, 0)
            self.main_layout.addWidget(label, i, 1)
            self.main_layout.addWidget(btn, i, 2)

        self.bbox.rejected.connect(self.reject)

        self.d_layout = QVBoxLayout()
        self.d_layout.addWidget(self.main_widget)
        self.d_layout.addWidget(self.bbox)
        self.setLayout(self.d_layout)

    def refresh(self):
        for i, land in enumerate(self.info):
            print(1)

    @Slot(int)
    def do(self, res):
        self.selected.emit(res)
        self.accept()


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
    needRender = Signal()

    def __init__(self) -> None:
        super().__init__(None)
        self.setWindowTitle("Test")
        self.statusBar().clearMessage()

        self.setWindowIcon(QIcon("c.png"))

        self.land = Land(4)
        self.land.updated.connect(self.update_map_tab)

        # set menu
        game_menu = QMenu("Game", self)
        save = QAction("save", game_menu)
        save.triggered.connect(self.save)
        game_menu.addAction(save)
        ext = QAction("Exit", game_menu)
        ext.triggered.connect(self.close)
        game_menu.addAction(ext)
        self.menuBar().addMenu(game_menu)

        # 主信息栏
        self.main_info = QGroupBox(self)
        self.main_info_layout = QGridLayout(self.main_info)

        self.food_info = QLabel("Food: ")
        self.food_info_value = QLabel("0")
        self.main_info_layout.addWidget(self.food_info, 0, 0)
        self.main_info_layout.addWidget(self.food_info_value, 0, 1)

        self.material_info = QLabel("Material: ")
        self.material_info_value = QLabel("0")
        self.main_info_layout.addWidget(self.material_info, 0, 2)
        self.main_info_layout.addWidget(self.material_info_value, 0, 3)

        # 主进度条
        self.main_progress_bar = QProgressBar(self)
        self.main_progress_bar.setRange(0, 10000)
        self.main_progress_bar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_progress_bar.setValue(0)

        # 创建标签页控件
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabBar(MyTabBar())
        self.tab_widget.setTabPosition(QTabWidget.TabPosition.West)

        # map tab
        self.map_tab = QWidget()
        self.define_map_tab()
        self.tab_widget.addTab(self.map_tab, "地图")

        # policy
        self.policy_tab = QWidget()
        self.define_policy_tab()
        self.tab_widget.addTab(self.policy_tab, "行政")

        self.global_widget = QWidget()
        self.global_layout = QVBoxLayout(self.global_widget)
        self.global_layout.addWidget(self.main_info)
        self.global_layout.addWidget(self.main_progress_bar)
        self.global_layout.addWidget(self.tab_widget)

        self.setCentralWidget(self.global_widget)

        self.global_timer = QTimer()
        self.global_timer.timeout.connect(self.global_update)
        self.global_timer.start(20)

    def global_update(self):
        self.food_info_value.setText(str(self.land.grain + self.land.meat))
        self.material_info_value.setText(
            str(self.land.wood + self.land.stone + self.land.metal)
        )
        self.main_progress_bar.setValue(self.main_progress_bar.value() + 10)
        if self.main_progress_bar.value() >= self.main_progress_bar.maximum():
            self.main_progress_bar.setValue(0)
            self.land.day_pass()

    def define_map_tab(self):
        self.map_tab_layout = QGridLayout(self.map_tab)
        self.tests: list[list[QToolButton]] = []
        for i, row in enumerate(self.land.land):
            temp = []
            for j, land in enumerate(row):
                btn = QToolButton()
                icon = QIcon(Land.SRC[land].src)
                btn.setIcon(icon)
                btn.setIconSize(btn.sizeHint())
                btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
                btn.clicked.connect(partial(self.land.do, (i, j)))
                self.map_tab_layout.addWidget(btn, i, j)
                temp.append(btn)
            self.tests.append(temp)

    def update_map_tab(self):
        for i, row in enumerate(self.land.land):
            for j, land in enumerate(row):
                btn = self.map_tab_layout.itemAtPosition(i, j).widget()
                assert isinstance(btn, QToolButton)
                icon = QIcon(Land.SRC[land].src)
                btn.setIcon(icon)

    def define_policy_tab(self):
        self.policy_tab_layout = QGridLayout(self.policy_tab)

    def save(self):
        self.statusBar().showMessage("123", 3000)

    def closeEvent(self, event: QCloseEvent) -> None:
        print(self.land.grain)
        return super().closeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Application()
    window.show()
    app.exec()
