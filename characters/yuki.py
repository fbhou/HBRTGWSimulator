from __future__ import annotations
from typing import TYPE_CHECKING

from character import Character

if TYPE_CHECKING:
    from battle import Battle

class Yuki(Character):
    def __init__(self, id = "Yuki", name = "和泉由希", troop: str = "31A", internal_id: str = "31A02"):
        super().__init__(id, name, troop, internal_id)
        self.has_offensive_ultimate = False
        self.melee = False
        self.priority = 90
