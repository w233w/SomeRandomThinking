# 一种基于目标识别算法的无刻度尺读数分析方法。

from PySide6.QtWidgets import *
from PySide6.QtCore import QTimer, QSize, QRect
import sys

from itertools import product
from functools import partial
from typing import TypeAlias
from enum import IntEnum

Coord: TypeAlias = tuple[int, int]


# 后台
class Season(IntEnum):
    Spring = 0
    Summer = 1
    Autumn = 2
    Winter = 3


class General:
    def __init__(self) -> None:
        self.name = "P"
        self.health = self.max_health = 10000
        self.satiety = self.max_satiety = 10000
        self.gold = 10


class CropSeed:
    def __init__(self) -> None:
        pass


class CropItem:
    def __init__(self, name: str, quality_level: int) -> None:
        self.name: str = name
        self.quality_level: int = quality_level


class Crop:
    def __init__(
        self, seed_price: int, name: str, stages: list[str], loop: str
    ) -> None:
        self.seed_price = seed_price
        self.name = name
        self.stages = stages
        self.loop = loop
        self.grow_stage = 0
        self.grow_stage_max = len(stages) - 2
        self.grow_status = 0
        self.grow_need = 100
        self.season: list[Season] = []

    def grow(self, season: Season):
        if season in self.season:
            grow_rate = 2
        else:
            grow_rate = 1
        if self.done:
            return
        if self.grow_status >= self.grow_need:
            self.grow_stage += 1
            self.grow_status = 0
        self.grow_status += grow_rate

    @property
    def done(self) -> bool:
        return self.grow_stage > self.grow_stage_max

    @property
    def info(self) -> str:
        if not self.done:
            return f"阶段：{self.stages[self.grow_stage]}\n进度：{round(self.grow_status / self.grow_need, 2)}"
        else:
            return f"阶段：{self.stages[self.grow_stage]}"

    @property
    def sale_price(self) -> int:
        return self.seed_price

    def harvest(self) -> list[CropItem]:
        pass


crops = {
    "Cron": {
        "seed_price": 10,
        "stages": ["成长", "结果", "成熟"],
        "loop": "",
    }
}


# 中间层
def Singleton(cls):
    _instance = {}

    def _singleton(*args, **kargs):
        if cls not in _instance:
            _instance[cls] = cls(*args, **kargs)
        return _instance[cls]

    return _singleton


class FarmController:
    def __init__(self) -> None:
        self.size = 3
        self.farm: dict[Coord, Crop | None] = {
            c: None for c in product(range(self.size), range(self.size))
        }
        self.updated: set[Coord] = set()
        self.skip_confirm = False
        self.selected_crop: str | None = None

    def __getitem__(self, coord: Coord):
        if not isinstance(coord, tuple):
            raise KeyError()
        return self.farm[coord]

    def change_skip(self):
        self.skip_confirm = not self.skip_confirm

    def plant(self, coord: Coord):
        self.farm[coord] = Crop(**crops[self.selected_crop], name=self.selected_crop)
        self.updated.add(coord)

    def on_sale(self, coord: Coord) -> int:
        crop = self.farm[coord]
        if crop is None:
            raise RuntimeError()
        self.farm[coord] = None
        self.updated.add(coord)
        return crop.sale_price

    def update(self, season: Season):
        for k, v in self.farm.items():
            if v is not None:
                v.grow(season)
                self.updated.add(k)

    def end(self):
        self.updated.clear()


class BackpackController:
    def __init__(self) -> None:
        self.container: dict[str, int] = {}


class TimeController:
    def __init__(self) -> None:
        self.ts = 0


@Singleton
class GameController:
    def __init__(self) -> None:
        self.farm = FarmController()
        self.general = General()

    def farm_sale(self, field: Coord):
        self.general.gold += self.farm.on_sale(field)

    def update(self):
        self.farm.update(Season.Spring)


game = GameController()


