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
    QSpinBox,
)
from PySide6.QtCore import (
    QSize,
    QTimer,
    Qt,
    Slot,
    Signal,
    QRect,
    QPoint,
    QFile,
    QMetaObject,
)
from PySide6.QtGui import QAction, QCloseEvent, QPaintEvent, QPalette
from PySide6.QtUiTools import QUiLoader
from dataclasses import dataclass, asdict, Field
import random
from typing import Any, AnyStr, Literal, Self, Optional, Union
from collections import defaultdict
from functools import partial
from math import ceil
import sqlite3 as sql
import os
import json
import uuid
from enum import Enum

# 空间戒指挂机
# 空间戒指内有空间，每几秒生成一个空间原石
# 空间原石可以兑换等比例空间，或者log级减少升级戒指来减少生成时间，或者攒满一定量换一个戒指
# 戒指可以套戒指，每个空间最多有两个戒指。


class RingNode:
    def __init__(
        self,
        parent: Optional[RingNode] = None,
        level: int = 0,
        ms_pass: int = 0,
        space: int = 100,
        gem: int = 0,
        left: dict = {},
        right: dict = {},
        modifier: dict = {},
    ) -> None:
        self.id = uuid.uuid4()
        self.parent = parent  # 父戒指，主空间的戒指没有父戒指
        self.level = level  # 等级
        self.ms_pass = ms_pass  # 距离上次生产已过去的毫秒数
        self.space = space  # 最大空间
        self.gem = gem  # 宝石量
        if left:
            self.left = RingNode(self, **left)  # 空间内嵌套的戒指1
        else:
            self.left = None
        if right:
            self.right = RingNode(self, **right)  # 空间内嵌套的戒指2
        else:
            self.right = None
        self.modifier = modifier  # 独立升级

    def update(self, delta: int) -> None:
        if self.parent:
            self.ms_pass += delta
            ms_require = self.ms_require
            if self.ms_pass >= ms_require:
                if self.depth == 1:  # 主空间戒指
                    self.gem = min(self.gem + self.ms_pass // ms_require, self.space)
                    self.ms_pass -= ms_require * self.ms_pass // ms_require
                elif self.depth > 1 and self.parent.gem > 0:  # 非主空间戒指
                    self.gem = min(self.gem + 1, self.space)
                    self.parent.gem -= 1
                    self.ms_pass -= ms_require
                else:  # 有父戒指，但父戒指没有宝石了，维持即将生产的状态
                    self.ms_pass = ms_require
        if self.left:
            self.left.update(delta)
        if self.right:
            self.right.update(delta)

    @property
    def depth(self) -> int:
        if self.parent:
            return self.parent.depth + 1
        else:
            return 0

    @property
    def ms_require(self) -> int:
        return ceil(3000 / (1 + 0.01 * self.level))

    def can_level_up(self) -> bool:
        if not self.parent:
            return False
        return self.gem >= self.level + 1

    def level_up(self) -> None:
        self.gem -= self.level + 1
        self.level += 1

    def can_expend_with(self, n: int) -> bool:
        if not self.parent:
            return False
        return self.gem >= n

    def expend(self, n: int) -> None:
        self.gem -= n
        self.space += n

    def can_new(self) -> bool:
        if self.left and self.right:
            return False
        return self.gem >= 1000

    def new(self) -> None:
        if not self.left:
            self.left = RingNode(self)
        elif not self.right:
            self.right = RingNode(self)

    def as_dict(self) -> dict[str, Any]:
        d = {
            "level": self.level,
            "ms_pass": self.ms_pass,
            "space": self.space,
            "gem": self.gem,
            "left": self.left.as_dict() if self.left else None,
            "right": self.right.as_dict() if self.right else None,
        }
        return d


class GlobalModifier:
    """大多是全局生效的buff，或者是否解锁某个功能的标志位"""

    def __init__(self) -> None:
        pass


class RingTree:
    def __init__(self, data: Optional[dict]) -> None:
        if data:
            self.root = RingNode(**data)
        else:
            self.root = RingNode(None)
            self.root.left = RingNode(self.root)
        self.current_visit = self.root

    def save(self) -> dict:
        return self.root.as_dict()

    def update(self, delta: int) -> None:
        self.root.update(delta)


class UnlockList:
    def __init__(self, **kwargs) -> None:
        self.can_new = kwargs.get("can_new", False)
        self.can_enter = kwargs.get("can_enter", False)

    def save(self) -> dict:
        return {
            "can_new": self.can_new,
            "can_enter": self.can_enter,
        }


class Data:
    def __init__(self) -> None:
        if os.path.exists("save.json"):
            with open("save.json", "r") as f:
                data = json.load(f)
                self.unlock = UnlockList(**data["unlocks"])
                self.tree = RingTree(data["rings"])
        else:
            self.unlock = UnlockList()
            self.tree = RingTree(None)

    def save(self) -> None:
        with open("save.json", "w") as f:
            json.dump(
                {
                    "unlocks": self.unlock.save(),
                    "rings": self.tree.save(),
                },
                f,
                indent=4,
                ensure_ascii=False,
            )

    def update(self, delta: int) -> None:
        self.tree.update(delta)


class CardView(QWidget):
    def __init__(self, parent) -> None:
        super().__init__(parent)
        self.gridLayout = QGridLayout(self)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)

        self.name = QLabel("Ring", self)
        self.name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.gridLayout.addWidget(self.name, 0, 1, 1, 1)

        self.enter = QPushButton("Enter", self)
        self.enter.setVisible(False)
        self.gridLayout.addWidget(self.enter, 0, 2, 1, 1)

        self.space_hint = QLabel("容量", self)
        self.gridLayout.addWidget(self.space_hint, 4, 0, 1, 1)

        self.level = QLabel("等级:", self)
        self.gridLayout.addWidget(self.level, 1, 0, 1, 1)

        self.space = QLabel("空间升级", self)
        self.space.setToolTip("使用等量的宝石交换等量的空间")
        self.gridLayout.addWidget(self.space, 3, 0, 1, 1)

        self.produce_hint = QLabel("生产", self)
        self.gridLayout.addWidget(self.produce_hint, 7, 0, 1, 1)

        self.space_upgrade_spin = QSpinBox(self)
        self.space_upgrade_spin.setRange(1, 10000)
        self.gridLayout.addWidget(self.space_upgrade_spin, 3, 1, 1, 1)

        self.new_ring = QPushButton("制造", self)
        self.new_ring.setVisible(False)
        self.gridLayout.addWidget(self.new_ring, 3, 1, 1, 1)

        self.space_upgrade = QPushButton("升级", self)
        self.gridLayout.addWidget(self.space_upgrade, 3, 2, 1, 1)

        self.level_upgrade = QPushButton("升级", self)
        self.level_upgrade.setToolTip("升级需要等级数加1的宝石")
        self.gridLayout.addWidget(self.level_upgrade, 1, 2, 1, 1)

        self.spaceBar = QProgressBar(self)
        self.spaceBar.setStyleSheet("QProgressBar::chunk{background:red}")
        self.spaceBar.setValue(24)
        self.spaceBar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spaceBar.setTextVisible(False)
        self.gridLayout.addWidget(self.spaceBar, 5, 0, 1, 3)

        self.produceBar = QProgressBar(self)
        self.produceBar.setValue(24)
        self.produceBar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.gridLayout.addWidget(self.produceBar, 8, 0, 1, 3)

        self.produce_time = QLabel("5 s", self)
        self.produce_time.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.gridLayout.addWidget(self.produce_time, 7, 2, 1, 1)

        self.space_verbose = QLabel("10000/10000", self)
        self.space_verbose.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.gridLayout.addWidget(self.space_verbose, 4, 2, 1, 1)

        self.old_linka: Optional[QMetaObject.Connection] = None
        self.old_linkb: Optional[QMetaObject.Connection] = None

    def enable_enter(self) -> None:
        self.enter.setVisible(True)

    def enable_new(self) -> None:
        self.new_ring.setVisible(True)

    def update(self, node: RingNode) -> None:
        self.produce_time.setText(f"{node.ms_require/1000:.4f} s")
        if node.ms_require <= 1000:
            self.produceBar.setRange(0, 1)
            self.produceBar.setValue(1)
            self.produceBar.setFormat(f"{1000 / node.ms_require:.2f} /s")
        else:
            self.produceBar.setRange(0, node.ms_require)
            self.produceBar.setValue(node.ms_pass)
        self.level_upgrade.setDisabled(not node.can_level_up())
        if self.old_linka:
            self.level_upgrade.pressed.disconnect(self.old_linka)
        self.old_linka = self.level_upgrade.pressed.connect(node.level_up)
        self.enter.setEnabled(bool(node.left or node.right))

        self.space_verbose.setText(f"{node.gem} / {node.space}")
        self.spaceBar.setRange(0, node.space)
        self.spaceBar.setValue(node.gem)
        self.space_upgrade.setDisabled(
            not node.can_expend_with(self.space_upgrade_spin.value())
        )
        if self.old_linkb:
            self.space_upgrade.pressed.disconnect(None)
        self.old_linkb = self.space_upgrade.pressed.connect(
            partial(node.expend, self.space_upgrade_spin.value())
        )

        self.level.setText(f"等级: {node.level}")


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

        self.upgrade_tab = QWidget()
        self.define_upgrade_tab()
        self.tab_widget.addTab(self.upgrade_tab, "升级")

        # 设置主布局
        self.global_widget = QWidget()
        global_layout = QVBoxLayout(self.global_widget)
        global_layout.addWidget(self.tab_widget)

        self.setCentralWidget(self.global_widget)

        # 创建并启动一个定时器
        self.golbal_timer_speed = 20  # ms
        self.global_timer = QTimer(self)
        self.global_timer.setTimerType(Qt.TimerType.PreciseTimer)
        self.global_timer.timeout.connect(self.global_timer_update)
        self.global_timer.setInterval(self.golbal_timer_speed)
        self.global_timer.start()  # 每20毫秒更新一次

    def define_space_tab(self) -> None:
        """设计两个组件，一个面包屑，一个HboxLayout基于data展示最多两个card，每个card里有进度条"""
        self.面包屑 = QWidget()

        self.ring_view = QWidget()
        self.ring_view_layout = QHBoxLayout(self.ring_view)

        self.ring_view_left = CardView(self.ring_view)

        self.ring_view_right = CardView(self.ring_view)

        self.space_tab_layout = QHBoxLayout(self.space_tab)
        self.space_tab_layout.addWidget(self.ring_view_left)
        self.space_tab_layout.addWidget(self.ring_view_right)

    def update_space_tab(self, unlock: UnlockList) -> None:
        node = self.data.tree.current_visit
        if node.left:
            self.ring_view_left.setVisible(True)
            if unlock.can_enter:
                self.ring_view_left.enter.setVisible(True)
            if unlock.can_new:
                self.ring_view_left.new_ring.setVisible(True)
            self.ring_view_left.update(node.left)
        else:
            self.ring_view_left.setVisible(False)
        if node.right:
            self.ring_view_right.setVisible(True)
            self.ring_view_right.update(node.right)
        else:
            self.ring_view_right.setVisible(False)

    def define_upgrade_tab(self) -> None:
        pass

    def global_timer_update(self) -> None:
        self.data.update(20)
        self.update_space_tab(self.data.unlock)

    def save(self):
        self.data.save()
        self.statusBar().showMessage("Save 完成.", 5000)

    def closeEvent(self, event: QCloseEvent) -> None:
        try:
            self.save()
        except:
            pass
        return super().closeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Application()
    window.show()
    app.exec()
