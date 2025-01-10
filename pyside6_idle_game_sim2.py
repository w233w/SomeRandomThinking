from __future__ import annotations
from dataclasses import dataclass
from functools import partial
from itertools import product
from math import ceil
import sys
from math import floor, ceil
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
class Richness:
    土地: int
    林木: int
    石材: int
    金属: int
    淡水: int
    海洋: int


@dataclass
class RichnessUsage:
    土地: float
    林木: float
    石材: float
    金属: float
    淡水: float
    海洋: float


@dataclass
class Land:
    uid: int
    name: str
    src: str
    desc: str
    richness: Richness
    can_build: list[int]  # uid of building


@dataclass
class Building:
    uid: int
    name: str
    src: str
    desc: str
    level: int
    land_richness_usage: RichnessUsage
    cost: dict[str, int]
    population: list[int]


class LandController(QObject):
    updated = Signal()
    day_passed = Signal()

    # TODO ecs临时解决方法
    BUILDINGS: dict[int, Building] = {
        0: Building(0, "宫殿", "p.png", "", 1, RichnessUsage(0, 0, 0, 0, 0, 0), {}, []),
        1: Building(
            1, "民宅", "h.png", "", 1, RichnessUsage(0, 0, 0, 0, 0, 0), {"wood": 20}, []
        ),
        2: Building(
            2, "麦田", "c.png", "", 1, RichnessUsage(1, 0, 0, 0, 0.1, 0), {}, []
        ),
    }

    LANDS: dict[int, Land] = {
        0: Land(0, "平原", "g.png", "", Richness(10, 5, 1, 1, 0, 0), [1, 2]),
        1: Land(1, "山地", "m.png", "", Richness(1, 3, 10, 8, 0, 0), []),
        2: Land(2, "淡水", "w.png", "", Richness(0, 0, 0, 3, 10, 0), []),
        3: Land(3, "海洋", "nw.png", "", Richness(0, 0, 0, 0, 0, 10), []),
        4: Land(4, "盆地", "", "", Richness(0, 0, 0, 0, 0, 0), []),
        5: Land(5, "湿地", "", "", Richness(5, 2, 0, 0, 5, 0), []),
        6: Land(6, "林地", "", "", Richness(2, 8, 0, 0, 0, 0), []),
        7: Land(7, "森林", "", "", Richness(0, 10, 0, 0, 0, 0), []),
    }

    def __init__(self, size: int, parent: Application) -> None:
        super().__init__(parent)
        assert size >= 4
        self.food: int = 0
        self.wood: int = 0
        self.stone: int = 0
        self.metal: int = 0
        self.population: int = 0

        self.land_size = size
        self.lands: list[list[Land]] = self.gen_lend(self.land_size)
        self.buildings: list[list[Optional[Building]]] = self.gen_building(
            self.land_size
        )
        self.p = parent

    def gen_lend(self, size: int) -> list[list[Land]]:
        _land: list[list[int]] = [[0 for _ in range(size)] for _ in range(size)]
        land: list[list[Land]] = [
            [LandController.LANDS[_land[x][y]] for y in range(size)]
            for x in range(size)
        ]
        return land

    def gen_building(self, size: int) -> list[list[Optional[Building]]]:
        buildings: list[list[Optional[Building]]] = [
            [None for _ in range(size)] for _ in range(size)
        ]
        _floor, _ceil = floor(self.land_size / 2 - 0.5), ceil(self.land_size / 2 - 0.5)
        if _floor != _ceil:
            palace_x = random.randint(_floor, _ceil)
            palace_y = random.randint(_floor, _ceil)
        else:
            palace_x, palace_y = _ceil, _floor
        buildings[palace_x][palace_y] = LandController.BUILDINGS[0]
        return buildings

    def get_land_pic(self, coord) -> Land | Building:
        building = self.buildings[coord[0]][coord[1]]
        if building:
            return building
        else:
            return self.lands[coord[0]][coord[1]]

    def do(self, coord: tuple[int, int]) -> None:
        land_type = self.get_land_pic(coord)
        if isinstance(land_type, Land):
            land_info = land_type
            building_info = [
                LandController.BUILDINGS[uid] for uid in land_type.can_build
            ]
            md = MyDialog_Land(land_info, building_info, self.get_able(building_info))
            md.selected.connect(partial(self.update, coord))
            self.day_passed.connect(partial(md.refresh, self.get_able(building_info)))
            md.exec()
        elif isinstance(land_type, Building):
            md = MyDialog_Building(land_type)
            md.exec()

    def get_able(self, building_info: list[Building]) -> list[bool]:
        temp = []
        for building in building_info:
            cost = building.cost
            for resource, volumn in cost.items():
                if getattr(self, resource) <= volumn:
                    temp.append(False)
                    break
            else:
                temp.append(True)
        return temp

    def update(self, coord, a: Building) -> None:
        self.buildings[coord[0]][coord[1]] = a
        self.updated.emit()

    def day_pass(self) -> None:
        for i, j in product(range(self.land_size), range(self.land_size)):
            pic = self.get_land_pic((i, j))
            if isinstance(pic, Building):
                match pic.uid:
                    case 2:
                        self.food += 10
                    case 1:
                        self.food -= 1
                    case _:
                        pass
        self.day_passed.emit()


