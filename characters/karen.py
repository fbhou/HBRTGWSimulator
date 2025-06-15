from __future__ import annotations
from typing import TYPE_CHECKING
import random

from character import Character

if TYPE_CHECKING:
    from battle import Battle

class Karen(Character):

    def __init__(self, id = "Karen", name = "朝仓可怜", troop: str = "31A", internal_id: str = "31A04"):
        super().__init__(id, name, troop, internal_id)
        self.pp = 1
        self.has_offensive_ultimate = True
        self.melee = True
        self.priority = 70
    
    def dice(self, battle: Battle) -> int:
        result = battle.d(100, f"{self.format_name()}")
        battle.dice_dict[self.id] = result
        boss = list(battle.enemy_dict.items())[0][1]
        if boss.is_break and result >= 50 and boss.blast_count() < 5:
            print(f"{self.format_name()} 发动技能「杀戮的美学」，叠加 1 层破坏！")
            boss.blast_count_dict[self.id] = boss.blast_count_dict.get(self.id, 0) + 1
        if result <= 3:
            battle.failure_list.append(self.id)
        elif result >= 98:
            battle.success_list.append(self.id)
        return result
    
    def move(self, battle: Battle):
        if self.is_dead or self.down_turn > 0 or self.unable_attack_turn > 0:
            return
        self.default_attack(battle)
        boss = list(battle.enemy_dict.items())[0][1]
        if self.blood_dance not in battle.skill_list and self.pp > 0 and battle.round >= 3 and boss.is_break and battle.dice_dict[self.id] >= 65:
            print(f"{self.format_name()} 尝试发动必杀技「血腥之舞」！")
            self.cast_ultimate(battle)
    
    def cast_ultimate(self, battle):
        if self.pp <= 0:
            print(f"{self.format_name()} 的剩余技能次数不足，无法发动「血腥之舞」！")
            return False
        battle.skill_list.append(self.blood_dance)
        self.pp -= 1
        return True
    
    def blood_dance(self, battle: Battle):
        print(f"{self.format_name()} 发动必杀技「血腥之舞」！")
        boss = list(battle.enemy_dict.items())[0][1]
        power = 0
        blast_sum = 0
        full_success = True
        for _ in range(10):
            damage = battle.d(100)
            if damage >= 50 and boss.blast_count() < 5:
                boss.blast_count_dict[self.id] = boss.blast_count_dict.get(self.id, 0) + 1
                blast_sum += 1
            if damage < 50:
                full_success = False
            power += damage
        print(f"{self.format_name()} 的「血腥之舞」造成了 {power} 点伤害，叠加 {blast_sum} 层破坏，当前 {boss.blast_count()} 层破坏！")
        battle.damage_original_dict[self.id] += power
        if full_success:
            print(f"{self.format_name()} 的必杀技「血腥之舞」全程成功，追加 100 点固定伤害！")
            battle.damage_original_dict[self.id] += 100
        else:
            print(f"{self.format_name()} 因为反作用力无法行动！")
            self.down_turn = 2
