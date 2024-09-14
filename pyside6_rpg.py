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
    QTableView,
)
from PySide6.QtWidgets import *
from PySide6.QtCore import QTimer, Qt, Slot
from PySide6.QtGui import QIntValidator, QColor, QAction
from dataclasses import dataclass
import random
from typing import Literal, overload, Self, TypeAlias
import json
from collections import defaultdict
from math import ceil

# qt version of l.py
# u play rouge leader, a hidden black magic beginner。
# unfinished

CBattleStatus: TypeAlias = Literal[
    "hp",
    "min_atk",
    "max_atk",
    "crit",
    "crit_dmg",
    "pyh_defence",
    "mgc_defence",
    "dodge",
    "mgc_multi",
    "spell_will",
]


class Spell:
    def __init__(
        self,
        name: str,
        level: int,
        damage_type: Literal["magic", "pure"],
        priority: int,
        base_damage: int,
        damge_by_level: float,
    ) -> None:
        self.name: str = name
        self.level: int = level
        self.damage_type: Literal["magic", "pure"] = damage_type
        self.priority: int = priority
        self.base_damage: int = base_damage
        self.damge_by_level: float = damge_by_level

    @property
    def damage(self):
        damage = self.base_damage + (self.damge_by_level * (self.level - 1))
        return damage

    def as_json(self):
        return self.__dict__


@dataclass
class BattleInfo:
    damage_type: Literal["physic", "magic", "pure"]
    damage_val: float
    description: str
    source: "Character"
    dest: "Character"


class Equipment:
    def __init__(self, name, part, base_status, description: str = "") -> None:
        self.name: str = name
        self.part: Literal["Weapon", "Head", "Body", "Hand", "Leg", "Foot", "Ring"] = (
            part
        )
        self.base_status: dict[CBattleStatus, float] = base_status
        self.description: str = description

    @property
    def info(self):
        s = ""
        for k, v in self.base_status.items():
            s += f"{k}: {v}\n"
        s = s[:-1]
        return s

    def as_json(self):
        return self.__dict__


@dataclass(frozen=True)
class Item:
    name: str
    description: str


Items = {
    "gold": Item("gold", "gold"),
    "red shard": Item("red shard", "tier1 red gem"),
    "red shard2": Item("red shard2", "tier1 red gem"),
    "red shard3": Item("red shard3", "tier1 red gem"),
    "red shard4": Item("red shard4", "tier1 red gem"),
    "red shard5": Item("red shard5", "tier1 red gem"),
}


class ItemController:
    def __init__(self) -> None:
        self.container: dict[Item, int] = defaultdict(int)

    def __getitem__(self, key: Item):
        return self.container[key]

    def add(self, items: dict[Item, int]) -> None:
        for k, v in items.items():
            self.container[k] += v

    def __len__(self) -> int:
        return len(self.container)

    def __iter__(self):
        return iter(self.container.items())


