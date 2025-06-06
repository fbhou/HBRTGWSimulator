from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from battle import Battle

class Field(object):
    def __init__(self, source: str = "", name: str = "默认场地"):
        self.source = source
        self.name = name
    
    def effect(self, battle: Battle):
        pass

class Field_fire(Field):
    def __init__(self, source = "", name = "属性场地·火"):
        super().__init__(source, name)
    
    def effect(self, battle):
        battle.damage_extra_dict[self.source] = battle.damage_extra_dict.get(self.source, 0) + 20

class Field_thunder(Field):
    def __init__(self, source = "", name = "属性场地·雷"):
        super().__init__(source, name)
    
    def effect(self, battle):
        from characters.tama import Tama
        for character in battle.character_dict.values():
            if isinstance(character, Tama):
                tama = character
                thunder_damage = min(10 * tama.charge, 50)
                for id, character in battle.character_dict.items():
                    if id != tama.id and character.is_melee and character.down_turn <= 0 and character.unable_attack_turn <= 0:
                        battle.damage_original_dict[id] = battle.damage_original_dict.get(id, 0) + thunder_damage
                        character.rd -= thunder_damage
                        tama.rd += thunder_damage
