from __future__ import annotations
from dataclasses import dataclass
from functools import partial, reduce
from itertools import product, count
from math import ceil
from abc import abstractmethod
import sys
import random
from enum import Enum, IntEnum, EnumMeta
from math import floor, ceil
from typing import Any, Literal, Optional, Iterable, Dict, List
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
    QListWidget,
    QListWidgetItem,
)
from PySide6.QtCore import QEvent, QMetaObject, QSize, QTimer, Qt, Slot, Signal, QObject
from PySide6.QtGui import QAction, QCloseEvent, QPaintEvent, QPixmap, QIcon

# text based escape from tarkov


class DayTime:
    def __init__(self) -> None:
        self.day = 0
        self.hour = 0
        self.minute = 0

    def timepass(self, *, day=0, hour=0, minute=0):
        self.minute += minute
        next_hour = self.minute // 60
        self.minute %= 60

        self.hour += hour + next_hour
        next_day = self.hour // 24
        self.hour %= 24

        self.day += day + next_day

    def __repr__(self) -> str:
        return f"{str(self.day).zfill(2)}日{str(self.hour).zfill(2)}时{str(self.minute).zfill(2)}分"


class GlobalController(QObject):
    time_pass = Signal(DayTime)

    def __init__(self) -> None:
        """控制所有主要controller，减少global关键次的应用。"""
        super().__init__()
        self.time = DayTime()

        self.backpack = InventoryController()
        self.map = MapController()

        self.backpack.time_pass.connect(self.time_update)

    def time_update(self, minute_pass: int):
        self.time.timepass(minute=minute_pass)
        self.time_pass.emit(self.time)


class MapController(QObject):
    def __init__(self) -> None:
        """管理每局的所有zone"""
        super().__init__()
        self.zones: dict[tuple[int, int], ZoneController] = {}


class ZoneController(QObject):
    def __init__(self) -> None:
        """zone管理区域内所有location"""
        super().__init__()
        self.locations: dict[int, LocationController] = {}
        self.connections: dict[int, tuple[int, ...]] = {}

    def update(self, m: DayTime):
        for location in self.locations.values():
            location.update(m)


class LocationController(QObject):
    def __init__(self) -> None:
        """location包含该地点所有信息，包括单位，建筑，地形，危险度"""
        super().__init__()
        self.land_type = "plain"
        self.units = []
        self.structures = []

    def update(self, m: DayTime):
        """location内所有事物的变化"""
        pass


class InventoryController(QObject):
    time_pass = Signal(int)

    def __init__(self) -> None:
        """包含数个容器"""
        super().__init__()
        self.containers: list[ContainerController] = []

        self.containers.append(ContainerController("a", 10, self))
        self.containers.append(ContainerController("b", 15, self))
        self.containers.append(ContainerController("c", 14, self))

        for container in self.containers:
            container.item_used_time.connect(self.time_pass.emit)

        self.equipment = EquipmentController(self)

    def get_container(self, index: int):
        assert 0 <= index < len(self.containers)
        return self.containers[index]

    def get_quick_use_container(self, index: int):
        quick_use_container = [
            cont for cont in self.containers if cont.is_quick_use_container
        ]
        assert 0 <= index < len(quick_use_container)
        return quick_use_container[index]

    def equipment_query(self, item_type: str) -> list[Item]:
        res = []
        for c in self.containers:
            e_list = c.query(item_type)
            res.extend(e_list)
        return res


class ContainerController(QObject):
    """
    管理单个容器内物品
    同一类物品的每个实例可能存在不同值
    若完全一致则堆叠处理
    否则分开处理
    """

    item_used_time = Signal(int)
    item_overflow = Signal(type("Item"))
    item_use = Signal(type(callable))
    item_drop = Signal(type("Item"))

    def __init__(
        self,
        name: str,
        max_volumn: int,
        parent,
        quick_use: bool = False,
        save_container: bool = False,
    ) -> None:
        super().__init__(parent)
        self.name = name
        self.max_volumn: int = max_volumn
        self.is_quick_use_container: bool = quick_use
        self.is_save_container: bool = save_container
        assert not (self.is_quick_use_container and self.is_save_container)
        self.items: List[Item] = [
            TestUsableItem(),
            TestUsableItem(),
            TestEquipableItem("头部"),
        ]

    @property
    def volumn(self) -> int:
        res = 0
        for item in self.items:
            res += item.volumn
        return res

    def add_item(self, item_type: type[Item], quantity: int):
        for _ in range(quantity):
            item = item_type()
            if item.volumn + self.volumn <= self.max_volumn:
                self.items.append(item)
            else:
                self.item_overflow.emit(item)

    def use_item(self, item: Item):
        assert item in self.items
        self.items.remove(item)
        self.item_use.emit(item.callback)
        self.item_used_time.emit(item.use_time)

    def drop_item(self, item: Item):
        assert item in self.items
        self.items.remove(item)
        self.item_drop.emit(item)

    def query(self, eq_type: str):
        res = []
        for item in self.items:
            if isinstance(item, TestEquipableItem):
                if item.equipment_type == eq_type:
                    res.append(item)
        return res


