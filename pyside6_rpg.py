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
    QGraphicsDropShadowEffect,
)
from PySide6.QtCore import QTimer, Qt, Slot
from PySide6.QtGui import QIntValidator, QColor
from dataclasses import dataclass, field
import random
from typing import Literal, overload
from abc import abstractmethod

# qt version of l.py
# u play rouge leader, a hidden black magic beginner。
# unfinished


class Spell:
    def __init__(
        self,
        level: int,
        damage_type: Literal["magic", "pure"],
        priority: int,
        base_damage: int,
        damge_by_level: float,
    ) -> None:
        self.level: int = level
        self.damage_type: Literal["magic", "pure"] = damage_type
        self.priority: int = priority
        self.base_damage: int = base_damage
        self.damge_by_level: float = damge_by_level

    @property
    def damage(self):
        damage = self.base_damage + (self.damge_by_level * (self.level - 1))
        return damage


@dataclass
class BattleInfo:
    damage_type: Literal["physic", "magic", "pure"]
    damage_val: float


class Character:
    def __init__(self, wisdom, strength, agility, name) -> None:
        self.wisdom: int = wisdom + 1000
        self.strength: int = strength + 1000
        self.agility: int = agility + 1000
        self.name: str = name
        self.update_battle_info()

    def update_battle_info(self) -> None:
        self.hp = self.max_hp = 20 + self.strength * 3
        self.min_atk = 1 + min(self.strength, self.agility)
        self.max_atk = 1 + max(self.strength, self.agility)
        self.crit = 0.05 + 0.005 * self.agility + 0.002 * self.wisdom
        self.crit_dmg = 1.5 + 0.003 * self.strength + 0.002 * self.agility
        self.phy_defence = max(0.7, 1 - 0.005 * self.strength)
        self.mgc_defence = max(0.7, 1 - 0.005 * self.wisdom)
        self.dodge = min(0.7, 0.002 * self.agility)
        self.mgc_multi = 1 + 0.05 * self.wisdom
        self.spell_will = 0.4 + 0.05 * len(self.spells)  # chance to cast spell

    @abstractmethod
    def make_action(self) -> BattleInfo: ...

    @property
    def power(self):
        return self.agility + self.wisdom + self.strength

    def __bool__(self):
        return self.hp > 0

    def on_attack(self, battle_info: BattleInfo):
        if not random.random() < self.dodge:
            style = battle_info.damage_type
            if style == "magic":
                self.hp -= battle_info.damage_val * self.mgc_defence
            elif style == "physic":
                self.hp -= battle_info.damage_val * self.phy_defence
            elif style == "pure":
                self.hp -= battle_info.damage_val


class Player(Character):
    def __init__(self) -> None:
        self.spells: list[Spell] = []
        self.gold: int = 10
        self.tier: int = 0
        super().__init__(10, 10, 10, "Player")

    def make_action(self) -> BattleInfo:
        if random.random() < self.spell_will and self.spells != []:
            spell: Spell = random.choices(
                self.spells, [s.priority for s in self.spells]
            )[0]
            if not isinstance(spell, Spell):
                raise TypeError()
            return BattleInfo(spell.damage_type, spell.damage * self.mgc_multi)
        else:
            base_atk = random.randint(self.min_atk, self.max_atk)
            if random.random() < self.crit:
                return BattleInfo("physic", base_atk * self.crit_dmg)
            else:
                return BattleInfo("physic", base_atk)


class Enemy(Character):
    # def __init__(self, code: int) -> None:
    def __init__(self, code, name="Test") -> None:
        wisdom: int = 7 + random.randint(code - 3, code + 3)
        strength: int = 7 + random.randint(code - 3, code + 3)
        agility: int = 7 + random.randint(code - 3, code + 3)
        self.spells: list[Spell] = []
        super().__init__(wisdom, strength, agility, name)
        self.max_hp *= 10
        self.hp *= 10

    def make_action(self):
        base_atk = random.randint(self.min_atk, self.max_atk)
        if random.random() < self.crit:
            return BattleInfo("physic", base_atk * self.crit_dmg)
        else:
            return BattleInfo("physic", base_atk)


class BattleController:
    def __init__(self, player, opponent) -> None:
        self.player: Player = player
        self.player.update_battle_info()
        self.opponent: Enemy = opponent
        self.opponent.update_battle_info()
        self.player_turn: bool = True

    @property
    def battle_end(self) -> list[bool, list[Character]]:
        flag: bool = False
        chars: list[Character] = []
        if not self.player:
            flag = True
            chars.append(self.player)
        if not self.opponent:
            flag = True
            chars.append(self.opponent)
        return flag, chars

    def fight(self):
        if self.player_turn:
            bf = self.player.make_action()
            print("Player to opponent", bf)
            self.opponent.on_attack(bf)
        else:
            bf = self.opponent.make_action()
            print("Opponent to player", bf)
            self.player.on_attack(bf)
        self.player_turn = not self.player_turn


class MyWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test")
        self.statusBar().clearMessage()

        self.player = Player()
        self.battle_group = []

        self.progress_bar_max_volumn = 10000
        self.on_event = False
        self.on_battle = False

        # 全局信息
        info_group = QGroupBox(f"{self.player.name}-Info")
        self.info_gold_label = QLabel("Gold:")
        self.info_gold = QLabel(str(self.player.gold))
        self.info_tier_label = QLabel("Tier:")
        self.info_tier = QLabel(str(self.player.tier))

        info_group_layout = QGridLayout(info_group)
        info_group_layout.addWidget(self.info_gold_label, 0, 0)
        info_group_layout.addWidget(self.info_gold, 0, 1)
        info_group_layout.addWidget(self.info_tier_label, 0, 2)
        info_group_layout.addWidget(self.info_tier, 0, 3)

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
        # 事件/战斗界面
        self.center = QWidget()
        self.center.setAutoFillBackground(True)

        self.center_layout = QStackedLayout(self.center)

        self.battle_scene = QWidget()
        self.battle_scene_layout = QGridLayout(self.battle_scene)
        self.define_battle_scene()
        self.battle_timer = QTimer()
        self.battle_timer.timeout.connect(self.battle)

        self.center_layout.addWidget(self.battle_scene)
        self.battle_scene.setVisible(False)

        # 探索进度条
        self.explore_progress_bar = QProgressBar()
        self.explore_progress_bar.setRange(1, self.progress_bar_max_volumn)
        self.explore_progress_bar.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.explore_rate = 10

        self.layout4 = QVBoxLayout(self.map_tab)
        self.layout4.addWidget(self.center)
        self.layout4.addWidget(self.explore_progress_bar)

    def define_battle_scene(self):
        attribute_effect = QGraphicsDropShadowEffect()
        attribute_effect.setColor(QColor(128, 128, 128))
        attribute_effect.setBlurRadius(2)
        attribute_effect.setOffset(10)
        self.name_1 = QLabel()
        self.battle_scene_layout.addWidget(self.name_1, 0, 0, 1, 3)
        self.hp_bar1 = QProgressBar(self.battle_scene)
        self.hp_bar1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hp_bar1.setRange(0, 10000)
        self.hp_bar1.setValue(10000)
        self.battle_scene_layout.addWidget(self.hp_bar1, 1, 0, 1, 3)
        self.name_2 = QLabel()
        self.battle_scene_layout.addWidget(
            self.name_2, 0, 3, 1, 3, alignment=Qt.AlignmentFlag.AlignRight
        )
        self.hp_bar2 = QProgressBar(self.battle_scene)
        self.hp_bar2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hp_bar2.setRange(0, 10000)
        self.hp_bar2.setValue(10000)
        self.hp_bar2.setInvertedAppearance(True)
        self.battle_scene_layout.addWidget(self.hp_bar2, 1, 3, 1, 3)
        self.strength1 = QLabel()
        self.strength1.setStyleSheet("QLabel { color: red;}")
        self.strength1.setGraphicsEffect(attribute_effect)
        self.battle_scene_layout.addWidget(self.strength1, 2, 0)
        self.agility1 = QLabel()
        self.agility1.setStyleSheet("QLabel { color: green;}")
        self.battle_scene_layout.addWidget(self.agility1, 2, 1)
        self.wisdom1 = QLabel()
        self.wisdom1.setStyleSheet("QLabel { color: blue;}")
        self.battle_scene_layout.addWidget(self.wisdom1, 2, 2)
        self.strength2 = QLabel()
        self.strength2.setStyleSheet("QLabel { color: red;}")
        self.battle_scene_layout.addWidget(
            self.strength2, 2, 3, alignment=Qt.AlignmentFlag.AlignRight
        )
        self.agility2 = QLabel()
        self.agility2.setStyleSheet("QLabel { color: green;}")
        self.battle_scene_layout.addWidget(
            self.agility2, 2, 4, alignment=Qt.AlignmentFlag.AlignRight
        )
        self.wisdom2 = QLabel()
        self.wisdom2.setStyleSheet("QLabel { color: blue;}")
        self.battle_scene_layout.addWidget(
            self.wisdom2, 2, 5, alignment=Qt.AlignmentFlag.AlignRight
        )

    def draw_battle_scene(self):
        self.name_1.setText(self.bc.player.name)
        self.hp_bar1.setValue(10000 * self.bc.player.hp / self.bc.player.max_hp)
        self.hp_bar1.setFormat(f"{round(self.bc.player.hp)} / {self.bc.player.max_hp}")
        self.name_2.setText(self.bc.opponent.name)
        self.hp_bar2.setValue(10000 * self.bc.opponent.hp / self.bc.opponent.max_hp)
        self.strength1.setText(str(self.bc.player.strength))
        self.agility1.setText(str(self.bc.player.agility))
        self.wisdom1.setText(str(self.bc.player.wisdom))
        self.strength2.setText(str(self.bc.opponent.strength))
        self.agility2.setText(str(self.bc.opponent.agility))
        self.wisdom2.setText(str(self.bc.opponent.wisdom))

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
        # 更新资源
        self.info_gold.setText(str(self.player.gold))

    @Slot()
    def update_status(self, massage: str, delay: int = 1500):
        self.statusBar().showMessage(massage, delay)

    def start_battle(self):
        print("Battle start")
        self.bc = BattleController(self.player, Enemy(self.player.tier + 3))
        self.draw_battle_scene()
        self.on_battle = True
        self.battle_scene.setVisible(True)
        self.battle_timer.start(500)

    @Slot()
    def battle(self):
        self.bc.fight()
        self.draw_battle_scene()
        flag, loser = self.bc.battle_end
        if flag:
            if self.player in loser:
                self.explore_progress_bar.reset()
            self.end_battle()

    def end_battle(self):
        print("Battle end")
        self.on_battle = False
        self.battle_timer.stop()
        self.battle_scene.setVisible(False)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = MyWidget()
    widget.show()
    sys.exit(app.exec())
