from __future__ import annotations
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
    QMenu,
    QTableWidget,
    QHeaderView,
    QTableWidgetItem,
    QTextEdit,
    QCheckBox,
    QLayout,
    QLayoutItem,
    QTabBar,
    QStylePainter,
    QStyleOptionTab,
    QStyle,
    QSpacerItem,
    QSizePolicy,
)
from PySide6.QtCore import QSize, QTimer, Qt, Slot, Signal, QRect, QPoint
from PySide6.QtGui import QAction, QPaintEvent, QPalette
from dataclasses import dataclass, asdict, Field
import random
from typing import Any, Literal, Self, Optional
from collections import defaultdict
from functools import partial
from math import ceil
import sqlite3 as sql
import os
import json
import uuid

# 空间戒指挂机
# 空间戒指有1米见方的空间，每5秒生成一个1厘米见方的空间原石
# 空间原石可以兑换等比例空间，或者log级减少升级戒指来减少生成时间，或者攒满1米见方换一个戒指
# 戒指可以套戒指，每个空间最多有两个戒指。
# 戒指里面的戒指需要消耗上层的原石来生成更高级的原石
# 比如第二层空间的戒指能生产二级空间原石


class RingNode:
    def __init__(
        self,
        tier: int,
        level: int = 0,
        ms_pass: int = 0,
        space: int = 0,
        gem: int = 0,
        childs: list[RingNode] = [],
        parent: Optional[RingNode] = None,
        is_root: bool = False,
    ) -> None:
        self.id = uuid.uuid4()
        self.tier = tier  # 阶级，当前版本只有一阶
        self.level = level  # 等级
        self.ms_pass = ms_pass  # 距离上次生产已过去的毫秒数
        self.space = space  # 最大空间
        self.gem = gem  # 已生产
        self.childs = childs  # 空间内嵌套的戒指
        self.parent = parent  # 父戒指，主空间的戒指没有父戒指
        self.is_root = is_root

    def update(self, delta: int):
        self.ms_pass += delta
        ms_require = ceil(5000 / (1 + 0.01 * self.level))
        if self.ms_pass >= ms_require:
            if not self.parent:  # 主空间戒指
                self.gem += 1
                self.ms_pass -= ms_require
            elif self.parent and self.parent.gem > 0:  # 非主空间戒指
                self.gem += 1
                self.parent.gem -= 1
                self.ms_pass -= ms_require
            else:
                self.ms_pass = ms_require

    def can_level_up(self) -> bool:
        return self.gem >= self.level

    def level_up(self):
        self.gem -= self.level
        self.level += 1

    def can_expend_with(self, n: int) -> bool:
        return self.gem >= n

    def expend(self, n: int):
        self.gem -= n
        self.space += n


class Data:
    def __init__(self) -> None:
        self.upgrade = True
        self.move = False
        self.data = {
            "upgrade": {"upgrade": True, "move": False},
            "rings": [
                {
                    "tier": 1,
                    "level": 0,
                    "ms_pass": 0,
                    "space": 1000000,
                    "gem": [0],
                    "rings": [],
                }
            ],
        }
        self.load()

    def ring_template(self, tier: int = 1) -> dict:
        return {
            "rings": [
                {
                    "id": uuid.uuid4(),
                    "tier": tier,  # 阶级，当前版本只有一阶
                    "level": 0,  # 等级
                    "ma_pass": 0,  # 距离上次生产已过去的毫秒数
                    "space": 1000000,  # 最大空间
                    "gem": 0,  # 已生产
                    "rings": [],  # 空间内嵌套的戒指
                }
            ]
        }

    def load(self) -> None:
        if os.path.exists("save.json"):
            with open("save.json", "r") as f:
                self.data = json.load(f)

    def save(self) -> None:
        with open("save.json", "w") as f:
            json.dump(self.data, f, indent=4, ensure_ascii=False)

    # 按层遍历
    def update(self, delta: int) -> None:
        depth = 0
        visited = []


class Application(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Test")
        self.statusBar().clearMessage()

        self.data = Data()

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
        self.tab_widget.setTabPosition(QTabWidget.TabPosition.West)

        # map tab
        self.space_tab = QWidget()
        self.define_space_tab()
        self.tab_widget.addTab(self.space_tab, "空间")

        # 设置主布局
        self.global_widget = QWidget()
        global_layout = QVBoxLayout(self.global_widget)
        global_layout.addWidget(self.tab_widget)

        self.setCentralWidget(self.global_widget)

        # 创建并启动一个定时器
        self.golbal_timer_speed = 20  # ms
        self.global_timer = QTimer(self)
        self.global_timer.timeout.connect(self.global_timer_update)
        self.global_timer.setInterval(self.golbal_timer_speed)
        self.global_timer.start()  # 每20毫秒更新一次

    def define_space_tab(self):
        """设计两个组件，一个面包屑，一个HboxLayout基于data展示最多两个card，每个card是一个ring"""

        self.space_tab_layout = QVBoxLayout(self.space_tab)

    def global_timer_update(self):
        pass

    def save(self):
        pass
