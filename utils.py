from __future__ import annotations
import random
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from battle import Battle

def dp_level_name(dp: int) -> str:
    if dp <= 0:
        return "[完全破盾]"
    if dp == 1:
        return "[重度损伤]"
    if dp == 2:
        return "[中度损伤]"
    if dp == 3:
        return "[轻微损伤]"
    return "[无伤]"

def extra_turn_reason_type_name(reason: int) -> str:
    if reason == 1:
        return "Overdrive"
    elif reason == 2:
        return "技能效果"
    else:
        return "未知原因"
