from PySide6.QtWidgets import *
from PySide6.QtCore import QTimer, Qt, Signal
from PySide6.QtGui import QTextDocument, QPixmap, QPainter, QIcon
from itertools import product
import sys

from PySide6.QtWidgets import QWidget
from functools import partial
from collections import defaultdict
from copy import deepcopy
from typing import Callable, TypeAlias, Literal, Any
from abc import abstractmethod, abstractstaticmethod
import random


class Skill:
    def __init__(self) -> None:
        self.mana_request = 0

    @abstractmethod
    def apply(self, items) -> None: ...


class Dice:
    def __init__(self) -> None:
        self.pool = [1, 2, 3, 4, 5, 6]
        self.mana_carry = 0

    def roll(self) -> int:
        return random.choice(self.pool)


class Character:
    def __init__(self, name, hp, mana) -> None:
        self.name: str = name
        self.max_hp: int = hp
        self.hp: int = self.max_hp
        self.max_mana: int = mana
        self.mana: int = self.max_mana


class GameController:
    def __init__(self) -> None:
        self.selected = []

    def on_select(self, item):
        if item in self.selected:
            self.selected.remove(item)
        else:
            self.selected.append(item)

    def is_selected(self, item):
        return item in self.selected

    def action(self, source):
        source.vaildate(self.selected)


class CharacterCard(QGroupBox):
    def __init__(self, character, parent: QWidget) -> None:
        super().__init__("test", parent)
        self.character: Character = character
        self.layout = QHBoxLayout(self)
        # 左侧物品
        self.layout.addWidget(QLabel("Item"))
        # 中间信息
        self.middle_widget = QWidget()
        self.middle_widget_layout = QVBoxLayout(self.middle_widget)
        self.middle_widget_layout.addWidget(QLabel(self.character.name))
        self.middle_widget_layout.addWidget(QLabel(str(self.character.hp)))
        self.middle_widget_layout.addWidget(QLabel(str(self.character.mana)))
        # 右侧技能
        self.skill_widget = QWidget()
        self.skill_widget_layout = QVBoxLayout(self.skill_widget)
        self.skill_widget_layout.addWidget(QLabel("skill"))
        self.skill_widget_layout.addWidget(QLabel("skill"))

        self.layout.addWidget(self.middle_widget)
        self.layout.addWidget(self.skill_widget)


class MyWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test")

        # load key data
        self.game = GameController()

        # 主体组件
        self.global_widget = QWidget()

        # 顶部stage info
        self.stage_info = QGroupBox("Stage")
        self.stage_info_layout = QHBoxLayout(self.stage_info)
        self.stage_info_layout.addWidget(QLabel("stage"))
        self.stage_info_layout.addWidget(QLabel("stage"))

        # 中左self
        self.player = QWidget()
        self.player_layout = QVBoxLayout(self.player)
        self.player_layout.addWidget(CharacterCard(Character("123", 2, 1), self))
        self.player_layout.addWidget(CharacterCard(Character("1234", 2, 2), self))
        self.player_layout.addWidget(CharacterCard(Character("1235", 1, 1), self))
        self.player_layout.addWidget(CharacterCard(Character("1236", 2, 4), self))

        # 中battle info
        self.battle_info = QWidget()
        self.battle_info_layout = QVBoxLayout(self.battle_info)
        self.battle_info_layout.addWidget(QLabel("info"))

        # 中右enemy
        self.enemys = QWidget()
        self.enemys_layout = QVBoxLayout(self.enemys)
        self.enemys_layout.addWidget(QLabel("Enemy"))
        self.enemys_layout.addWidget(QLabel("Enemy"))
        self.enemys_layout.addWidget(QLabel("Enemy"))
        self.enemys_layout.addWidget(QLabel("Enemy"))

        # 下方inventory
        self.inventory = QGroupBox("Inventory")
        self.inventory_layout = QGridLayout(self.inventory)
        self.inventory_layout.addWidget(QLabel("inventory"), 0, 0)
        self.inventory_layout.addWidget(QLabel("inventory"), 1, 0)
        self.inventory_layout.addWidget(QLabel("inventory"), 0, 1)
        self.inventory_layout.addWidget(QLabel("inventory"), 1, 1)

        # 设置主布局
        self.global_layout = QGridLayout(self.global_widget)
        self.global_layout.addWidget(self.stage_info, 0, 0, 1, 3)
        self.global_layout.addWidget(self.player, 1, 0)
        self.global_layout.addWidget(self.battle_info, 1, 1)
        self.global_layout.addWidget(self.enemys, 1, 2)
        self.global_layout.addWidget(self.inventory, 2, 0, 1, 3)

        self.setCentralWidget(self.global_widget)

        # 创建并启动一个定时器
        self.global_timer = QTimer(self)
        self.global_timer.timeout.connect(self.global_update)
        self.global_timer.start(50)

    def global_update(self):
        pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = MyWidget()
    widget.show()
    sys.exit(app.exec())
