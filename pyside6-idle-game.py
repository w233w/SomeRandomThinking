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
    QLineEdit,
)
from PySide6.QtCore import QTimer, Qt, Slot
from PySide6.QtGui import QIntValidator
from dataclasses import dataclass, field
import random

# qt version of l.py
# u play rouge leader, a hidden black magic beginner。
# unfinished


class Character:
    def __init__(self, wisdom: int = 3, strength: int = 3, agility: int = 3) -> None:
        self.wisdom: int = wisdom
        self.strength: int = strength
        self.agility: int = agility
        self.update_battle_info()

    def update_battle_info(self, types: str = "normal") -> None:
        try:
            getattr(self, "max_hp")
        except:
            self.hp = self.max_hp = 20 + self.strength * 3
        self.min_atk = 1 + min(self.strength, self.agility)
        self.max_atk = 1 + max(self.strength, self.agility)
        self.atk_spd = 0.9**self.agility
        self.crit = 0.05 + 0.005 * self.agility + 0.002 * self.wisdom
        self.crit_dmg = 1.5 + 0.002 * self.strength + 0.003 * self.agility
        self.phy_defence = max(0.7, 1 - 0.005 * self.strength)
        self.mgc_defence = max(0.7, 1 - 0.03 * self.agility - 0.004 * self.wisdom)
        self.dodge = min(0.7, 0.002 * self.agility)
        self.mgc_multi = 1 + 0.05 * self.wisdom
        match types:
            case "strength":
                self.hp += self.strength
            case "wisdom":
                self.mgc_multi += 0.5
            case "agility":
                self.atk_spd = 0.88**self.agility
            case "normal":
                self.hp += 1
                self.min_atk += 1
                self.max_atk += 1
            case _:
                ValueError()

    @property
    def is_crit(self):
        return random.randint(0, 1000) < self.crit * 1000

    @property
    def is_dodge(self):
        return random.randint(0, 1000) < self.dodge * 1000

    def attack(self):
        base_atk = random.randint(self.min_atk, self.max_atk)
        if self.is_crit:
            return int(base_atk * self.crit_dmg)
        else:
            return int(base_atk)

    def spell(self, spell_info):
        return spell_info["dmg"] * self.battle_info["mgc_multi"]

    def on_attack(self):
        if not self.is_dodge:
            pass

    def on_spell(self):
        if not self.is_dodge:
            pass


@dataclass
class Values:
    name: str = "Player"
    gold: int = 10
    insight: int = 0
    sans: int = 100
    twist_rate: int = 0
    wisdom: int = 3
    strength: int = 3
    agility: int = 3


class MyWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test")
        self.statusBar().clearMessage()

        self.value = Values()

        self.progress_bar_max_volumn = 10000
        self.on_event = False
        self.on_battle = False

        # 全局信息
        info_group = QGroupBox(f"{self.value.name}-Info")
        self.info_gold_label = QLabel("Gold:")
        self.info_gold = QLabel(str(self.value.gold))
        self.info_insight_label = QLabel("Insight:")
        self.info_insight = QLabel(str(self.value.insight))
        self.info_sans_label = QLabel("Sans:")
        self.info_sans = QLabel(str(self.value.sans))

        info_group_layout = QGridLayout(info_group)
        info_group_layout.addWidget(self.info_gold_label, 0, 0)
        info_group_layout.addWidget(self.info_gold, 0, 1)
        info_group_layout.addWidget(self.info_insight_label, 0, 2)
        info_group_layout.addWidget(self.info_insight, 0, 3)
        info_group_layout.addWidget(self.info_sans_label, 0, 4)
        info_group_layout.addWidget(self.info_sans, 0, 5)

        # 创建标签页控件
        self.tab_widget = QTabWidget()

        # map tab
        self.map_tab = QWidget()
        self.draw_map_page()
        self.tab_widget.addTab(self.map_tab, "Map")

        # 设置主布局
        self.global_widget = QWidget()
        global_layout = QVBoxLayout(self.global_widget)
        global_layout.addWidget(info_group)
        global_layout.addWidget(self.tab_widget)

        self.setCentralWidget(self.global_widget)

        # 创建并启动一个定时器
        self.global_timer = QTimer(self)
        self.global_timer.timeout.connect(self.global_timer_update)
        self.global_timer.start(20)  # 每20毫秒更新一次

    def draw_map_page(self):
        # 地图切换
        map_selecter_group = QGroupBox("map-selecter")
        map_selecter_group.setMaximumWidth(250)
        self.map_btns = []
        for i in range(8):
            self.map_btns.append(QPushButton(f"map{i+1}"))
        map_selecter_layout = QGridLayout(map_selecter_group)
        for i in range(8):
            map_selecter_layout.addWidget(self.map_btns[i], i // 4, i % 4)
        # 事件/战斗界面
        self.center = QWidget()
        self.center.setMinimumHeight(120)
        self.center.setAutoFillBackground(True)

        self.center_layout = QStackedLayout(self.center)

        self.battle_scene = QWidget()
        self.battle_scene_layout = QGridLayout(self.battle_scene)
        self.draw_battle_scene()

        self.center_layout.addWidget(self.battle_scene)
        self.battle_scene.setVisible(False)

        # 探索进度条
        self.explore_progress_bar = QProgressBar()
        self.explore_progress_bar.setRange(0, self.progress_bar_max_volumn)
        self.explore_progress_bar.setTextVisible(False)
        self.explore_progress_bar.setValue(0)

        self.explore_rate = 10

        layout4 = QVBoxLayout(self.map_tab)
        layout4.addWidget(map_selecter_group)
        layout4.addWidget(self.center)
        layout4.addWidget(self.explore_progress_bar)

    def draw_battle_scene(self):
        self.hp_bar1 = QProgressBar(self.battle_scene)
        self.hp_bar1.setRange(0, 10000)
        self.hp_bar1.setValue(10000)
        self.hp_bar1.setTextVisible(False)
        self.battle_scene_layout.addWidget(self.hp_bar1, 0, 0, 1, 2)
        self.hp_bar2 = QProgressBar(self.battle_scene)
        self.hp_bar2.setRange(0, 10000)
        self.hp_bar2.setValue(10000)
        self.hp_bar2.setTextVisible(False)
        self.hp_bar2.setInvertedAppearance(True)
        self.battle_scene_layout.addWidget(self.hp_bar2, 0, 2, 1, 2)
        self.strength1 = QLabel()
        self.battle_scene_layout.addWidget(self.strength1, 1, 0)
        self.agility1 = QLabel()
        self.battle_scene_layout.addWidget(self.agility1, 2, 0)
        self.wisdom1 = QLabel()
        self.battle_scene_layout.addWidget(self.wisdom1, 3, 0)
        self.strength2 = QLabel()
        self.battle_scene_layout.addWidget(
            self.strength2, 1, 3, alignment=Qt.AlignmentFlag.AlignRight
        )
        self.agility2 = QLabel()
        self.battle_scene_layout.addWidget(
            self.agility2, 2, 3, alignment=Qt.AlignmentFlag.AlignRight
        )
        self.wisdom2 = QLabel()
        self.battle_scene_layout.addWidget(
            self.wisdom2, 3, 3, alignment=Qt.AlignmentFlag.AlignRight
        )

    @Slot()
    def global_timer_update(self):
        """全局更新内容"""
        # 更新探索进度条
        if self.explore_progress_bar.value() < self.progress_bar_max_volumn:
            if not self.on_battle and not self.on_event:
                new_val = min(
                    self.progress_bar_max_volumn,
                    self.explore_progress_bar.value() + self.explore_rate,
                )
                self.explore_progress_bar.setValue(new_val)
                if (
                    new_val / self.progress_bar_max_volumn > 0.05
                    and random.randint(0, 1000) < 20
                ):
                    self.start_battle()
        else:
            self.explore_progress_bar.setValue(self.explore_rate)
            self.update_status("Explore done.")

        self.info_gold.setText(str(self.value.gold))

    @Slot()
    def update_status(self, massage: str, delay: int = 1500):
        self.statusBar().showMessage(massage, delay)

    def start_battle(self):
        self.a = 0
        self.on_battle = True
        self.battle_scene.setVisible(True)
        self.global_timer.timeout.connect(self.battle)

    @Slot()
    def battle(self):
        self.a += 1
        if self.a > 50:
            self.end_battle()

    def end_battle(self):
        self.on_battle = False
        self.global_timer.timeout.disconnect(self.battle)
        self.battle_scene.setVisible(False)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = MyWidget()
    widget.show()
    sys.exit(app.exec())
