from __future__ import annotations
from typing import TYPE_CHECKING

from character import Character

if TYPE_CHECKING:
    from battle import Battle

class Ruka(Character):
    def __init__(self, id: str = "Ruka", name: str = "茅森月歌", troop: str = "31A", internal_id: str = "31A01"):
        super().__init__(id, name, troop, internal_id)
        self.pp = 1
        self.has_offensive_ultimate = True
        self.melee = True
        self.rediced = False
        self.priority = 100

    def dice(self, battle: Battle) -> int:
        result = battle.d(100, f"{self.format_name()}")
        if result < 50:
            print(f"{self.format_name()} 发动技能「二刀流」，攻击骰重骰取高！")
            self.rediced = True
            result = max(result, battle.d(100))
        battle.dice_dict[self.id] = result
        if result <= 3:
            battle.failure_list.append(self.id)
        elif result >= 98:
            battle.success_list.append(self.id)
        return result

    def move(self, battle: Battle):
        if self.is_dead or self.down_turn > 0 or self.unable_attack_turn > 0:
            return
        self.default_attack(battle)
        if self.ephemeral_cascade not in battle.skill_list:
            danger = False
            for character_id, character in battle.character_dict.items():
                if character.dp <= 1:
                    danger = True
                    break
            if danger:
                print(f"{self.format_name()} 发现队友处于危险状态，尝试发动必杀技「梦幻泡影+」！")
                self.cast_ultimate(battle)
        if self.ephemeral_cascade not in battle.skill_list:
            if list(battle.enemy_dict.items())[0][1].is_break and battle.dice_dict[self.id] >= 85:
                print(f"{self.format_name()} 攻击掷骰≥85，尝试发动必杀技「梦幻泡影+」！")
                self.cast_ultimate(battle)

    def cast_ultimate(self, battle: Battle):
        if self.pp <= 0:
            print(f"{self.format_name()} 的剩余技能次数不足，无法发动「梦幻泡影+」！")
            return False
        battle.skill_list.append(self.ephemeral_cascade_plus)
        self.pp -= 1
        return True

    def ephemeral_cascade(self, battle: Battle):
        power = 0
        if list(battle.enemy_dict.items())[0][1].is_break:
            print(f"{self.format_name()} 发动必杀技「梦幻泡影」（强化版）！")
            power += battle.dd(9, 100) + 100
        else:
            print(f"{self.format_name()} 发动必杀技「梦幻泡影」！")
            power += battle.dd(5, 50) + battle.dd(4, 100)
        print(f"{self.format_name()} 的「梦幻泡影」造成 {power} 点伤害！")
        battle.damage_original_dict[self.id] = battle.damage_original_dict.get(self.id, 0) + power

    def ephemeral_cascade_plus(self, battle: Battle):
        print(f"{self.format_name()} 发动必杀技「梦幻泡影+」！")
        power = battle.dd(9, 100) + 100
        print(f"{self.format_name()} 的「梦幻泡影+」造成 {power} 点伤害！")
        battle.damage_original_dict[self.id] = battle.damage_original_dict.get(self.id, 0) + power
        if battle.d(2, "派生分支") == 1:
            self.blazing_ignition(battle)
        else:
            self.lunar_flurry(battle)

    def blazing_ignition(self, battle: Battle):
        from field import Field_fire
        print(f"{self.format_name()} 发动衍生技能「烈火燎原」！")
        if isinstance(battle.field, Field_fire):
            power = max(battle.dd(4, 500) + 200, 1000)
        else:
            power = battle.dd(2, 500) + 100
        print(f"{self.format_name()} 的「烈火燎原」造成 {power} 点伤害！")
        battle.damage_original_dict[self.id] = battle.damage_original_dict.get(self.id, 0) + power

    def lunar_flurry(self, battle: Battle):
        print(f"{self.format_name()} 发动衍生技能「万紫千红」！")
        power = 0
        od = 0
        for _ in range(12):
            damage = battle.d(100)
            power += damage
            if damage >= 50:
                od += 1
        print(f"{self.format_name()} 的「万紫千红」造成 {power} 点伤害，叠加 {od} 层超频条！")
        battle.overdrive += od
        battle.damage_original_dict[self.id] = battle.damage_original_dict.get(self.id, 0) + power
