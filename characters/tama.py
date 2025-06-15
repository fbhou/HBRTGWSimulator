from __future__ import annotations
from typing import TYPE_CHECKING
import random

from character import Character

if TYPE_CHECKING:
    from battle import Battle

class Tama(Character):

    def __init__(self, id: str = "Tama", name: str = "国见玉", troop: str = "31A", internal_id: str = "31A06"):
        super().__init__(id, name, troop, internal_id)
        self.recover_pp = 3
        self.resurrect_pp = 1
        self.spark_pp = 4
        self.charge = 0
        self.has_offensive_ultimate = True
        self.melee = True
        self.priority = 50
    
    def resupply(self, battle: Battle):
        if self.down_turn > 0:
            return
        recover_targets = [character for character in battle.character_dict.values() if character.dp < character.max_dp]
        if len(recover_targets) >= 3:
            print(f"{self.format_name()} 发动技能「饱和恢复」！")
            self.recover_pp -= 1
            for character in recover_targets:
                character.dp = min(character.max_dp, character.dp + 1)
            self.unable_attack_turn += 1
    
    def move(self, battle: Battle):
        if self.is_dead or self.down_turn > 0:
            return
        if self.unable_attack_turn <= 0:
            self.default_attack(battle)
        if self.resurrect_pp > 0 and battle.round >= 3 and self.charge == 0 and min([character.dp for character in battle.character_dict.values()]) <= 1:
            self.vivifying_light(battle)
        if battle.dice_dict.get(self.id, 0) >= 50:
            self.cast_ultimate(battle)

    def default_attack(self, battle: Battle):
        basic_damage = battle.dice_dict.get(self.id, 0) + min(10 * self.charge, 50)
        if self.id in battle.damage_150_list:
            battle.damage_original_dict[self.id] = 1.5 * basic_damage
        elif self.id in battle.damage_200_list:
            battle.damage_original_dict[self.id] = 2 * basic_damage
        else:
            battle.damage_original_dict[self.id] = basic_damage

    def cast_ultimate(self, battle: Battle) -> bool:
        if battle.round < 3:
            return False
        if not battle.in_overdrive and self.spark_pp <= 0:
            print(f"{self.format_name()} 的剩余技能次数不足，无法发动「二律背反火花拨弦」！")
            return False
        battle.skill_list.append(self.bright_spark)
        if not battle.in_overdrive:
            self.spark_pp -= 1
        return True
    
    def vivifying_light(self, battle: Battle):
        print(f"{self.format_name()} 发动必杀技「复苏之光」，恢复我方全员全部偏导护盾至满状态！")
        self.resurrect_pp -= 1
        for character in battle.character_dict.values():
            character.dp = character.max_dp
        self.unable_attack_turn = 99

    def bright_spark(self, battle: Battle):
        from field import Field_thunder
        print(f"{self.format_name()} 发动必杀技「二律背反火花拨弦」！")
        power = 200 + battle.dd(3, 200) + 100 * self.charge
        delta_charge = 2 if isinstance(battle.field, Field_thunder) else 1
        battle.damage_original_dict[self.id] = battle.damage_original_dict.get(self.id, 0) + power
        self.charge += delta_charge
        print(f"{self.format_name()} 的「二律背反火花拨弦」造成 {power} 点伤害，并叠加 {delta_charge} 层充电，当前 {self.charge} 层充电！")

    def on_ally_round_start(self, battle: Battle):
        self.resupply(battle)