# 前台
class MainView(QWidget):
    def __init__(self, parent: QWidget | None = ...) -> None:
        super().__init__(parent)
        self.layout = QGridLayout(self)
        self.name = QLabel("Name: ")
        self.name_info = QLabel(game.general.name)
        self.layout.addWidget(self.name, 0, 0)
        self.layout.addWidget(self.name_info, 0, 1)
        self.gold = QLabel("Gold: ")
        self.gold_info = QLabel(str(game.general.gold))
        self.layout.addWidget(self.gold, 0, 2)
        self.layout.addWidget(self.gold_info, 0, 3)
        self.health = QProgressBar(self)
        self.health.setRange(0, 10000)
        self.health.setTextVisible(False)
        self.health.setValue(10000)
        self.layout.addWidget(self.health, 1, 0, 1, 2)

    def update(self):
        self.gold_info.setText(str(game.general.gold))


class ConfirmDialog(QDialog):
    def __init__(
        self,
        text: str = "",
        parent: QWidget | None = ...,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("Confirm")
        self.layout = QVBoxLayout(self)

        self.text = QLabel(self)
        self.text.setText(text)
        self.layout.addWidget(self.text)

        self.button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self
        )
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.layout.addWidget(self.button_box)


class FarmView(QWidget):
    def __init__(self, parent: QWidget | None = ...) -> None:
        super().__init__(parent)
        self.layout = QVBoxLayout(self)

        self.skip_confirm = QCheckBox("Skip confirm", self)
        self.skip_confirm.stateChanged.connect(game.farm.change_skip)
        self.layout.addWidget(self.skip_confirm)

        self.quick_plant = QComboBox(self)
        self.quick_plant.addItem("--None--", None)
        for name, crop in crops.items():
            self.quick_plant.addItem(name, crop)
        self.quick_plant.currentIndexChanged.connect(self.on_combobox_changed)

        self.layout.addWidget(self.quick_plant)

        self.farm_layout = QGridLayout()
        for field, crop in game.farm.farm.items():
            btn = QPushButton()
            if crop is not None:
                btn.setText(crop.name)
                btn.setToolTip(crop.info)
                btn.clicked.connect(partial(self.remove, field, crop))
            else:
                btn.clicked.connect(partial(self.plant, field))
            btn.setMinimumSize(60, 60)
            self.farm_layout.addWidget(btn, field[0], field[1])
        self.layout.addLayout(self.farm_layout)

    def on_combobox_changed(self):
        game.farm.selected_crop = self.quick_plant.currentText()

    def plant(self, field: Coord):
        if self.quick_plant.currentData() is not None:
            game.farm.plant(field)

    def remove(self, coord: Coord, crop: Crop | None):
        if crop is None:
            return
        if not game.farm.skip_confirm:
            d = ConfirmDialog("Sale?", self)
            if not d.exec():
                return
        game.farm_sale(coord)

    def update(self):
        if not game.farm.updated:
            return
        for field in game.farm.updated:
            crop = game.farm[field]
            btn: QPushButton = self.farm_layout.itemAtPosition(*field).widget()
            btn.clicked.disconnect()
            if crop is not None:
                btn.setText(crop.name)
                btn.setToolTip(crop.info)
                btn.clicked.connect(partial(self.remove, field, crop))
            else:
                btn.setText("")
                btn.setToolTip("")
                btn.clicked.connect(partial(self.plant, field))
        game.farm.end()


class MyApplication(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test")

        # 主体组件
        self.tabview = QTabWidget()

        # 首页tab
        self.main_tab = MainView(self)
        self.tabview.addTab(self.main_tab, "main")

        # food tab
        self.food_tab = QTabWidget(self)
        self.food_tab_layout = QGridLayout(self.food_tab)
        self.tabview.addTab(self.food_tab, "food")

        # farm tab
        self.farm_tab = FarmView(self)
        self.tabview.addTab(self.farm_tab, "farm")

        # 设置主布局
        self.setCentralWidget(self.tabview)

        # 创建并启动一个定时器
        self.global_timer = QTimer(self)
        self.global_timer.timeout.connect(self.global_update)
        self.global_timer.start(50)

    def global_update(self):
        game.update()
        self.farm_tab.update()
        self.main_tab.update()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = MyApplication()
    widget.show()
    sys.exit(app.exec())
