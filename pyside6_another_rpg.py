from PySide6.QtWidgets import *
from PySide6.QtCore import QTimer, Qt, Signal
from PySide6.QtGui import QTextDocument, QPixmap, QPainter, QIcon
from itertools import product
import sys

from PySide6.QtWidgets import QWidget
from functools import partial
from collections import defaultdict, Counter
from copy import deepcopy
from typing import Callable, TypeAlias, Literal, Any
from abc import abstractmethod, abstractstaticmethod
import random

# 后端部分


class Dice:
    def __init__(self) -> None:
        self.pool: list[int] = [1, 2, 3, 4, 5, 6]
        self.last_roll: int = 0

    def roll(self) -> None:
        self.last_roll = random.choice(self.pool)


class DamageNode:
    def __init__(self, val) -> None:
        self.val: int = val


class OutGoingDamageNode(DamageNode):
    def __init__(self, val) -> None:
        super().__init__(val)


class InComeDamageNode(DamageNode):
    def __init__(self, val) -> None:
        super().__init__(val)


class HealNode:
    def __init__(self) -> None:
        super().__init__()


BattleNode: TypeAlias = Dice | DamageNode | HealNode


class Skill_info:
    def __init__(
        self,
        name: str,
        require: str,
        effect: str,
        call: Callable[[list[BattleNode]], list[BattleNode]],
    ) -> None:
        self.name: str = name
        self.require: str = require
        self.effect: str = effect
        self.call: Callable[[list[BattleNode]], list[BattleNode]] = call


class Character:
    def __init__(self, name: str, hp: int) -> None:
        self.name: str = name
        self.max_hp: int = hp
        self.hp: int = self.max_hp
        self.skills: list[Skill_info] = []


class Fighter(Character):
    def __init__(self) -> None:
        super().__init__("Fighter", 3)
        self.skill1_max: int = 2
        self.skill1_available: int = self.skill1_max
        self.skills.append(
            Skill_info("Basic attack    ", "single 6", "deal 1 dmg.", self.skill1)
        )

    def turn_end(self):
        self.skill1_available = self.skill1_max

    def skill1(self, inputs) -> list[BattleNode]:
        if self.skill1_available <= 0:
            return False, []
        if len(inputs) != 1:
            return False, []
        the_input = inputs[0]
        if not isinstance(the_input, Dice):
            return False, []
        if the_input.last_roll != 6:
            return False, []
        self.skill1_available -= 1
        return True, [OutGoingDamageNode(1)]


class Wizard(Character):
    def __init__(self) -> None:
        super().__init__("Wizard", 1)
        self.skills.append(
            Skill_info(
                "Fireball-Splash ", "4 of kind", "one dmg to every opponent", None
            )
        )
        self.skills.append(
            Skill_info("Fireball-Focus  ", "4 of kind", "4 dmg to one opponent", None)
        )
        self.skills.append(
            Skill_info(
                "Chain lighting  ", "5 of kind", "dmg = 6th dice, all opponent ", None
            )
        )
        self.skills.append(
            Skill_info("Demise          ", "6 of a kingd", "kill all opponent", None)
        )


class Rogue(Character):
    def __init__(self) -> None:
        super().__init__("Rogue", 3)
        self.skills.append(
            Skill_info(
                "Sneak attack    ", "single 1", "1 dmg to one opponent", self.skill1
            )
        )
        self.skills.append(
            Skill_info(
                "Crippling strike ",
                "full house",
                "dmg = 6th dice, one opponent",
                self.skill2,
            )
        )

    def skill1(self, inputs: list[BattleNode]):
        if len(inputs) != 1:
            return False, []
        the_input = inputs[0]
        if not isinstance(the_input, Dice):
            return False, []
        if the_input.last_roll != 1:
            return False, []
        return True, [OutGoingDamageNode(1)]

    def skill2(self, inputs: list[BattleNode]):
        if len(inputs) != 6:
            return False, []
        for i in range(6):
            if not isinstance(inputs[i], Dice):
                return False, []
        p = []
        v = [d.last_roll for d in inputs]
        for i in range(6):
            temp = v[:i] + v[i + 1 :]
            c = Counter(temp)
            if len(c) != 2:
                continue
            if list(c.values()) not in [[2, 3], [3, 2]]:
                continue
            p.append(v[i])
        if p:
            return True, [OutGoingDamageNode(max(p))]
        else:
            return False, []


