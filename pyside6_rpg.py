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
    QLayoutItem,
    QTabBar,
    QStylePainter,
    QStyleOptionTab,
    QStyle,
)
from PySide6.QtCore import QSize, QTimer, Qt, Slot, Signal, QRect, QPoint
from PySide6.QtGui import QAction, QPaintEvent
from dataclasses import dataclass, asdict
import random
from typing import Literal, Self
from collections import defaultdict
from functools import partial
from math import ceil
import sqlite3 as sql

# qt version of l.py
# u play rouge leader, a hidden black magic beginner。
# unfinished


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


@dataclass(frozen=True)
class Equipment_status:
    max_hp: int = None
    min_atk: int = None
    max_atk: int = None
    crit: float = None
    crit_dmg: float = None
    pyh_defence: float = None
    mgc_defence: float = None
    dodge: float = None
    mgc_multi: float = None
    spell_will: float = None


@dataclass(frozen=True)
class Equipment:
    name: str
    part: Literal["Weapon", "offhand", "Head", "Body", "Hand", "Leg", "Foot", "Ring"]
    equipment_status: Equipment_status
    description: str = ""


@dataclass(frozen=True)
class Item:
    name: str
    description: str = ""


@dataclass(frozen=True)
class Gem:
    name: str
    description: str
    element: str
    power: int