class MyDialog_Land(QDialog):
    selected = Signal(Building)

    def __init__(
        self, land_info: Land, building_info: list[Building], able: list[bool]
    ) -> None:
        super().__init__()
        self.setWindowTitle("Detail")

        self.bbox = QDialogButtonBox(QDialogButtonBox.StandardButton.Cancel, self)
        self.bbox.rejected.connect(self.reject)

        richness = land_info.richness

        self.info_widget = QGroupBox(f"{land_info.name} info", self)
        self.info_layout = QGridLayout(self.info_widget)
        self.土地 = QLabel(f"土地:")
        self.土地_value = QLabel(f"<b><font color=brown>{richness.土地}</font></b>")
        self.林木 = QLabel(f"林木:")
        self.林木_value = QLabel(f"<b><font color=green>{richness.林木}</font></b>")
        self.石材 = QLabel(f"石材:")
        self.石材_value = QLabel(f"<b><font color=gray>{richness.石材}</font></b>")
        self.金属 = QLabel(f"金属:")
        self.金属_value = QLabel(f"<b><font color=gold>{richness.金属}</font></b>")
        self.淡水 = QLabel(f"淡水:")
        self.淡水_value = QLabel(f"<b><font color=blue>{richness.淡水}</font></b>")
        self.海洋 = QLabel(f"海洋:")
        self.海洋_value = QLabel(f"<b><font color=darkblue>{richness.海洋}</font></b>")
        self.info_layout.addWidget(self.土地, 0, 0)
        self.info_layout.addWidget(self.土地_value, 0, 1)
        self.info_layout.addWidget(self.林木, 0, 2)
        self.info_layout.addWidget(self.林木_value, 0, 3)
        self.info_layout.addWidget(self.石材, 0, 4)
        self.info_layout.addWidget(self.石材_value, 0, 5)
        self.info_layout.addWidget(self.金属, 1, 0)
        self.info_layout.addWidget(self.金属_value, 1, 1)
        self.info_layout.addWidget(self.淡水, 1, 2)
        self.info_layout.addWidget(self.淡水_value, 1, 3)
        self.info_layout.addWidget(self.海洋, 1, 4)
        self.info_layout.addWidget(self.海洋_value, 1, 5)

        self.main_widget = QWidget(self)
        self.main_layout = QGridLayout(self.main_widget)

        for i, (building, a) in enumerate(zip(building_info, able)):
            image = QLabel(self.main_widget)
            image.setPixmap(QPixmap(building.src))
            label = QLabel(building.name, self.main_widget)
            label.setToolTip(repr(building.land_richness_usage))
            btn = QPushButton("buy", self.main_widget)
            btn.clicked.connect(partial(self.do, building))
            btn.setDisabled(not a)
            btn.setToolTip(repr(building.land_richness_usage))
            self.main_layout.addWidget(image, i, 0)
            self.main_layout.addWidget(label, i, 1)
            self.main_layout.addWidget(btn, i, 2)

        self.bbox.rejected.connect(self.reject)

        self.d_layout = QVBoxLayout()
        self.d_layout.addWidget(self.info_widget)
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


class MyDialog_Building(QDialog):
    selected = Signal(Building)

    def __init__(self, building_info: Building) -> None:
        super().__init__()
        self.setWindowTitle("Detail")

        self.bbox = QDialogButtonBox(QDialogButtonBox.StandardButton.Cancel, self)
        self.bbox.rejected.connect(self.reject)

        self.info_widget = QGroupBox(f"{building_info.name} info", self)
        self.info_layout = QGridLayout(self.info_widget)

        self.main_widget = QWidget(self)
        self.main_layout = QGridLayout(self.main_widget)

        self.bbox.rejected.connect(self.reject)

        self.d_layout = QVBoxLayout()
        self.d_layout.addWidget(self.info_widget)
        self.d_layout.addWidget(self.main_widget)
        self.d_layout.addWidget(self.bbox)
        self.setLayout(self.d_layout)

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

        self.land = LandController(4, self)
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

        # policy tab
        self.policy_tab = QWidget()
        self.define_policy_tab()
        self.tab_widget.addTab(self.policy_tab, "行政")

        # science tab
        self.science_tab = QWidget()
        self.define_science_tab()
        self.tab_widget.addTab(self.science_tab, "科技")

        # army tab
        self.army_tab = QWidget()
        self.define_army_tab()
        self.tab_widget.addTab(self.army_tab, "军事")

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
        self.food_info_value.setText(str(self.land.food))
        self.material_info_value.setText(
            str(self.land.wood + self.land.stone + self.land.metal)
        )
        self.main_progress_bar.setValue(self.main_progress_bar.value() + 10)
        if self.main_progress_bar.value() >= self.main_progress_bar.maximum():
            self.main_progress_bar.setValue(0)
            self.land.day_pass()

    def define_map_tab(self):
        self.map_tab_layout = QGridLayout(self.map_tab)
        self.map_tab_layout.setContentsMargins(0, 0, 0, 0)
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

    def define_science_tab(self):
        pass

    def define_army_tab(self):
        pass

    def save(self):
        self.showMessage("123", 3000)

    def showMessage(self, msg: str, time: int = 3000) -> None:
        self.statusBar().showMessage(msg, time)

    def closeEvent(self, event: QCloseEvent) -> None:
        return super().closeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("WindowsVista")
    window = Application()
    window.show()
    app.exec()