class Item(QObject):
    id_counter = count()
    items: Dict[int, type[Item]] = {}

    class ItemType(IntEnum):
        pass

    def __init__(self) -> None:
        super().__init__()
        self.volumn = 1
        self.use_time = 10

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls._register_subclass()

    @classmethod
    def _register_subclass(cls):
        cls_id = next(Item.id_counter)
        cls.cls_id = cls_id
        Item.items[cls_id] = cls

    @abstractmethod
    def callback(self, **kwargs) -> None: ...

    @abstractmethod
    def tooltip(self) -> str: ...


class TestUsableItem(Item):
    def __init__(self) -> None:
        super().__init__()

    def callback(self, **kwargs):
        assert "p" in kwargs
        p = kwargs["p"]
        p.hp += 1

    def tooltip(self) -> str:
        return "test"


class TestEquipableItem(Item):
    def __init__(self, equipment_type: str) -> None:
        super().__init__()
        self.equipment_type = equipment_type

    def callback(self, **kwargs):
        pass

    def tooltip(self) -> str:
        return "test equipment"


class BattleController(QObject):
    def __init__(self) -> None:
        """阻止背包的使用，只能用登录快捷栏的物品"""
        super().__init__()


class EquipmentController(QObject):
    def __init__(self, parent) -> None:
        super().__init__(parent)
        self.max_volumn = 100
        self.main_hand: Optional[Item] = None
        self.off_hand: Optional[Item] = None
        self.is_dual_hand: bool = False
        self.head: Optional[Item] = None
        self.inner_cloth: Optional[Item] = None
        self.cloth: Optional[Item] = None
        self.pents: Optional[Item] = None
        self.shoes: Optional[Item] = None

    def equip(self, item: Item):
        pass


class EquipmentUI(QWidget):
    parts_table = {
        "头部": "head",
        "内搭": "inner_cloth",
        "外搭": "cloth",
        "主手": "main_hand",
        "副手": "off_hand",
        "下装": "pents",
        "鞋子": "shoes",
    }

    def __init__(
        self, equipment: EquipmentController, parent: QWidget | None = None
    ) -> None:
        super().__init__(parent)
        self.controller = equipment
        layout = QGridLayout(self)

        self.head = QPushButton(self)
        self.head.clicked.connect(partial(self.show_available_equipment, "头部"))
        self.inner_cloth = QPushButton(self)
        self.inner_cloth.clicked.connect(partial(self.show_available_equipment, "外搭"))
        self.cloth = QPushButton(self)
        self.cloth.clicked.connect(partial(self.show_available_equipment, "内搭"))
        self.main_hand = QPushButton(self)
        self.main_hand.clicked.connect(partial(self.show_available_equipment, "主手"))
        self.off_hand = QPushButton(self)
        self.off_hand.clicked.connect(partial(self.show_available_equipment, "副手"))
        self.pents = QPushButton(self)
        self.pents.clicked.connect(partial(self.show_available_equipment, "下装"))
        self.shoes = QPushButton(self)
        self.shoes.clicked.connect(partial(self.show_available_equipment, "鞋子"))
        layout.addWidget(self.head, 0, 0, 1, 0)
        layout.addWidget(self.inner_cloth, 1, 0)
        layout.addWidget(self.cloth, 1, 1)
        layout.addWidget(self.main_hand, 2, 0)
        layout.addWidget(self.off_hand, 2, 1)
        layout.addWidget(self.pents, 3, 0, 1, 0)
        layout.addWidget(self.shoes, 4, 0, 1, 0)
        self.updateUI()

    def updateUI(self):
        for name, code in EquipmentUI.parts_table.items():
            btn: QPushButton = getattr(self, code)
            item: Optional[Item] = getattr(self.controller, code)
            if item is not None:
                btn.setText(f"{name}\n" + item.__class__.__name__)
                btn.setToolTip(item.tooltip())
            else:
                btn.setText(f"{name}\n无")
                btn.setToolTip("")

    def show_available_equipment(self, query_equipment_type: str):
        inventory = self.controller.parent()
        assert isinstance(inventory, InventoryController)
        e_list = inventory.equipment_query(query_equipment_type)
        print(e_list)
        dig = EquipmentDialog(query_equipment_type, None, e_list)
        dig.acctpe_item.connect(self.re_item)
        dig.exec()

    def re_item(self, item: Optional[Item]):
        if item:  # 换装
            pass
        else:  # 卸装
            pass


