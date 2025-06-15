from __future__ import annotations
import random
from typing import TYPE_CHECKING

from field import Field
from utils import dp_level_name

if TYPE_CHECKING:
    from character import Character
    from enemy import Enemy_Single, Enemy_Multi

class Battle(object):
    def __init__(self):
        self.log = []

        self.character_dict = {}
        self.enemy_dict = {}
        self.dice_dict = {}
        self.damage_original_dict = {}
        self.success_list = []
        self.failure_list = []
        self.damage_150_list = []
        self.damage_200_list = []
        self.damage_blast_dict = {}
        self.damage_buff_dict = {}
        self.damage_extra_dict = {}
        self.field = Field()
        self.skill_list = []
        self.enemy_single_list = []
        self.enemy_multi_list = []
        self.overdrive = 0
        self.in_overdrive = False
        
        self.round = 0
        self.winned = False
        self.lost = False

    def run_round(self):
        self.round += 1
        self.dice_dict = {}
        self.damage_original_dict = {}
        self.success_list = []
        self.failure_list = []
        self.damage_150_list = []
        self.damage_200_list = []
        self.damage_blast_dict = {}
        self.damage_buff_dict = {}
        self.damage_extra_dict = {}
        self.skill_list = []
        self.enemy_single_list = []
        self.enemy_multi_list = []

        self.ally_round()
        if self.lost or self.winned:
            return
        if self.overdrive * len(self.enemy_dict) >= 10:
            self.in_overdrive = True
            self.overdrive = 0
            self.dice_dict = {}
            self.damage_original_dict = {}
            self.success_list = []
            self.failure_list = []
            self.damage_150_list = []
            self.damage_200_list = []
            self.damage_blast_dict = {}
            self.damage_extra_dict = {}
            self.skill_list = []
            print("--- 额外回合 ---")
            self.ally_round()
            self.in_overdrive = False
        if self.lost or self.winned:
            return
        
        self.enemy_round()
        if self.lost or self.winned:
            return
        
        # Update battle states at the end of the round
        for character in self.character_dict.values():
            if character.down_turn > 0:
                character.down_turn -= 1
            if character.unable_attack_turn > 0:
                character.unable_attack_turn -= 1
            if character.unable_dodge_turn > 0:
                character.unable_dodge_turn -= 1
            if character.is_dead:
                self.lost = True
        temp_enemy_dict = self.enemy_dict.copy()
        for enemy_id, enemy in temp_enemy_dict.items():
            if enemy.is_dead:
                self.enemy_dict.pop(enemy_id)
        if not self.enemy_dict:
            self.winned = True
        
    def ally_round(self):
        # Print round information
        print()
        print(f"--- Round {self.round} ---")
        print()
        print("角色状态：")
        for id, character in self.character_dict.items():
            print(f"{character.format_name()} - DP: {dp_level_name(character.dp)}, Down Turn: {character.down_turn}")
            self.damage_original_dict[id] = 0
            character.rediced = False
        print("敌人状态：")
        for enemy in self.enemy_dict.values():
            print(f"{enemy.format_name()} - DP: {enemy.dp}, HP: {enemy.hp}, Is Break: {enemy.is_break}, Down Turn: {enemy.down_turn}, Blast Count: {enemy.blast_count()}, Target Queue: {enemy.target_queue}, Break Turn: {enemy.break_turn}")
        print("")

        boss = list(self.enemy_dict.items())[0][1]

        for character in self.character_dict.values():
            character.on_ally_round_start(self)

        # Attack dice rolls
        print("攻击掷骰：")
        for character in self.character_dict.values():
            if character.down_turn > 0:
                print(f"{character.format_name()}：无法行动")
            elif character.unable_attack_turn > 0:
                print(f"{character.format_name()}：无法攻击")
            else:
                character.dice(self)
        
        # Process dice results
        for character in self.character_dict.values():
            character.on_dice_finish(self)

        # Process successes and failures
        for id in self.success_list:
            self.character_dict[id].success(self)
        for id in self.failure_list:
            self.character_dict[id].failure(self)

        # Main moves
        for character in self.character_dict.values():
            character.move(self)

        # Process skills
        for skill in self.skill_list:
            skill(self)
        
        # Process field effects
        if self.field:
            self.field.effect(self)
        
        # Process blast rate
        if boss.is_break:
            self.damage_blast_dict = {character_id: 20 * boss.blast_count_dict.get(character_id, 0) for character_id in boss.blast_count_dict.keys()}

        # Damage statistics
        for id, damage in self.damage_original_dict.items():
            if id == "None":
                continue
            character = self.character_dict[id]
            character.rd += damage
            character.ad += damage * (1 + sum(self.damage_buff_dict.values()))
        for id, damage in self.damage_blast_dict.items():
            character = self.character_dict[id]
            character.rd += damage * (1 + sum(self.damage_buff_dict.values()))
            effective_characters = [id for id in self.damage_original_dict.keys() if id != "None" and self.damage_original_dict[id] > 0]
            for id in effective_characters:
                character = self.character_dict[id]
                character.ad += damage * (1 + sum(self.damage_buff_dict.values())) / len(effective_characters)
        for id, buff in self.damage_buff_dict.items():
            character = self.character_dict[id]
            character.rd += buff * sum(list(self.damage_original_dict.values()))
        for id, damage in self.damage_extra_dict.items():
            character = self.character_dict[id]
            character.rd += damage
            character.ad += damage

        # Apply damage to enemies
        total_damage = (sum(self.damage_original_dict.values()) + sum(self.damage_blast_dict.values())) * (1 + sum(self.damage_buff_dict.values()))
        total_damage += sum(self.damage_extra_dict.values())
        print("")
        print(f"总伤害：{total_damage}")
        print("")

        list(self.enemy_dict.items())[0][1].receive_damage(total_damage)

        # Update character states at the end of the round
        temp_enemy_dict = self.enemy_dict.copy()
        for enemy_id, enemy in temp_enemy_dict.items():
            if enemy.is_dead:
                self.enemy_dict.pop(enemy_id)
        if not self.enemy_dict:
            self.winned = True

    def enemy_round(self):
        for character in self.character_dict.values():
            character.on_enemy_round_start(self)

        # Enemy move
        for enemy in self.enemy_dict.values():
            enemy.move(self)
        
        # Process enemy attacks
        for enemy_single in self.enemy_single_list:
            for character in self.character_dict.values():
                character.on_enemy_single_damage(self, enemy_single)
            if enemy_single.target in self.character_dict:
                self.character_dict[enemy_single.target].receive_damage(self, enemy_single)
        
        for enemy_multi in self.enemy_multi_list:
            for character in self.character_dict.values():
                character.on_enemy_multi_damage(self, enemy_multi)
            if enemy_multi.damage > 0:
                for character in self.character_dict.values():
                    character.receive_damage(self, enemy_multi)
        
        # Update enemy states
        for enemy in self.enemy_dict.values():
            if enemy.down_turn > 0:
                enemy.down_turn -= 1
            if enemy.target_queue:
                if len(enemy.target_queue) == 1:
                    enemy.target_queue = []
                else:
                    enemy.target_queue = enemy.target_queue[1:]

    def d(self, bound: int, message: str = "") -> int:
        result = random.randint(1, bound)
        for character in self.character_dict.values():
            character.on_dice_result(self, result)
        if message == "":
            print(f"1d{bound} = {result}")
        else:
            print(f"{message}：1d{bound} = {result}")
        return result

    def dd(self, num: int, bound: int, message: str = "") -> int:
        res = 0
        for i in range(num):
            result = random.randint(1, bound)
            for character in self.character_dict.values():
                character.on_dice_result(self, result)
            res += result
        if message == "":
            print(f"{num}d{bound} = {res}")
        else:
            print(f"{message}：{num}d{bound} = {res}")
        return res