class Cleric(Character):
    def __init__(self) -> None:
        super().__init__("Cleric", 6)
        self.skills.append(
            Skill_info("Minor Heal      ", "4 stright", "Heal two", None)
        )
        self.skills.append(
            Skill_info(
                "Heal            ",
                "5 stright",
                "Heal = 6th dice, to one ally, it 6th dice is 1 heal all ally",
                None,
            )
        )
        self.skills.append(
            Skill_info(
                "Miracle         ", "6 stright", "Full heal and revive all", None
            )
        )


class Enemy:
    def __init__(self, name: str, hp: int) -> None:
        self.name: str = name
        self.max_hp: int = hp
        self.hp: int = self.max_hp
        self.dice_num: int = self.hp
        self.dices: list[Dice] = [Dice() for _ in range(self.dice_num)]

    def update(self):
        self.dice_num = self.hp


# 中间层


def Singleton(cls):
    _instance = {}

    def _singleton(*args, **kargs):
        if cls not in _instance:
            _instance[cls] = cls(*args, **kargs)
        return _instance[cls]

    return _singleton


@Singleton
class GameController:
    def __init__(self) -> None:
        self.selected = []
        self.battle_container: list[BattleNode] = []

        self.cleric = Cleric()
        self.wizard = Wizard()
        self.rogue = Rogue()
        self.fighter = Fighter()

        self.reroll_available = self.reroll_max = 3

        self.just_updated = True

    def turn_start(self):
        self.battle_container.clear()
        self.battle_container.extend([Dice() for _ in range(6)])
        for node in self.battle_container:
            node.roll()
        self.just_updated = True

    def on_reroll(self):
        if self.reroll_available < 1:
            return
        if len(self.selected) <= 0:
            return
        for node in self.selected:
            if not isinstance(node, Dice):
                return
        for dice in self.selected:
            dice.roll()
        self.reroll_available -= 1
        self.selected.clear()
        self.just_updated = True

    def turn_end(self):
        for node in self.battle_container:
            if isinstance(node, DamageNode):
                return
        self.battle_container.clear()
        self.fighter.turn_end()
        self.reroll_available = self.reroll_max
        self.just_updated = True

    def update(self):
        self.just_updated = False

    def on_select(self, node: BattleNode):
        if node in self.selected:
            self.selected.remove(node)
        else:
            self.selected.append(node)
        self.just_updated = True

    def is_selected(self, node: BattleNode):
        return node in self.selected

    def action(self, skill: Skill_info):
        success, res = skill.call(self.selected)
        if success:
            for node in self.selected:
                self.battle_container.remove(node)
            self.selected.clear()
        self.battle_container.extend(res)
        self.just_updated = True


game = GameController()


# UI 部分


