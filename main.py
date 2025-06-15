from prettytable import PrettyTable

from battle import Battle
from enemy import *
from characters.ruka import Ruka
from characters.yuki import Yuki
from characters.tsukasa import Tsukasa
from characters.karen import Karen
from characters.megumi import Megumi
from characters.tama import Tama
from characters.anon import Anon

if __name__ == "__main__":
    battle = Battle()
    print("########## 战斗开始 ##########")
    
    ruka_id = "Ruka"
    ruka = Ruka(ruka_id)
    battle.character_dict[ruka_id] = ruka

    yuki_id = "Yuki"
    yuki = Yuki(yuki_id)
    battle.character_dict[yuki_id] = yuki

    tsukasa_id = "Tsukasa"
    tsukasa = Tsukasa(tsukasa_id)
    battle.character_dict[tsukasa_id] = tsukasa

    karen_id = "Karen"
    karen = Karen(karen_id)
    battle.character_dict[karen_id] = karen

    megumi_id = "Megumi"
    megumi = Megumi(megumi_id)
    battle.character_dict[megumi_id] = megumi

    tama_id = "Tama"
    tama = Tama(tama_id)
    battle.character_dict[tama_id] = tama

    anon_id = "Anon"
    anon = Anon(anon_id)
    battle.character_dict[anon_id] = anon

    # hopper_id = "Hopper"
    # hopper = Hopper()
    # battle.enemy_dict[hopper_id] = hopper

    rotary_mole_id = "RotaryMole"
    rotary_mole = Rotary_Mole()
    battle.enemy_dict[rotary_mole_id] = rotary_mole

    while not battle.winned and not battle.lost:
        battle.run_round()
    
    if battle.winned:
        print("胜利！")
    else:
        print("失败！")

    print("########## 战斗结束 ##########")
    print("########## 伤害统计 ##########")
    table = PrettyTable()
    table.field_names = ["队员", "aD", "rD"]
    for character in battle.character_dict.values():
        table.add_row([character.name, f"{character.ad:>8.1f}", f"{character.rd:>8.1f}"])
    print(table)