class Character:
    def __init__(self, wisdom, strength, agility, name) -> None:
        self.wisdom: int = wisdom
        self.strength: int = strength
        self.agility: int = agility
        self.name: str = name
        self.spells: list[Spell] = []
        self.equipments: list[Equipment] = []

    def __repr__(self) -> str:
        return self.name

    # hp, min_atk max_atk crit crit_dmg pyh_defence mgc_defence dodge mgc_multi spell_will
    def update_battle_info(self) -> None:
        self.hp = self.max_hp = 20 + self.strength * 5
        self.min_atk = min(self.strength, self.agility)
        self.max_atk = max(self.strength, self.agility)
        self.crit = min(0.7, 0.05 + 0.0025 * self.agility + 0.001 * self.wisdom)
        self.crit_dmg = 1.5 + 0.0015 * self.strength + 0.001 * self.agility
        self.phy_defence = max(0.7, 1 - 0.005 * self.strength)
        self.mgc_defence = max(0.7, 1 - 0.005 * self.wisdom)
        self.dodge = min(0.7, max(0, 0.002 * self.agility - 0.002 * self.strength))
        self.mgc_multi = 1 + 0.05 * self.wisdom
        self.spell_will = 0.2 + 0.08 * len(self.spells)  # chance to cast spell
        for equipment in self.equipments:
            attrs = equipment.base_status
            for k, v in attrs.items():
                if hasattr(self, k):
                    if k == "hp":
                        self.hp += v
                        self.max_hp += v
                    else:
                        setattr(self, k, getattr(self, k) + v)

    def make_action(self, target: Self) -> BattleInfo:
        if random.random() < self.spell_will and self.spells != []:
            spell: Spell = random.choices(
                self.spells, [s.priority for s in self.spells]
            )[0]
            if not isinstance(spell, Spell):
                raise TypeError()
            return BattleInfo(
                spell.damage_type,
                spell.damage * self.mgc_multi,
                "cast <b>" + spell.name + "</b>",
                self,
                target,
            )
        else:
            if self.min_atk >= self.max_atk:
                base_atk = self.max_atk
            else:
                base_atk = random.randint(self.min_atk, self.max_atk)
            if random.random() < self.crit:
                return BattleInfo(
                    "physic", base_atk * self.crit_dmg, "<b>Crit hit</b>", self, target
                )
            else:
                return BattleInfo("physic", base_atk, "<b>Attack</b>", self, target)

    @property
    def power(self):
        return self.agility + self.wisdom + self.strength

    def __bool__(self):
        return self.hp > 0

    def on_attack(self, battle_info: BattleInfo):
        if not random.random() < self.dodge:
            match battle_info.damage_type:
                case "magic":
                    true_damage = battle_info.damage_val * self.mgc_defence
                    self.hp -= round(true_damage, 2)
                case "physic":
                    true_damage = battle_info.damage_val * self.phy_defence
                    self.hp -= round(true_damage, 2)
                case "pure":
                    self.hp -= round(battle_info.damage_val, 2)
        else:
            print("Dodge")


class Player(Character):
    def __init__(self) -> None:
        super().__init__(10, 10, 10, "Player")
        self.spells.append(Spell("Throw Fire", 1, "magic", 10, 15, 2))
        # self.equipments.append(Equipment("Omni-helmet", "head", {"hp": 10000}))
        # self.equipments.append(
        #     Equipment("King-Axe", "weapon", {"min_atk": 100, "max_atk": 1000})
        # )
        self.items = ItemController()
        self.tier: int = 0

    @property
    def gold(self) -> int:
        return self.items[Items["gold"]]

    def get_reward(self, reward: dict[Item, int]) -> None:
        self.items.add(reward)


class Enemy(Character):
    def __init__(self, code, name="Test") -> None:
        wisdom: int = code**2 + random.randint(-code, code)
        strength: int = code**2 + random.randint(-code, code)
        agility: int = code**2 + random.randint(-code, code)
        super().__init__(wisdom, strength, agility, name)
        self.gold = code**2

    def drop_reward(self) -> dict[Item, int]:
        return {
            Items["gold"]: self.gold,
            Items["red shard"]: 1,
            Items["red shard2"]: 1,
            Items["red shard3"]: 1,
            Items["red shard4"]: 1,
            Items["red shard5"]: 1,
        }


class BattleController:
    def __init__(self, player, opponent) -> None:
        self.player: Player = player
        self.player.update_battle_info()
        self.opponent: Enemy = opponent
        self.opponent.update_battle_info()
        self.player_turn: bool = True
        self.last_bf: BattleInfo = None

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
            self.last_bf = self.player.make_action(self.opponent)
            # print("Player to opponent", self.last_bf)
            self.opponent.on_attack(self.last_bf)
        else:
            self.last_bf = self.opponent.make_action(self.player)
            # print("Opponent to player", self.last_bf)
            self.player.on_attack(self.last_bf)
        self.player_turn = not self.player_turn

    def reward(self) -> dict[Item, int]:
        return self.opponent.drop_reward()


class MyWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test")
        self.statusBar().clearMessage()

        # set menu
        game_menu = QMenu("Game", self)
        save = QAction("save", game_menu)
        save.triggered.connect(self.save)
        game_menu.addAction(save)
        ext = QAction("Exit", game_menu)
        ext.triggered.connect(self.save_close)
        game_menu.addAction(ext)
        self.menuBar().addMenu(game_menu)

        # load key data
        self.player = Player()
        self.battle_group = []

        self.progress_bar_max_volumn = 10000
        self.on_event = False
        self.on_battle = False

        # 全局信息
        info_group = QGroupBox(f"{self.player.name} Info")
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
        self.explore_tab = QWidget()
        self.draw_explore_tab()
        self.tab_widget.addTab(self.explore_tab, "探索")

        # item tab
        self.item_tab = QWidget()
        self.define_item_tab()
        self.tab_widget.addTab(self.item_tab, "物品")

        # TODO equipment tab
        self.equipment_tab = QWidget()
        self.tab_widget.addTab(self.equipment_tab, "装备")

        # TODO skill tab
        self.skill_tab = QWidget()
        self.draw_skill_tab()
        self.tab_widget.addTab(self.skill_tab, "技能")

        # TODO ritual tab
        self.ritual_tab = QWidget()
        self.tab_widget.addTab(self.ritual_tab, "仪式")

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

    def save(self):
        print(123)

    def save_close(self):
        try:
            self.save()
        except:
            RuntimeError("Save failed.")
        self.close()

    def draw_explore_tab(self):
        # 事件/战斗界面
        self.center = QWidget()
        self.center.setAutoFillBackground(True)

        self.center_layout = QStackedLayout(self.center)

        self.battle_scene = QWidget()
        self.battle_scene_layout = QGridLayout(self.battle_scene)
        self.define_battle_scene()
        self.battle_timer = QTimer()
        self.battle_timer.timeout.connect(self.battle)

        # TODO event scene
        self.event_scene = QWidget()
        self.event_scene_layout = QVBoxLayout(self.event_scene)
        self.define_event_scene()
        self.event_timer

        # TODO explore scene

        self.center_layout.addWidget(self.battle_scene)
        self.center_layout.addWidget(self.event_scene)
        self.battle_scene.setVisible(False)
        self.event_scene.setVisible(False)

        # 探索进度条
        self.explore_progress_bar = QProgressBar()
        self.explore_progress_bar.setRange(1, self.progress_bar_max_volumn)
        self.explore_progress_bar.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.explore_rate = 10

        self.explore_description = QLabel()
        self.explore_description
        self.explore_description.setText("<p></p>")

        self.explore_tab_layout = QVBoxLayout(self.explore_tab)
        self.explore_tab_layout.addWidget(self.center)
        self.explore_tab_layout.addWidget(self.explore_description)
        self.explore_tab_layout.addWidget(self.explore_progress_bar)

    def define_battle_scene(self):
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
        self.strength1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.battle_scene_layout.addWidget(self.strength1, 2, 0)
        self.agility1 = QLabel()
        self.agility1.setStyleSheet("QLabel { color: green;}")
        self.agility1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.battle_scene_layout.addWidget(self.agility1, 2, 1)
        self.wisdom1 = QLabel()
        self.wisdom1.setStyleSheet("QLabel { color: blue;}")
        self.wisdom1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.battle_scene_layout.addWidget(self.wisdom1, 2, 2)
        self.strength2 = QLabel()
        self.strength2.setStyleSheet("QLabel { color: red;}")
        self.strength2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.battle_scene_layout.addWidget(self.strength2, 2, 3)
        self.agility2 = QLabel()
        self.agility2.setStyleSheet("QLabel { color: green;}")
        self.agility2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.battle_scene_layout.addWidget(self.agility2, 2, 4)
        self.wisdom2 = QLabel()
        self.wisdom2.setStyleSheet("QLabel { color: blue;}")
        self.wisdom2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.battle_scene_layout.addWidget(self.wisdom2, 2, 5)

    def update_battle_scene(self):
        self.name_1.setText(self.bc.player.name)
        self.hp_bar1.setValue(10000 * self.bc.player.hp / self.bc.player.max_hp)
        self.hp_bar1.setFormat(f"{ceil(self.bc.player.hp)} / {self.bc.player.max_hp}")
        self.name_2.setText(self.bc.opponent.name)
        self.hp_bar2.setValue(10000 * self.bc.opponent.hp / self.bc.opponent.max_hp)
        self.hp_bar2.setFormat(
            f"{ceil(self.bc.opponent.hp)} / {self.bc.opponent.max_hp}"
        )
        self.strength1.setText(str(self.bc.player.strength))
        self.agility1.setText(str(self.bc.player.agility))
        self.wisdom1.setText(str(self.bc.player.wisdom))
        self.strength2.setText(str(self.bc.opponent.strength))
        self.agility2.setText(str(self.bc.opponent.agility))
        self.wisdom2.setText(str(self.bc.opponent.wisdom))
        if self.bc.last_bf is not None:
            self.explore_description.setText(
                self.bc.last_bf.source.name
                + " "
                + self.bc.last_bf.description
                + " on "
                + self.bc.last_bf.dest.name
            )

    def define_event_scene(self):
        pass

    def draw_skill_tab(self):
        pass

    def define_item_tab(self):
        self.item_table = QTableWidget()
        self.item_table.setColumnCount(2)
        self.item_table.setHorizontalHeaderLabels(["Name", "Volumn"])
        self.item_table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.Stretch
        )
        self.item_table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Fixed
        )
        self.item_table.horizontalHeader().resizeSection(1, 50)

        self.item_tab_layout = QHBoxLayout(self.item_tab)
        self.item_tab_layout.addWidget(self.item_table)

        self.update_item_table()

    def update_item_table(self):
        self.item_table.setRowCount(len(self.player.items))
        for i, (item, vol) in enumerate(self.player.items):
            name = QTableWidgetItem(item.name)
            name.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            name.setToolTip(item.description)
            self.item_table.setItem(i, 0, name)
            volumn = QTableWidgetItem(str(vol))
            volumn.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.item_table.setItem(i, 1, volumn)

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
                if self.explore_description.text != "":
                    self.explore_description.setText("<p></p>")
                if random.randint(0, 10000) < 50:
                    self.start_battle()
        else:
            self.explore_progress_bar.setValue(self.explore_rate)
            self.update_status("Explore done.")
            self.player.tier += 1
        # 更新资源
        self.info_gold.setText(str(self.player.gold))
        self.info_tier.setText(str(self.player.tier))

    @Slot()
    def update_status(self, massage: str, delay: int = 1500):
        self.statusBar().showMessage(massage, delay)

    def start_battle(self):
        print("Battle start")
        if random.random() < 0.9:
            self.bc = BattleController(self.player, Enemy(self.player.tier + 3))
        else:
            self.bc = BattleController(self.player, Enemy(self.player.tier + 5, "BIG"))
        self.update_battle_scene()
        self.on_battle = True
        self.battle_scene.setVisible(True)
        self.battle_timer.start(500)

    @Slot()
    def battle(self):
        self.bc.fight()
        self.update_battle_scene()
        flag, loser = self.bc.battle_end
        if flag:
            if self.player in loser:
                self.explore_progress_bar.reset()
                self.player.tier -= 1
            else:
                reward = self.bc.reward()
                self.player.get_reward(reward)
                string = "获得："
                for k, v in reward.items():
                    string += f"{k.name}*{v}; "
                self.update_status(string)
            self.end_battle()

    def end_battle(self):
        print("Battle end")
        self.on_battle = False
        self.battle_timer.stop()
        self.battle_scene.setVisible(False)
        self.update_item_table()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("WindowsVista")
    widget = MyWidget()
    widget.show()
    sys.exit(app.exec())
