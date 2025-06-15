from __future__ import annotations
from typing import TYPE_CHECKING
import random

from battle import Battle
from character import Character
from field import Field_fire

if TYPE_CHECKING:
    from field import *

class Tsukasa(Character):

    def __init__(self, id: str = "Tsukasa", name: str = "东城司", troop: str = "31A", internal_id: str = "31A03"):
        super().__init__(id, name, troop, internal_id)
        self.pp = 1
        self.enhancement_cd = 0
        self.has_offensive_ultimate = False
        self.melee = False
        self.priority = 80

    def select_enhancement_target(self, battle: Battle, count: int) -> list:
        temp_dice_dict = battle.dice_dict.copy()
        selected_targets = []
        while temp_dice_dict and len(selected_targets) < count:
            if not temp_dice_dict:
                break
            character_id = min(temp_dice_dict.items(), key=lambda item: item[1])[0]
            if character_id in battle.failure_list or battle.character_dict[character_id].rediced:
                temp_dice_dict.pop(character_id)
                continue
            if temp_dice_dict[character_id] >= 50:
                break
            selected_targets.append(character_id)
            temp_dice_dict.pop(character_id)
        return selected_targets

    def enhancement(self, battle: Battle):
        if self.enhancement_cd > 0:
            print(f"{self.format_name()} 的技能「强化」冷却中，剩余 {self.enhancement_cd} 回合。")
            self.enhancement_cd -= 1
            return
        if self.select_enhancement_target(battle, 1):
            character_id = self.select_enhancement_target(battle, 1)[0]
            print(f"{self.format_name()} 发动技能「强化」，将 {battle.character_dict[character_id].format_name()} 的攻击出力修正为 50！")
            self.rd += 50 - battle.dice_dict[character_id]
            battle.character_dict[character_id].rd -= 50 - battle.dice_dict[character_id]
            battle.dice_dict[character_id] = 50
            self.enhancement_cd = 1

    def memento_mori(self, battle: Battle):
        target_ids = self.select_enhancement_target(battle, 3)
        if battle.round >= 3 and self.pp > 0 and self.enhancement_cd <= 0 and len(target_ids) >= 3:
            self.pp -= 1
            print(f"{self.format_name()} 发动必杀技「生死无常」！")
            for target_id in target_ids:
                target = battle.character_dict[target_id]
                print(f"将 {target.format_name()} 的攻击出力提升 50！")
                self.rd += 50
                target.rd -= 50
                battle.dice_dict[target_id] += 50
            print(f"{self.format_name()} 追加 100 点固定伤害并开启「属性场地·火」！")
            battle.damage_extra_dict[self.id] = 100
            battle.field = Field_fire(source=self.id)
            self.enhancement_cd = 1

    def success_7_9(self, battle: Battle):
        temp_character_list = []
        for character in battle.character_dict.values():
            if character.is_dead or character.down_turn > 0 or character.unable_attack_turn > 0:
                continue
            if character.has_offensive_ultimate:
                temp_character_list.append(character)
        if temp_character_list:
            character = random.choice(temp_character_list)
            print(f"{self.format_name()} 尝试追加发动 {character.format_name()} 的必杀技！")
            character.cast_ultimate(battle)
        else:
            print(f"队友呢队友呢救一下啊！")

    def on_dice_finish(self, battle: Battle):
        if self.down_turn <= 0 and self.unable_attack_turn <= 0:
            self.memento_mori(battle)
            self.enhancement(battle)