class MyQListWidgetItem(QListWidgetItem):
    def __init__(self, text: str, listview: Optional[QListWidget], extra_data: Any):
        super().__init__(text, listview)
        self.extra_data = extra_data


class EquipmentDialog(QDialog):
    acctpe_item = Signal(type["Any"])

    def __init__(
        self,
        title: str,
        equipmented: Item | None,
        e_list: list[Item],
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle(title)
        self.bbox = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Cancel
            | QDialogButtonBox.StandardButton.Apply,
            self,
        )
        self.bbox.rejected.connect(self.reject)
        self.bbox.accepted.connect(self.accept)

        self.e_list = e_list

        if equipmented:
            self.equiped_widget = QGroupBox(f"{equipmented.__class__.__name__}", self)
        else:
            self.equiped_widget = QGroupBox("无", self)

        self.preview_widget = QGroupBox("预览", self)
        self.preview_widget.setMinimumSize(self.equiped_widget.size())

        self.available_equipments = QListWidget(self)
        unequip = MyQListWidgetItem("[Unequip]", self.available_equipments, None)
        for e in e_list:
            ws = MyQListWidgetItem(e.__class__.__name__, self.available_equipments, e)
            ws.setToolTip(e.tooltip())

        self.selected: Optional[Any] = None

        self.available_equipments.setCurrentItem(unequip)
        self.available_equipments.itemClicked.connect(self.set_preview)

        self.bbox.rejected.connect(self.reject)

        self.d_layout = QGridLayout(self)
        self.d_layout.addWidget(self.equiped_widget, 0, 0)
        self.d_layout.addWidget(self.preview_widget, 0, 1)
        self.d_layout.addWidget(self.available_equipments, 1, 0, 1, 2)
        self.d_layout.addWidget(self.bbox, 2, 0, 1, 2)
        self.setLayout(self.d_layout)

    def set_preview(self, item: MyQListWidgetItem):
        self.selected = item.extra_data
        if self.selected:  # 选中了某一装备
            self.preview_widget.setTitle(self.selected.__class__.__name__)
        else:  # 选择卸下
            self.preview_widget.setTitle("无")

    def accept(self) -> None:
        self.acctpe_item.emit(self.selected)
        return super().accept()


class ContainerUI(QGroupBox):
    class MyQListWidgetItem(QListWidgetItem):
        def __init__(self, text: str, listview: Optional[QListWidget], extra_data: Any):
            super().__init__(text, listview)
            self.extra_data = extra_data

    def __init__(
        self, container: ContainerController, parent: QWidget | None = None
    ) -> None:
        super().__init__(parent)

        self.container = container
        layout = QVBoxLayout(self)

        self.on_selected: Optional[Item] = None

        self.save_mark = "*" if self.container.is_save_container else ""
        self.quick_mark = "※" if self.container.is_quick_use_container else ""
        self.setTitle(
            f"{self.save_mark}{self.quick_mark}{self.container.name}【{self.container.volumn}/{self.container.max_volumn}】"
        )

        self.list = QListWidget(self)
        self.list.setMaximumWidth(120)
        for item in self.container.items:
            wd = MyQListWidgetItem(item.__class__.__name__, self.list, item)
            wd.setToolTip(item.tooltip())
        self.list.itemClicked.connect(self.select)
        layout.addWidget(self.list)

        self.buttons = QWidget()
        self.buttons_layout = QHBoxLayout(self.buttons)
        self.use_button = QPushButton("使用", self.buttons)
        self.use_button.setDisabled(not self.can_use)
        self.use_button.clicked.connect(self.use)
        self.use_button.setMaximumWidth(50)
        self.buttons_layout.addWidget(self.use_button)
        self.drop_button = QPushButton("丢弃", self.buttons)
        self.drop_button.setDisabled(not self.can_use)
        self.drop_button.clicked.connect(self.drop)
        self.drop_button.setMaximumWidth(50)
        self.buttons_layout.addWidget(self.drop_button)
        self.buttons_layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.buttons)

    def select(self, item: MyQListWidgetItem):
        self.on_selected = item.extra_data
        self.update()

    @property
    def can_use(self):
        return self.on_selected is not None

    def use(self):
        assert self.on_selected is not None
        self.container.use_item(self.on_selected)
        self.on_selected = None
        self.update()

    def drop(self):
        assert self.on_selected is not None
        self.container.drop_item(self.on_selected)
        self.on_selected = None
        self.update()

    def update(self):
        if self.on_selected is None:
            self.setTitle(
                f"{self.save_mark}{self.quick_mark}{self.container.name}【{self.container.volumn}/{self.container.max_volumn}】"
            )
            self.list.clear()
            for item in self.container.items:
                wd = MyQListWidgetItem(item.__class__.__name__, self.list, item)
                wd.setToolTip(item.tooltip())
        self.use_button.setDisabled(not self.can_use)
        self.drop_button.setDisabled(not self.can_use)