class NodeView(QWidget):
    def __init__(self, full) -> None:
        super().__init__()
        self.full = full
        self.layout = QGridLayout(self)
        for i in range(6):
            if i < self.full:
                label = QLabel("@")
            else:
                continue
            self.layout.addWidget(label, i % 3, i // 3)

    def update(self, current):
        while (child := self.layout.takeAt(0)) != None:
            child.widget().deleteLater()
        for i in range(6):
            if i < current:
                label = QLabel("@")
            elif i < self.full:
                label = QLabel("O")
            self.layout.addWidget(label, i % 3, i // 3)


class CharacterCard(QGroupBox):
    def __init__(self, character: Character, parent: QWidget) -> None:
        self.character: Character = character
        super().__init__(self.character.name, parent)
        self.layout = QHBoxLayout(self)
        # 左侧信息
        self.middle_widget = QWidget()
        self.middle_layout = QVBoxLayout(self.middle_widget)
        self.hp_bar = NodeView(self.character.max_hp)
        self.middle_layout.addWidget(self.hp_bar)
        self.layout.addWidget(self.middle_widget)
        # 右侧技能
        self.skill_layout = QVBoxLayout()
        self.skill_layout.setSpacing(0)
        for skill in self.character.skills:
            full_tooltip = f"Require: {skill.require}\nEffect: {skill.effect}"
            skill_row = QHBoxLayout()
            name = QLabel(skill.name)
            name.setToolTip(full_tooltip)
            skill_row.addWidget(name)
            btn = QPushButton("Active")
            btn.clicked.connect(partial(game.action, skill))
            skill_row.addWidget(btn)
            self.skill_layout.addLayout(skill_row)
        self.layout.addLayout(self.skill_layout)
        self.update()

    def update(self):
        self.hp_bar.update(1)


class EnemyCard(QGroupBox):
    def __init__(self, enemy: Enemy, parent: QWidget) -> None:
        self.enemy = enemy
        super().__init__(self.enemy.name, parent)

        self.layout = QHBoxLayout(self)
        # 左侧信息
        self.label = QLabel("Info")
        self.layout.addWidget(self.label)
        # 右侧lastroll
        self.last_roll = 1


class MyApplication(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test")

        # 主体组件
        self.global_widget = QWidget()

        # 顶部stage info
        self.stage_info = QGroupBox("Stage")
        self.stage_info_layout = QHBoxLayout(self.stage_info)
        self.stage_info_layout.addWidget(QLabel("stage"))

        # 中左self
        self.player = QWidget()
        self.player_layout = QVBoxLayout(self.player)
        self.player_layout.addWidget(CharacterCard(game.cleric, self))
        self.player_layout.addWidget(CharacterCard(game.wizard, self))
        self.player_layout.addWidget(CharacterCard(game.rogue, self))
        self.player_layout.addWidget(CharacterCard(game.fighter, self))

        # 中battle info
        self.battle_info = QWidget()
        self.battle_info_layout = QVBoxLayout(self.battle_info)
        self.battle_buttons = QGroupBox("Action")
        self.battle_buttons.setMaximumHeight(100)
        self.battle_buttons_layout = QVBoxLayout(self.battle_buttons)
        self.reroll = QPushButton("Reroll")
        self.reroll.clicked.connect(game.on_reroll)
        self.battle_buttons_layout.addWidget(self.reroll)
        self.end_turn = QPushButton("End")
        self.end_turn.clicked.connect(game.turn_end)
        self.battle_buttons_layout.addWidget(self.end_turn)
        self.battle_info_layout.addWidget(self.battle_buttons)

        self.battle_nodes = QGroupBox("Pool")
        self.battle_node_layout = QVBoxLayout(self.battle_nodes)
        self.battle_info_layout.addWidget(self.battle_nodes)

        # 中右enemy
        self.enemys = QWidget()
        self.enemys_layout = QVBoxLayout(self.enemys)
        self.enemys_layout.addWidget(EnemyCard(Enemy("111", 2), self))
        self.enemys_layout.addWidget(EnemyCard(Enemy("1211", 2), self))
        self.enemys_layout.addWidget(EnemyCard(Enemy("1211", 2), self))

        # 设置主布局
        self.global_layout = QGridLayout(self.global_widget)
        self.global_layout.addWidget(self.stage_info, 0, 0, 1, 3)
        self.global_layout.addWidget(self.player, 1, 0)
        self.global_layout.addWidget(self.battle_info, 1, 1)
        self.global_layout.addWidget(self.enemys, 1, 2)

        self.setCentralWidget(self.global_widget)

        # 创建并启动一个定时器
        self.global_timer = QTimer(self)
        self.global_timer.timeout.connect(self.global_update)
        self.global_timer.start(50)
        game.turn_start()

    def global_update(self):
        if game.just_updated:
            while (child := self.battle_node_layout.takeAt(0)) != None:
                child.widget().deleteLater()
            for node in game.battle_container:
                if isinstance(node, Dice):
                    btn = QPushButton(str(node.last_roll))
                elif isinstance(node, OutGoingDamageNode):
                    btn = QPushButton(f"{node.val} ->")
                elif isinstance(node, InComeDamageNode):
                    btn = QPushButton(f"<- {node.val}")
                elif isinstance(node, HealNode):
                    btn = QPushButton(f"Heal")

                if game.is_selected(node):
                    btn.setStyleSheet("QPushButton { color: red;}")
                btn.clicked.connect(partial(game.on_select, node))
                self.battle_node_layout.addWidget(btn)
        game.update()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = MyApplication()
    widget.show()
    sys.exit(app.exec())
