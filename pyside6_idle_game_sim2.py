from __future__ import annotations
from dataclasses import dataclass
import enum
from functools import partial
from itertools import product
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

from numpy import isin


@dataclass
class Land:
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


class LandController(QObject):
    updated = Signal()
    day_passed = Signal()
    
    BUILDINGS: dict[int, Building] = {
        0: Building(0, "麦田", "c.png", "", 1, {}),
        1: Building(1, "民宅", "h.png", "", 1, {"wood": 20}),
    }

    LANDS: dict[int, Land] = {
        0: Land(0, "normal", "g.png", "", [BUILDINGS[0], BUILDINGS[1]]),
        1: Land(1, "palace", "p.png", "", []),
        2: Land(2, "mountain", "m.png", "", []),
        3: Land(3, "normal-water", "w.png", "", []),
        4: Land(4, "salt-water", "nw.png", "", []),
        5: Land(5, "盆地", "", "", []),
    }

    def __init__(self, size: int) -> None:
        super().__init__()
        assert size >= 4
        self.grain: int = 0
        self.meat: int = 0
        self.wood: int = 0
        self.stone: int = 0
        self.metal: int = 0
        self.population: int = 0

        self.land_size = size
        self.lands: list[list[Land]] = self.gen_lend(self.land_size)
        self.buildings : list[list[Optional[Building]]] = [[None for _ in range(size)] for _ in range(size)]

        for a in self.lands:
            for b in a:
                if b.uid == 0:
                    pass
                if b.uid == 1:
                    self.population += 100

    def gen_lend(self, size: int) -> list[list[Land]]:
        _land: list[list[int]] = [[0 for _ in range(size)] for _ in range(size)]
        palace_x = random.randint(1, self.land_size - 2)
        palace_y = random.randint(1, self.land_size - 2)
        _land[palace_x][palace_y] = 1
        land: list[list[Land]] = [[LandController.LANDS[_land[x][y]] for y in range(size)] for x in range(size)]
        return land
    
    def get_land_pic(self, coord) -> Land | Building:
        building = self.buildings[coord[0]][coord[1]]
        if building:
            return building
        else: 
            return self.lands[coord[0]][coord[1]]

    def do(self, coord: tuple[int, int]) -> None:
        menu_info = self.lands[coord[0]][coord[1]].can_build
        md = MyDialog(menu_info, self.get_able())
        md.selected.connect(partial(self.update, coord))
        self.day_passed.connect(partial(md.refresh, self.get_able()))
        md.exec()
        
    def get_able(self) -> list[bool]:
        return [True, bool(random.randint(0, 1))]

    def update(self, coord, a: Building) -> None:
        self.buildings[coord[0]][coord[1]] = a
        self.updated.emit()

    def day_pass(self) -> None:
        for (i, j) in product(range(self.land_size), range(self.land_size)):
            pic = self.get_land_pic((i, j))
            if isinstance(pic, Building):
                match pic.uid:
                    case 0:
                        self.grain += 10
                    case 1:
                        self.grain -= 1
                    case _:
                        pass
        self.day_passed.emit()


class MyDialog(QDialog):
    selected = Signal(Building)

    def __init__(self, info: list[Building], able: list[bool]) -> None:
        super().__init__()
        self.setWindowTitle("Detail")

        self.bbox = QDialogButtonBox(QDialogButtonBox.StandardButton.Cancel, self)
        self.bbox.rejected.connect(self.reject)

        self.main_widget = QWidget(self)
        self.main_layout = QGridLayout(self.main_widget)

        for i, (building, a) in enumerate(zip(info, able)):
            image = QLabel()
            image.setPixmap(QPixmap(building.src))
            label = QLabel(building.name)
            btn = QPushButton("buy")
            btn.clicked.connect(partial(self.do, building))
            btn.setDisabled(not a)
            self.main_layout.addWidget(image, i, 0)
            self.main_layout.addWidget(label, i, 1)
            self.main_layout.addWidget(btn, i, 2)

        self.bbox.rejected.connect(self.reject)

        self.d_layout = QVBoxLayout()
        self.d_layout.addWidget(self.main_widget)
        self.d_layout.addWidget(self.bbox)
        self.setLayout(self.d_layout)

    def refresh(self, able: list[bool]) -> None:
        for i, b in enumerate(able):
            btn = self.main_layout.itemAtPosition(i, 2).widget()
            assert isinstance(btn, QPushButton)
            btn.setDisabled(not b)

    @Slot(int)
    def do(self, res: Building):
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

        self.land = LandController(4)
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
        for r in range(self.land.land_size):
            temp = []
            for c in range(self.land.land_size):
                land_pic: Land | Building = self.land.get_land_pic((r, c))
                btn = QToolButton()
                icon = QIcon(land_pic.src)
                btn.setIcon(icon)
                btn.setIconSize(btn.sizeHint())
                btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
                btn.clicked.connect(partial(self.land.do, (r, c)))
                self.map_tab_layout.addWidget(btn, r, c)
                temp.append(btn)
            self.tests.append(temp)

    def update_map_tab(self):
        for r in range(self.land.land_size):
            for c in range(self.land.land_size):
                btn = self.map_tab_layout.itemAtPosition(r, c).widget()
                assert isinstance(btn, QToolButton)
                land_pic: Land | Building = self.land.get_land_pic((r, c))
                icon = QIcon(land_pic.src)
                btn.setIcon(icon)

    def define_policy_tab(self):
        self.policy_tab_layout = QGridLayout(self.policy_tab)

    def save(self):
        self.statusBar().showMessage("123", 3000)

    def closeEvent(self, event: QCloseEvent) -> None:
        return super().closeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("WindowsVista")
    window = Application()
    window.show()
    app.exec()
