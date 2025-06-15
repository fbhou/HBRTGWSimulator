from __future__ import annotations
import random
from typing import TYPE_CHECKING
from wcwidth import wcswidth

from enemy import Enemy_Single, Enemy_Multi, Enemy_Damage
from utils import *

if TYPE_CHECKING:
    from battle import Battle

class Character(object):

    def __init__(self, id: str = "Default", name: str = "默认队员", troop: str = "", internal_id: str = "00A00"):
        self.max_dp = 4
        self.dp = self.max_dp
        self.id = id
        self.name = name
        self.troop = troop
        self.internal_id = internal_id
        self.down_turn = 0
        self.unable_attack_turn = 0
        self.unable_dodge_turn = 0
        self.is_dead = False
        self.rediced = False
        self.ad = 0
        self.rd = 0
        self.has_offensive_ultimate = False
        self.melee = True
        self.priority = 0
    
    def format_name(self) -> str:
        if wcswidth(self.name) > 8:
            return self.name
        else:
            return f"{self.name: <{8 + len(self.name) - wcswidth(self.name)}}"

    def dice(self, battle: Battle) -> int:
        result = battle.d(100, f"{self.format_name()}")
        battle.dice_dict[self.id] = result
        if result <= 3:
            battle.failure_list.append(self.id)
        if result >= 98:
            battle.success_list.append(self.id)
        return result

    def success(self, battle: Battle):
        result = 0
        level = 1
        while True:
            if level < 1:
                break
            result = battle.d(10, f"{self.format_name()} 的大成功掷骰")
            if result == 10:
                result = battle.d(2, f"")
                if result == 1:
                    print(f"{self.format_name()} 触发了未结算的多重大成功！")
                    level += 1
                    continue
                else:
                    level -= 1
                    continue
            elif result <= 3:
                self.success_1_3(battle)
                break
            elif result <= 6:
                self.success_4_6(battle)
                break
            else:
                self.success_7_9(battle)
            break
    
    def success_1_3(self, battle: Battle):
        print(f"{self.format_name()} 触发了大成功，本回合普攻伤害x1.5！")
        battle.damage_150_list.append(self.id)
    
    def success_4_6(self, battle: Battle):
        print(f"{self.format_name()} 触发了大成功，本回合普攻伤害x2！")
        battle.damage_200_list.append(self.id)
    
    def success_7_9(self, battle: Battle):
        print(f"{self.format_name()} 触发了大成功，本回合普攻伤害x2！")
        battle.damage_200_list.append(self.id)
        print(f"{self.format_name()} 追加发动必杀技！")
        self.cast_ultimate(battle)
            
    def failure(self, battle: Battle):
        for character_id in battle.character_dict:
            if character_id != self.id:
                if battle.character_dict[character_id].on_ally_failure(battle, character_id):
                    return
        result = 0
        level = 1
        while True:
            if level < 1:
                break
            result = battle.d(10, f"{self.format_name()} 的大失败掷骰")
            if result == 10:
                result = battle.d(2, f"")
                if result == 2:
                    print(f"{self.format_name()} 触发了未结算的多重大失败！")
                    level += 1
                    continue
                else:
                    level -= 1
                    continue
            elif result <= 3:
                self.failure_1_3(battle)
                break
            elif result <= 6:
                self.failure_4_6(battle)
                break
            else:
                self.failure_7_9(battle)
            break
    
    def failure_1_3(self, battle: Battle):
        print(f"{self.format_name()} 触发了大失败，被锁定为敌方单体攻击目标！")
        boss = list(battle.enemy_dict.items())[0][1]
        if boss.target_queue:
            if boss.target_queue[0] == self.id:
                boss.target_queue.append(self.id)
            else:
                boss.target_queue[0] = self.id
        else:
            boss.target_queue.append(self.id)
    
    def failure_4_6(self, battle: Battle):
        print(f"{self.format_name()} 触发了大失败，被锁定为敌方单体攻击目标！")
        boss = list(battle.enemy_dict.items())[0][1]
        if boss.target_queue:
            if boss.target_queue[0] == self.id:
                boss.target_queue.append(self.id)
            else:
                boss.target_queue[0] = self.id
        else:
            boss.target_queue.append(self.id)
        print(f"{self.format_name()} 本回合无法闪避！")
        self.unable_dodge_turn += 1

    def failure_7_9(self, battle: Battle):
        print(f"{self.format_name()} 触发了大失败，本回合无法行动！")
        self.down_turn += 1

    def move(self, battle: Battle):
        if self.is_dead or self.down_turn > 0 or self.unable_attack_turn > 0:
            return
        self.default_attack(battle)
    
    def default_attack(self, battle: Battle):
        if self.id in battle.damage_150_list:
            battle.damage_original_dict[self.id] = 1.5 * battle.dice_dict[self.id]
        elif self.id in battle.damage_200_list:
            battle.damage_original_dict[self.id] = 2 * battle.dice_dict[self.id]
        else:
            battle.damage_original_dict[self.id] = battle.dice_dict[self.id]

    def default_skill(self, battle: Battle):
        pass

    def default_ultimate(self, battle: Battle):
        pass

    def cast_ultimate(self, battle: Battle) -> bool:
        if self.default_ultimate not in battle.skill_list:
            battle.skill_list.append(self.default_ultimate)
            return True
        return False

    def receive_damage(self, battle: Battle, damage: Enemy_Damage):
        if isinstance(damage, Enemy_Single):
            self.receive_single_damage(battle, damage)
        elif isinstance(damage, Enemy_Multi):
            self.receive_multi_damage(battle, damage)
        if self.dp <= 0:
            self.is_dead = True

    def receive_single_damage(self, battle: Battle, damage: Enemy_Single):
        if not damage.is_inevitable and self.unable_dodge_turn <= 0 and self.down_turn <= 0:
            dodge = battle.d(100, f"{self.format_name()} 的闪避掷骰")
            if dodge >= damage.damage:
                print(f"{self.format_name()} 闪避成功！")
                return
            elif dodge >= damage.damage / 2:
                print(f"{self.format_name()} 闪避部分伤害！{dp_level_name(self.dp)} → {dp_level_name(self.dp - 1)}")
                self.dp -= 1
                return
        print(f"{self.format_name()} 未能闪避！{dp_level_name(self.dp)} → {dp_level_name(self.dp - 2)}")
        self.dp -= 2

    def receive_multi_damage(self, battle: Battle, damage: Enemy_Multi):
        if not damage.is_inevitable and self.unable_dodge_turn <= 0 and self.down_turn <= 0:
            dodge = battle.d(100, f"{self.format_name()} 的闪避掷骰")
            if dodge >= damage.damage:
                print(f"{self.format_name()} 闪避成功！")
                return
            elif dodge >= damage.damage / 2:
                print(f"{self.format_name()} 闪避部分伤害！{dp_level_name(self.dp)} → {dp_level_name(self.dp - 1)}")
                self.dp -= 1
                return
        print(f"{self.format_name()} 未能闪避！{dp_level_name(self.dp)} → {dp_level_name(self.dp - 2)}")
        self.dp -= 2

    def on_ally_round_start(self, battle: Battle):
        pass

    def on_enemy_round_start(self, battle: Battle):
        pass

    def on_dice_result(self, battle: Battle, result: int):
        pass

    def on_dice_finish(self, battle: Battle):
        pass
    
    def on_enemy_single_damage(self, battle: Battle, damage: Enemy_Single):
        pass

    def on_enemy_multi_damage(self, battle: Battle, damage: Enemy_Multi):
        pass

    def on_rotary_mole_escape(self, battle: Battle, power: int) -> bool:
        return False
    
    def on_ally_failure(self, battle: Battle, ally_id: str) -> bool:
        return False
