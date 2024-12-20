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
    QObject,
)
from PySide6.QtGui import QAction, QCloseEvent, QPaintEvent, QPalette
import random
from typing import Any, AnyStr, Literal, Self, Optional, Union, overload
from collections import defaultdict
from functools import partial
from math import ceil
import os
import json
import uuid

from numpy import isin


class RingNode(QObject):
    def __init__(
        self,
        father: Optional[RingNode] = None,
        level: int = 0,
        ms_pass: int = 0,
        space: int = 100,
        gem: int = 0,
        left: dict = {},
        right: dict = {},
    ) -> None:
        super().__init__(None)
        self.id = uuid.uuid4()
        self.father = father  # 父戒指，主空间的戒指没有父戒指
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

    def update(self, delta: int) -> None:
        if self.father:
            self.ms_pass += delta
            ms_require = self.ms_require
            if self.ms_pass >= ms_require:
                if self.depth == 1:  # 主空间戒指
                    self.gem = min(self.gem + self.ms_pass // ms_require, self.space)
                    self.ms_pass -= ms_require * self.ms_pass // ms_require
                elif self.depth > 1 and self.father.gem > 0:  # 非主空间戒指
                    self.gem = min(self.gem + 1, self.space)
                    self.father.gem -= 1
                    self.ms_pass -= ms_require
                else:  # 有父戒指，但父戒指没有宝石了，维持即将生产的状态
                    self.ms_pass = ms_require
        if self.left:
            self.left.update(delta)
        if self.right:
            self.right.update(delta)

    @property
    def depth(self) -> int:
        if self.father:
            return self.father.depth + 1
        else:
            return 0

    @property
    def ms_require(self) -> int:
        return ceil(3000 / (1 + 0.01 * self.level)) * (4 ** (self.depth - 1))

    def can_level_up(self) -> bool:
        if not self.father:
            return False
        return self.gem >= self.level + 1

    @Slot()
    def level_up(self) -> None:
        self.gem -= self.level + 1
        self.level += 1

    def can_expend_with(self, n: int) -> bool:
        if not self.father:
            return False
        return self.gem >= n

    @Slot(int)
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


class UnlockList:
    def __init__(self, **kwargs) -> None:
        self.can_new = kwargs.get("can_new", False)
        self.can_enter = kwargs.get("can_enter", False)

    def save(self) -> dict:
        return {
            "can_new": self.can_new,
            "can_enter": self.can_enter,
        }


class Data(QObject):
    def __init__(self) -> None:
        super().__init__(None)
        if os.path.exists("save.json"):
            with open("save.json", "r") as f:
                data = json.load(f)
                self.unlock = UnlockList(**data["unlocks"])
                self.root = RingNode(**data["rings"])
        else:
            self.unlock = UnlockList()
            self.root = RingNode(None)
            self.root.left = RingNode(self.root)
        self.current_visit = self.root

    def save(self) -> None:
        with open("save.json", "w") as f:
            json.dump(
                {
                    "unlocks": self.unlock.save(),
                    "rings": self.root.as_dict(),
                },
                f,
                indent=4,
                ensure_ascii=False,
            )

    def enter_node(self, node: RingNode) -> None:
        self.current_visit = node

    def update(self, delta: int) -> None:
        self.root.update(delta)


class CardView(QWidget):
    def __init__(self, parent, node: Optional[RingNode]) -> None:
        super().__init__(parent)

        self.node: Optional[RingNode] = node

        self.parent: Application = parent

        self.setVisible(bool(self.node))

        self.gridLayout = QGridLayout(self)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.back = QPushButton("Back", self)
        if self.node:
            self.back.setEnabled(bool(self.node.father) and self.node.father.depth > 0)
        self.back.clicked.connect(self.back_btn)
        self.gridLayout.addWidget(self.back, 0, 0, 1, 1)

        self.name = QLabel("Ring", self)
        self.name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.gridLayout.addWidget(self.name, 0, 1, 1, 1)

        self.enter = QPushButton("Enter", self)
        if self.node:
            self.enter.setEnabled(bool(self.node.left or self.node.right))
        self.enter.clicked.connect(self.enter_btn)
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
        self.gridLayout.addWidget(self.new_ring, 4, 1, 1, 1)

        self.space_upgrade = QPushButton("升级", self)
        self.space_upgrade.pressed.connect(self.space_up)
        self.gridLayout.addWidget(self.space_upgrade, 3, 2, 1, 1)

        self.level_upgrade = QPushButton("升级", self)
        self.level_upgrade.setToolTip("升级需要等级数加1的宝石")
        self.level_upgrade.pressed.connect(self.level_up)
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

        self.produce_time = QLabel("5.000 s", self)
        self.produce_time.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.gridLayout.addWidget(self.produce_time, 7, 2, 1, 1)

        self.space_verbose = QLabel("100/100", self)
        self.space_verbose.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.gridLayout.addWidget(self.space_verbose, 4, 2, 1, 1)

    def new_node(self, node: Optional[RingNode]) -> None:
        self.node = node
        self.setVisible(bool(self.node))
        if self.node:
            self.back.setEnabled(bool(self.node.father) and self.node.father.depth > 0)
            self.enter.setEnabled(bool(self.node.left or self.node.right))

    def back_btn(self) -> None:
        if self.node and self.node.father and self.node.father.depth > 0:
            self.parent.enter_new_node(self.node.father.father)

    def enter_btn(self) -> None:
        self.parent.enter_new_node(self.node)

    def level_up(self) -> None:
        if self.node:
            self.node.level_up()

    def space_up(self) -> None:
        if self.node:
            self.node.expend(self.space_upgrade_spin.value())

    def update(self) -> None:
        if self.node:
            self.produce_time.setText(f"{self.node.ms_require/1000:.4f} s")
            if self.node.ms_require <= 1000:
                self.produceBar.setRange(0, 1)
                self.produceBar.setValue(1)
                self.produceBar.setFormat(f"{1000 / self.node.ms_require:.2f} /s")
            else:
                self.produceBar.setRange(0, self.node.ms_require)
                self.produceBar.setValue(self.node.ms_pass)
            self.level_upgrade.setDisabled(not self.node.can_level_up())

            self.space_verbose.setText(f"{self.node.gem} / {self.node.space}")
            self.spaceBar.setRange(0, self.node.space)
            self.spaceBar.setValue(self.node.gem)
            self.space_upgrade.setDisabled(
                not self.node.can_expend_with(self.space_upgrade_spin.value())
            )

            self.level.setText(f"等级: {self.node.level}")


class Application(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Test")
        self.statusBar().clearMessage()

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

        self.ring_view_left = CardView(self, data.current_visit.left)
        self.ring_view_right = CardView(self, data.current_visit.right)

        self.space_tab_layout = QHBoxLayout(self.space_tab)
        self.space_tab_layout.addWidget(self.ring_view_left)
        self.space_tab_layout.addWidget(self.ring_view_right)

    @Slot(RingNode)
    def enter_new_node(self, node: RingNode):
        data.enter_node(node)
        self.ring_view_left.new_node(node.left)
        self.ring_view_right.new_node(node.right)

    def update_space_tab(self) -> None:
        self.ring_view_left.update()
        self.ring_view_right.update()

    def define_upgrade_tab(self) -> None:
        pass

    def global_timer_update(self) -> None:
        data.update(20)
        self.update_space_tab()

    def save(self):
        data.save()
        self.statusBar().showMessage("Save 完成.", 5000)

    # overload
    def closeEvent(self, event: QCloseEvent) -> None:
        try:
            self.save()
        except:
            pass
        return super().closeEvent(event)


data = Data()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Application()
    window.show()
    app.exec()
