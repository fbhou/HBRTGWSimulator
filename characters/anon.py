from __future__ import annotations
from typing import TYPE_CHECKING

from battle import Battle
from character import Character
from utils import dp_level_name

if TYPE_CHECKING:
    from battle import Battle
from enemy import Enemy_Single, Enemy_Multi

class Anon(Character):
    def __init__(self, id: str = "Anon", name: str = "千早爱音", troop: str = "30A", internal_id: str = "30A01"):
        super().__init__(id, name, troop, internal_id)
        self.has_offensive_ultimate = False
        self.melee = True
        self.invincible_cd = 0
        self.reflect_cd = 0
        self.priority = -100
    
    def move(self, battle: Battle):
        if self.invincible_cd > 0:
            self.invincible_cd -= 1
        if self.reflect_cd > 0:
            self.reflect_cd -= 1
        if self.is_dead or self.down_turn > 0:
            return
        boss = list(battle.enemy_dict.values())[0]
        if boss.down_turn > 0:
            self.dice(battle)
            self.default_attack(battle)
            if self.id in battle.success_list:
                self.success(battle)
            if self.id in battle.failure_list:
                self.failure(battle)
    
    def i_will_protect_everyone(self, battle: Battle) -> bool:
        if self.is_dead:
            return False
        print(f"{self.format_name()} 发动技能「哼哼，就由我来保护大家！」")
        boss = list(battle.enemy_dict.values())[0]
        boss.target_queue.insert(0, self.id)
        self.unable_attack_turn += 1
        return True

    def receive_single_damage(self, battle: Battle, damage: Enemy_Single):
        if not damage.is_inevitable and self.invincible_cd <= 0 and self.unable_dodge_turn <= 0 and self.down_turn <= 0:
            print(f"{self.format_name()} 发动技能「我的护盾可是无敌的~！」")
            self.invincible_cd = 1
            boss = list(battle.enemy_dict.values())[0]
            result = battle.d(100, f"{self.format_name()} 的反击掷骰")
            if result >= 50:
                print(f"{self.format_name()} 反击成功！")
                boss.receive_damage(result)
            if not damage.is_inevitable and damage.damage < 50:
                print(f"敌人的攻击被无效化！")
                return
        if not damage.is_inevitable and self.unable_dodge_turn <= 0 and self.down_turn <= 0:
            dodge = battle.d(100, f"{self.format_name()} 的闪避掷骰")
            if dodge >= damage.damage:
                print(f"{self.format_name()} 闪避成功！")
                return
            elif dodge >= damage.damage / 2:
                print(f"{self.format_name()} 闪避部分伤害！{dp_level_name(self.dp)} → {dp_level_name(self.dp)}")
                return
        print(f"{self.format_name()} 未能闪避！{dp_level_name(self.dp)} → {dp_level_name(self.dp - 1)}")
        self.dp -= 1
        if self.dp <= 0:
            self.is_dead = True
        
    def i_will_reflect_enemy_skill(self, battle: Battle, damage: Enemy_Multi) -> bool:
        boss = list(battle.enemy_dict.values())[0]
        if damage.is_inevitable:
            return False
        if self.reflect_cd <= 0:
            self.reflect_cd = 2
            print(f"{self.format_name()} 发动技能「看我把敌人的招式弹回去！」")
            result = battle.d(100, f"{self.format_name()} 的对抗掷骰")
            if result >= damage.damage:
                print(f"{self.format_name()} 对抗成功，无效化本次攻击并追加 {damage.damage + result} 反弹伤害！")
                boss.receive_damage(damage.damage + result)
                return True
            elif result >= damage.damage / 2:
                print(f"{self.format_name()} 对抗失败，仅自身受到伤害")
                self.receive_single_damage(battle, Enemy_Single(self.id, damage.damage, is_inevitable=True))
                return True
            else:
                print(f"{self.format_name()} 防御失败")
                return False
        else:
            print(f"{self.format_name()} 勉强发动技能「看我把敌人的招式弹回去！」")
            result = battle.d(100, f"{self.format_name()} 的对抗掷骰")
            if result >= damage.damage:
                print(f"{self.format_name()} 对抗成功，无效化本次攻击并追加 {damage.damage + result} 反弹伤害！")
                self.receive_single_damage(battle, Enemy_Single(self.id, damage.damage, is_inevitable=True))
                boss.receive_damage(damage.damage + result)
                return True
            elif result >= damage.damage / 2:
                print(f"{self.format_name()} 对抗失败，仅自身受到伤害")
                self.receive_single_damage(battle, Enemy_Single(self.id, damage.damage, is_inevitable=True))
                return True
            else:
                print(f"{self.format_name()} 防御失败")
                return False
            
    def on_ally_round_start(self, battle: Battle):
        self.i_will_protect_everyone(battle)

    def on_enemy_multi_damage(self, battle: Battle, damage: Enemy_Multi):
        if self.i_will_reflect_enemy_skill(battle, damage):
            damage.damage = 0

    def on_rotary_mole_escape(self, battle: Battle, power: int) -> bool:
        boss = list(battle.enemy_dict.values())[0]
        result = battle.d(100, f"{self.format_name()} 的阻挡掷骰")
        if result + 50 >= power:
            print(f"{self.format_name()} 成功阻挡了 {boss.format_name()} 的逃跑！")
            return True
        else:
            print(f"{self.format_name()} 未能阻挡 {boss.format_name()} 的逃跑！")
            return False
