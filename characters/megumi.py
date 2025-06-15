from __future__ import annotations
from typing import TYPE_CHECKING
import random

from character import Character
if TYPE_CHECKING:
    from battle import Battle
class Megumi(Character):

    def __init__(self, id: str = "Megumi", name: str = "逢川惠", troop: str = "31A", internal_id: str = "31A05"):
        super().__init__(id, name, troop, internal_id)
        self.pp = 1
        self.stun_pp = 1
        self.has_offensive_ultimate = True
        self.melee = True
        self.priority = 60

    def move(self, battle: Battle):
        if self.is_dead or self.down_turn > 0 or self.unable_attack_turn > 0:
            return
        self.default_attack(battle)
        if self.stun_pp > 0 and battle.round >= 3 and battle.dice_dict[self.id] >= 75:
            print(f"{self.format_name()} 发动技能「救世主大人的一击！」！")
            self.stun_pp -= 1
            self.savior_strike(battle)

    def savior_strike(self, battle: Battle):
        boss = list(battle.enemy_dict.items())[0][1]
        result = 0
        if self not in battle.success_list:
            result = battle.d(100, f"{boss.format_name()} 的豁免判定")
        if result < battle.dice_dict[self.id]:
            print(f"{boss.format_name()} 被击晕！")
            boss.down_turn = 1
    
    def success_1_3(self, battle: Battle):
        print(f"{self.format_name()} 触发了大成功，抵消了队友的大失败！")
        if battle.failure_list:
            battle.failure_list.pop(0)
    
    def success_4_6(self, battle: Battle):
        print(f"{self.format_name()} 触发了大成功，本回合普攻伤害x1.5！")
        battle.damage_150_list.append(self.id)
    
    def success_7_9(self, battle: Battle):
        print(f"{self.format_name()} 触发了大成功，抵消了队友的大失败，本回合普攻伤害x1.5，并追加发动必杀技！")
        if battle.failure_list:
            battle.failure_list.pop(0)
        battle.damage_150_list.append(self.id)
        self.cast_ultimate(battle)

    def cast_ultimate(self, battle: Battle):
        if self.pp <= 0:
            print(f"{self.format_name()} 的剩余技能次数不足，无法发动「极限冲击」！")
            return False
        battle.skill_list.append(self.excelsior_impact)
        self.pp -= 1
        return True
    
    def excelsior_impact(self, battle: Battle):
        print(f"{self.format_name()} 发动必杀技「极限冲击」！")
        damage_sum = battle.dd(2, 100) + 100
        print(f"{self.format_name()} 的「极限冲击」造成 {damage_sum} 点伤害，并击晕敌人 1 回合！")
        battle.damage_original_dict[self.id] += damage_sum
        boss = list(battle.enemy_dict.items())[0][1]
        boss.down_turn += 1

    def on_ally_failure(self, battle: Battle, ally_id: str) -> bool:
        print(f"{battle.character_dict[ally_id].format_name()} 触发了大失败，{self.format_name()} 尝试发动「极限冲击」！")
        if self.cast_ultimate(battle):
            battle.failure_list.append(self.id)
            return True
        return False