Items = {
    "gold": Item("gold", "gold"),
    "arc shard": Item("arc shard", "充斥着奥数能量的小碎片"),
    "red shard": Item("red shard", "tier1 red gem"),
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


class EquipmentController:
    def __init__(self) -> None:
        self.container: dict[str, list[Equipment]] = {
            "Weapon": [],
            "Head": [],
            "Body": [],
            "Hand": [],
            "Leg": [],
            "Foot": [],
            "Ring": [],
        }
        self.equiped: dict[str, Equipment | None] = {
            "Weapon": None,
            "Head": None,
            "Body": None,
            "Hand": None,
            "Leg": None,
            "Foot": None,
            "Ring": None,
        }

    def overall_info(self):
        num = 0
        for l in self.container.values():
            num += len(l)

    def get_equipment(self, equipment: Equipment, equip: bool):
        part = equipment.part
        self.container[part].append(equipment)
        if equip:
            self.equiped[part] = equipment


class Character:
    def __init__(self, wisdom, strength, agility, name) -> None:
        self.wisdom: int = wisdom
        self.strength: int = strength
        self.agility: int = agility
        self.name: str = name
        self.spells: list[Spell] = []

    def __repr__(self) -> str:
        return self.name

    # hp, min_atk max_atk crit crit_dmg pyh_defence mgc_defence dodge mgc_multi spell_will
    def update_battle_info(self) -> None:
        self.max_hp = 20 + self.strength * 5
        self.min_atk = min(self.strength, self.agility)
        self.max_atk = max(self.strength, self.agility)
        self.crit = min(0.7, 0.05 + 0.0025 * self.agility + 0.001 * self.wisdom)
        self.crit_dmg = 1.5 + 0.0015 * self.strength + 0.001 * self.agility
        self.phy_defence = max(0.7, 1 - 0.005 * self.strength)
        self.mgc_defence = max(0.7, 1 - 0.005 * self.wisdom)
        self.dodge = min(0.7, max(0, 0.002 * self.agility - 0.002 * self.strength))
        self.mgc_multi = 1 + 0.05 * self.wisdom
        self.spell_will = 0.2 + 0.08 * len(self.spells)  # chance to cast spell
        self.hp = self.max_hp

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
        self.items = ItemController()
        self.equipments = EquipmentController()

        self.equipments.get_equipment(
            Equipment("Omni-helmet", "Head", Equipment_status(**{"max_hp": 10000})),
            True,
        )
        self.tier: int = 0

    def update_battle_info(self) -> None:
        super().update_battle_info()
        for equipment in self.equipments.equiped.values():
            if equipment is None:
                continue
            attrs: Equipment_status = equipment.equipment_status
            attrs = asdict(
                attrs, dict_factory=lambda x: {k: v for (k, v) in x if v is not None}
            )
            for k, v in attrs.items():
                if hasattr(self, k):
                    setattr(self, k, getattr(self, k) + v)
        self.hp = self.max_hp

    @property
    def gold(self) -> int:
        return self.items[Items["gold"]]

    def get_reward(self, reward: dict[Item, int]) -> None:
        self.items.add(reward)


class Enemy(Character):
    def __init__(self, name, reward, code) -> None:
        wisdom: int = code**2 + random.randint(-code, code)
        strength: int = code**2 + random.randint(-code, code)
        agility: int = code**2 + random.randint(-code, code)
        super().__init__(wisdom, strength, agility, name)
        self.reward = reward

    def drop_reward(self) -> dict[Item, int]:
        return self.reward


class Event:
    def __init__(self, description: str, options: dict[str, dict]) -> None:
        self.description: str = description
        self.options: dict[str, dict] = options
        self.true_options: list[str] = list(options.keys())


# TODO event和enemy应该同时竞争，event招enemy时建议改成存enemy里，用名字招。
# 或者将enemy视为一个选项的特殊event，如果event只有一个选项就自动选择。
# 也许battlecontroller可以放在mapcontroller里。

con = sql.connect("wcf.db")
cur = con.cursor()
# 表：map,[mapid, name, layer, base_enemy_tier]
cur.execute(
    """CREATE TABLE map(
        name TEXT NOT NULL,
        layer TEXT NOT NULL,
        baseEnemyTier INTEGER NOT NULL,
        PRIMARY KEY(name, layer)
    )"""
)
cur.execute("""INSERT INTO map VALUES ('Jail', '-2', 3)""")
cur.execute("""INSERT INTO map VALUES ('Jail', '-3', 6)""")
con.commit()
# 表：map_connect, [mapid_src, mapid_dst]
cur.execute(
    """CREATE TABLE map_connect(
        map_src INTEGER NOT NULL,
        map_dst INTEGER NOT NULL
    )"""
)
cur.execute("""INSERT INTO map_connect VALUES (1, 2)""")
con.commit()
# 表：enemys,[name, spawn_p]
# cur.execute(
#     """CREATE TABLE enemy(

#     )"""
# )
# 表：items,[itemid, description]
cur.execute(
    """CREATE TABLE item(
        name TEXT NOT NULL,
        description TEXT NOT NULL
    )"""
)
cur.execute("""INSERT INTO item VALUES ('gold', 'currency')""")
cur.execute("""INSERT INTO item VALUES ('white_shard', 'arc energy shard')""")
con.commit()


# 表：equipments,[equpimentid, description, part, 各属性有值就填值，没有就null]
# 表：enemy_drop,[enemyid, type, dropid] # 每个drop一行
# 表：enemy-map, [mapid, enemyid]
# 表：events, [p, require_event, description]
cur.execute(
    """CREATE TABLE event(
        description TEXT NOT NULL,
        spawn_rate REAL NOT NULL
    )"""
)
cur.execute(
    """INSERT INTO event VALUES ('有个囚犯背对着你，口中念念有词。\n*似乎仍然保留有一定神志。', 10)"""
)
con.commit()
# 表：events_options: [eventid, optionid, description, trigger(drop/enemy/none...)]
cur.execute(
    """CREATE TABLE event_option(
        event_id INTEGER NOT NULL,
        description TEXT NOT NULL,
        trigger TEXT,
        trigger_id INTEGER
    )"""
)
cur.execute("""INSERT INTO event_option VALUES (1, '上前看看', 'enemy', 1)""")
cur.execute("""INSERT INTO event_option VALUES (1, '无视', null, null)""")
cur.execute("""INSERT INTO event_option VALUES (1, '背后偷袭', 'item', 1)""")
con.commit()


class MapController:
    def __init__(self) -> None:
        # with open("./temp2.json") as j:
        #     self.map_data = json.loads(j.read())
        self.map_data = {
            ("jail", "地下1层"): {
                "connect": [("jail", "地下2层")],
                "enemy_base_tier": 3,
                "enemys": [
                    {
                        "name": "unnamed",
                        "spawn_priority": 80,
                        "drops": {
                            "items": [{"name": "gold", "val": 4, "p": 1.0}],
                            "equipments": [
                                {
                                    "name": "Broken Cloth",
                                    "part": "Body",
                                    "equipment_status": {"max_hp": 5},
                                    "description": "a piece of cloth",
                                    "p": 0.05,
                                }
                            ],
                        },
                    },
                    {
                        "name": "strange prisoner",
                        "spawn_priority": 0,
                        "drops": {
                            "items": [
                                {"name": "gold", "val": 22, "p": 1.0},
                                {"name": "arc shard", "val": 1, "p": 1.0},
                            ],
                        },
                    },
                ],
                "events": [
                    {
                        "id": 1,
                        "info": {
                            "description": "有个囚犯背对着你，口中念念有词。\n*似乎仍然保留有一定神志。",
                            "options": {
                                "上前看看": {
                                    "enemy": {
                                        "name": "strange prisoner",
                                        "spawn_priority": 0,
                                        "drops": {
                                            "items": [
                                                {
                                                    "name": "gold",
                                                    "val": 22,
                                                    "p": 1.0,
                                                },
                                                {
                                                    "name": "arc shard",
                                                    "val": 1,
                                                    "p": 1.0,
                                                },
                                            ],
                                        },
                                    }
                                },
                                "无视": {},
                                "发起攻击": {
                                    "items": [
                                        {"name": "gold", "val": 10, "p": 1.0},
                                    ]
                                },
                            },
                        },
                        "p": 10,
                        "encounter": 0,
                    }
                ],
            }
        }
        self.current_map = ("jail", "地下1层")

    def spawn_event(self, on_explore_end: bool = False):
        # TODO
        if on_explore_end:
            possible_path = self.map_data[self.current_map]["connect"]
        else:
            events = self.map_data[self.current_map]["events"]
            weights = [i["p"] for i in events]
            event = random.choices(events, weights, k=1)[0]
            return Event(**event["info"])

    def spawn_enemy(self):
        level = self.map_data[self.current_map]
        e_pow: int = level["enemy_base_tier"]
        pool = level["enemys"]
        e = random.choices(pool, [e["spawn_priority"] for e in pool], k=1)[0]
        return self.enemy_makeup(e, e_pow)

    @classmethod
    def enemy_makeup(cls, e: dict, e_pow: int):
        reward = {}
        drops = e["drops"]
        if "items" in drops:
            for i in drops["items"]:
                p = i["p"]
                if random.random() < p:
                    name, val = i["name"], i["val"]
                    item = Items[name]
                    reward[item] = val
        if "equipments" in drops:
            for i in drops["equipments"]:
                p = i["p"]
                if random.random() < p:
                    name, part, equipment_status, description = (
                        i["name"],
                        i["part"],
                        i["equipment_status"],
                        i["description"],
                    )
                    equipment = Equipment(
                        name, part, Equipment_status(**equipment_status), description
                    )
                    reward[equipment] = 1
        return Enemy(e["name"], reward, e_pow)


class BattleController:
    def __init__(self, player: Player, opponent: Enemy) -> None:
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


class MyTabBar(QTabBar):
    def paintEvent(self, event):
        painter = QStylePainter(self)
        option = QStyleOptionTab()
        for index in range(self.count()):
            self.initStyleOption(option, index)
            painter.drawControl(QStyle.CE_TabBarTabShape, option)
            painter.drawText(
                self.tabRect(index),
                Qt.AlignCenter | Qt.TextDontClip,
                self.tabText(index),
            )

    def tabSizeHint(self, index):
        size = QTabBar.tabSizeHint(self, index)
        if size.width() < size.height():
            size.transpose()
        return size


class EquipmentFloatingWindow(QWidget):
    def __init__(self, parent: QWidget | None = ..., f: Qt.WindowType = ...) -> None:
        super().__init__(parent, f)


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

        info_group_layout = QHBoxLayout(info_group)
        info_group_layout.addWidget(self.info_gold_label)
        info_group_layout.addWidget(self.info_gold)
        info_group_layout.addWidget(self.info_tier_label)
        info_group_layout.addWidget(self.info_tier)

        # 创建标签页控件
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabBar(MyTabBar())
        self.tab_widget.setTabPosition(QTabWidget.TabPosition.West)

        # map tab
        self.explore_tab = QWidget()
        self.draw_explore_tab()
        self.tab_widget.addTab(self.explore_tab, "探索")

        # item tab
        self.item_tab = QWidget()
        self.define_item_tab()
        self.tab_widget.addTab(self.item_tab, "物品")

        # TODO equipment tab
        # 多级菜单
        self.equipment_tab = QWidget()
        self.define_equipment_tab()
        self.tab_widget.addTab(self.equipment_tab, "装备")

        # TODO skill tab
        self.skill_tab = QWidget()
        self.define_skill_tab()
        self.tab_widget.addTab(self.skill_tab, "技能")

        # TODO ritual tab
        self.ritual_tab = QWidget()
        self.define_ritual_tab()
        self.tab_widget.addTab(self.ritual_tab, "仪式")

        # TODO voodoo tab
        self.voodoo_tab = QWidget()
        self.define_voodoo_tab()
        self.tab_widget.addTab(self.voodoo_tab, "巫术")

        # 设置主布局
        self.global_widget = QWidget()
        global_layout = QVBoxLayout(self.global_widget)
        global_layout.addWidget(info_group)
        global_layout.addWidget(self.tab_widget)

        self.setCentralWidget(self.global_widget)

        # 创建并启动一个定时器
        self.golbal_timer_speed = 20  # ms
        self.global_timer = QTimer(self)
        self.global_timer.timeout.connect(self.global_timer_update)
        self.global_timer.start(self.golbal_timer_speed)  # 每20毫秒更新一次

        self.event_auto_speed = 5000

    def save(self):
        print(123)

    def save_close(self):
        try:
            self.save()
        except:
            RuntimeError("Save failed.")
        self.close()

    def clear_layout(self, layout):
        item_list = list(range(layout.count()))
        item_list.reverse()  # 倒序删除，避免影响布局顺序

        for i in item_list:
            item: QLayoutItem = layout.itemAt(i)
            item.widget().deleteLater()
            layout.removeItem(item)

    def draw_explore_tab(self):
        self.map_controller = MapController()
        # 事件/战斗界面
        self.center = QWidget()
        self.center.setAutoFillBackground(True)

        self.center_layout = QStackedLayout(self.center)

        # 占位符
        self.place_holder = QLabel("探索中~")
        self.place_holder.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # battle scene
        self.battle_scene = QWidget()
        self.battle_scene_layout = QGridLayout(self.battle_scene)
        self.define_battle_scene()
        self.battle_timer = QTimer()
        self.battle_timer.timeout.connect(self.battle)

        # TODO event scene
        self.event_scene = QWidget()
        self.event_scene_layout = QVBoxLayout(self.event_scene)
        self.define_event_scene()
        self.event_timer = QTimer()
        self.event_timer.timeout.connect(self.force_end_event)

        self.center_layout.addWidget(self.place_holder)
        self.center_layout.addWidget(self.battle_scene)
        self.center_layout.addWidget(self.event_scene)
        self.center_layout.setCurrentIndex(0)

        # 探索进度条
        self.explore_progress_bar = QProgressBar()
        self.explore_progress_bar.setRange(1, self.progress_bar_max_volumn)
        self.explore_progress_bar.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.explore_rate = 10

        self.explore_description = QLabel()
        self.explore_description.setText("<p></p>")

        self.explore_tab_layout = QVBoxLayout(self.explore_tab)
        self.explore_tab_layout.addWidget(self.center)
        self.explore_tab_layout.addWidget(self.explore_description)
        self.explore_tab_layout.addWidget(self.explore_progress_bar)
        self.explore_tab_layout.setContentsMargins(1, 1, 1, 1)

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
        # self.battle_record = QTextEdit()
        # self.battle_record.resize(100, 100)
        # self.battle_record_cursor = self.battle_record.textCursor()
        # self.battle_scene_layout.addWidget(self.battle_record, 3, 0, 3, 6)

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
        self.event_description = QLabel(" ")
        self.event_description.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.event_options = QWidget()
        self.event_options_layout = QHBoxLayout(self.event_options)

        self.event_auto_select_check = QCheckBox("自动选择上一次的选择？")

        self.event_scene_layout.addWidget(self.event_description)
        self.event_scene_layout.addWidget(self.event_options)
        self.event_scene_layout.addWidget(self.event_auto_select_check)
        check: QLayoutItem = self.event_scene_layout.itemAt(2)
        check.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def update_event_scene(self):
        self.clear_layout(self.event_options_layout)
        self.event_description.setText(self.current_event.description)
        for i in self.current_event.options:
            btn = QPushButton(i)
            btn.clicked.connect(partial(self.deal_event, i))
            self.event_options_layout.addWidget(btn)

    def define_equipment_tab(self):
        self.equipment_controller = EquipmentController()

        self.equipment_tab_main = QWidget()
        self.equipment_tab_main_layout = QGridLayout(self.equipment_tab_main)
        for r in range(2):
            for c in range(5):
                btn = QPushButton("1")
                btn.setMaximumSize(20, 20)
                self.equipment_tab_main_layout.addWidget(btn, r, c)

        self.equipment_tab_main2 = QWidget()
        self.equipment_tab_main_layout2 = QGridLayout(self.equipment_tab_main2)
        for r in range(2):
            for c in range(5):
                btn = QPushButton("1")
                btn.setMaximumSize(20, 20)
                self.equipment_tab_main_layout2.addWidget(btn, r, c)

        self.equipment_tab_layout = QVBoxLayout(self.equipment_tab)
        self.equipment_tab_layout.addWidget(self.equipment_tab_main)
        self.equipment_tab_layout.addWidget(self.equipment_tab_main2)

    def define_skill_tab(self):
        pass

    def define_ritual_tab(self):
        pass

    def define_voodoo_tab(self):
        self.voodoo_tab_layout = QHBoxLayout(self.voodoo_tab)

        l = QLabel("123")
        self.voodoo_tab_layout.addWidget(l)

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
        self.item_table.horizontalHeader().resizeSection(1, 60)

        self.item_tab_layout = QHBoxLayout(self.item_tab)
        self.item_tab_layout.addWidget(self.item_table)
        self.item_tab_layout.setContentsMargins(1, 1, 1, 1)

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
        # 更新资源
        self.info_gold.setText(str(self.player.gold))
        self.info_tier.setText(str(self.player.tier))

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
                if random.randint(0, 10000) < 200:
                    self.start_event()
        else:
            self.explore_progress_bar.setValue(self.explore_rate)
            self.update_status("Explore done.")

    @Slot()
    def update_status(self, massage: str, delay: int = 1500):
        self.statusBar().showMessage(massage, delay)

    def start_battle(self, enemy: Enemy = None):
        if enemy is None:
            self.bc = BattleController(self.player, self.map_controller.spawn_enemy())
        else:
            self.bc = BattleController(self.player, enemy)
        self.update_battle_scene()
        self.on_battle = True
        self.center_layout.setCurrentIndex(1)
        self.battle_timer.start(500)

    @Slot()
    def battle(self):
        self.bc.fight()
        self.update_battle_scene()
        flag, loser = self.bc.battle_end
        if flag:
            if self.player in loser:
                self.explore_progress_bar.reset()
            else:
                reward = self.bc.reward()
                self.player.get_reward(reward)
                string = "获得："
                for k, v in reward.items():
                    string += f"{k.name}*{v}; "
                self.update_status(string)
            self.end_battle()

    def end_battle(self):
        self.on_battle = False
        self.battle_timer.stop()
        self.center_layout.setCurrentIndex(0)
        self.update_item_table()

    def start_event(self):
        self.current_event = self.map_controller.spawn_event()
        self.update_event_scene()
        self.on_event = True
        self.center_layout.setCurrentIndex(2)
        self.event_timer.start(self.event_auto_speed)
        self.event_timer.remainingTime()

    def deal_event(self, option: str):
        # 处理手动操作
        callback = self.current_event.options[option]
        self.force_end_event()
        for k, v in callback.items():
            if k == "enemy":
                self.start_battle(self.map_controller.enemy_makeup(v, 1))
            if k == "items":
                reward = {}
                for i in v:
                    p = i["p"]
                    if random.random() < p:
                        name, val = i["name"], i["val"]
                        item = Items[name]
                        reward[item] = val
                self.player.get_reward(reward)
                string = "获得："
                for k, v in reward.items():
                    string += f"{k.name}*{v}; "
                self.update_status(string)
                self.update_item_table()

    def force_end_event(self):
        # 处理默认操作
        self.on_event = False
        self.event_timer.stop()
        self.center_layout.setCurrentIndex(0)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("WindowsVista")
    widget = MyWidget()
    widget.show()
    sys.exit(app.exec())
