from __future__ import annotations
import random
from typing import TYPE_CHECKING
from wcwidth import wcswidth

if TYPE_CHECKING:
    from battle import Battle

class Enemy(object):

    def __init__(self, id: str = "Enemy", name: str = "敌人", max_dp: int = 100, max_hp: int = 100):
        self.id = id
        self.name = name
        self.max_dp = max_dp
        self.max_hp = max_hp
        self.dp = max_dp
        self.hp = max_hp
        self.is_break = False
        self.is_dead = False
        self.down_turn = 0
        self.break_turn = 0
        self.blast_count_dict = {}
        self.target = ""
        self.target_queue = []
        self.is_inevitable = False  # Indicates if the enemy's attacks are inevitable

    def format_name(self) -> str:
        if wcswidth(self.name) > 8:
            return self.name
        else:
            return f"{self.name: <{8 + len(self.name) - wcswidth(self.name)}}"

    def receive_damage(self, damage: int):
        if not self.is_break:
            self.dp -= damage
            if self.dp <= 0:
                self.dp_break()
                self.hp += self.dp
                self.dp = 0
        else:
            self.hp -= damage
        if self.hp <= 0:
            self.die()

    def dp_break(self):
        print()
        print(f"{self.format_name()} BREAK！")
        self.is_break = True
        self.down_turn = 1
    
    def die(self):
        self.is_dead = True

    def move(self, battle: Battle):
        if self.is_break:
            self.break_turn += 1
    
    def blast_count(self):
        return sum(self.blast_count_dict.values())

class Rotary_Mole(Enemy):

    def __init__(self):
        max_dp = 0
        for i in range(40):
            max_dp += random.randint(1, 100)
        if max_dp < 1500:
            max_dp = 1500
        max_hp = max_dp + 1000
        super().__init__("Rotary_Mole", "畸旋钻", max_dp, max_hp)
    
    def move(self, battle: Battle):
        if self.is_break:
            self.break_turn += 1
        if self.down_turn:
            return
        if self.break_turn == 2:
            print(f"{self.format_name()} 尝试逃跑！")
            if self.escape(battle):
                battle.lost = True
                return
            self.demise_wave(battle)
            return
        choice = random.randint(1, 2)
        if choice == 1:
            self.attack_single(battle)
        elif choice == 2:
            self.numb_needle(battle)
            
    def escape(self, battle: Battle) -> bool:
        power = battle.d(100, f"{self.format_name()} 的逃跑掷骰")
        for character in battle.character_dict.values():
            if character.on_rotary_mole_escape(battle, power):
                return False
        return True

    def attack_single(self, battle: Battle):
        if self.target_queue:
            self.target = self.target_queue[0]
        if self.target == "":
            self.target = random.sample(list(battle.character_dict.items()), 1)[0][0]
        print(f"{self.format_name()} 发动单体攻击，目标：{battle.character_dict[self.target].format_name()}！")
        power = 20 + battle.d(80)
        print(f"{self.format_name()} 的攻击出力：{power}")
        battle.enemy_single_list.append((Enemy_Single(self.target, power, is_inevitable=self.is_inevitable)))
    
    def numb_needle(self, battle: Battle):
        print(f"{self.format_name()} 发动群体攻击！")
        power = battle.d(100)
        print(f"{self.format_name()} 的攻击出力：{power}")
        battle.enemy_multi_list.append((Enemy_Multi(power, is_inevitable=False)))

    def demise_wave(self, battle: Battle):
        print(f"{self.format_name()} 发动转阶段特殊群体攻击！")
        power = battle.dd(2, 100)
        print(f"{self.format_name()} 的攻击出力：{power}")
        battle.enemy_multi_list.append((Enemy_Multi(power, is_inevitable=False)))

class Hopper(Enemy):

    def __init__(self):
        super().__init__("Hopper", "跳虫", 300, 300)

    def move(self, battle: Battle):
        if self.is_break:
            self.break_turn += 1
        if self.down_turn:
            return
        self.attack_single(battle)

    def attack_single(self, battle: Battle):
        if self.target_queue:
            self.target = self.target_queue[0]
        if self.target == "":
            self.target = random.sample(list(battle.character_dict.items()), 1)[0][0]
        print(f"{self.format_name()} 发动单体攻击，目标：{battle.character_dict[self.target].format_name()}！")
        power = battle.d(50)
        print(f"{self.format_name()} 的攻击出力：{power}")
        battle.enemy_single_list.append(Enemy_Single(self.target, power, is_inevitable=self.is_inevitable))

class Enemy_Damage(object):

    def __init__(self, damage: int, is_inevitable: bool = False):
        self.damage = damage
        self.is_inevitable = is_inevitable

class Enemy_Single(Enemy_Damage):

    def __init__(self, target: str, damage: int, is_inevitable: bool = False):
        super().__init__(damage, is_inevitable)
        self.target = target

class Enemy_Multi(Enemy_Damage):

    def __init__(self, damage: int, is_inevitable: bool = False):
        super().__init__(damage, is_inevitable)
        self.target = None  # Multi-target attacks do not have a specific target