class Application(QMainWindow):
    needRender = Signal()

    def __init__(self) -> None:
        super().__init__(None)
        self.setWindowTitle("Test")
        self.statusBar().clearMessage()

        self.setWindowIcon(QIcon("c.png"))

        self.game = GlobalController()
        self.game.time_pass.connect(self.time_update)

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
        self.main_info = QGroupBox("info", self)
        self.main_info_layout = QHBoxLayout(self.main_info)

        self.day_time_value = QLabel(str(self.game.time))
        self.main_info_layout.addWidget(
            self.day_time_value, alignment=Qt.AlignmentFlag.AlignCenter
        )

        # 创建标签页控件
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

        self.tab_widget = QTabWidget()
        self.tab_widget.setTabBar(MyTabBar())
        self.tab_widget.setTabPosition(QTabWidget.TabPosition.West)

        # map tab
        self.map_tab = QWidget()
        self.define_map_tab()
        self.tab_widget.addTab(self.map_tab, "地图")

        # policy tab
        self.backpack_tab = QWidget()
        self.define_backpack_tab()
        self.tab_widget.addTab(self.backpack_tab, "背包")

        # science tab
        self.setting_tab = QWidget()
        self.define_setting_tab()
        self.tab_widget.addTab(self.setting_tab, "设置")

        self.global_widget = QWidget()
        self.global_layout = QVBoxLayout(self.global_widget)
        self.global_layout.addWidget(self.main_info)
        self.global_layout.addWidget(self.tab_widget)

        self.setCentralWidget(self.global_widget)

    def time_update(self, time: DayTime):
        self.day_time_value.setText(str(self.game.time))

    def define_map_tab(self):
        """预设"""
        self.map_tab_layout = QGridLayout(self.map_tab)
        # 左侧基本信息
        self.map_info = QGroupBox("info")
        self.map_info_layout = QGridLayout(self.map_info)
        self.map_info_layout.setSpacing(0)
        for i in range(12):
            for j in range(12):
                btn = QPushButton(f" ", self.map_info)
                btn.setMaximumWidth(40)
                self.map_info_layout.addWidget(btn, i, j)

        # 右侧可交互
        self.map_tab_layout.addWidget(self.map_info)

    def update_map_tab(self):
        pass

    def define_backpack_tab(self):
        self.backpack_tab_layout = QHBoxLayout(self.backpack_tab)

        self.equipment_widget = QGroupBox("装备")
        self.equipment_layout = QGridLayout(self.equipment_widget)
        self.backpack_tab_layout.addWidget(self.equipment_widget)
        a = EquipmentUI(self.game.backpack.equipment, self.equipment_widget)
        self.equipment_layout.addWidget(a, 0, 0)

        self.containers_widget = QGroupBox("背包")
        self.containers_layout = QGridLayout(self.containers_widget)
        self.backpack_tab_layout.addWidget(self.containers_widget)
        self.update_backpack_tab()

    def update_backpack_tab(self):
        items = self.containers_layout.count()
        for i in range(items):
            item = self.containers_layout.itemAt(i)
            self.containers_layout.removeItem(item)
            if item.widget():
                item.widget().deleteLater()
        containers = self.game.backpack.containers
        for i, container in enumerate(containers):
            l = ContainerUI(container, self.containers_widget)
            self.containers_layout.addWidget(l, 0, i)

    def define_setting_tab(self):
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
