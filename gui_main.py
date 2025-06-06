# gui_main.py
import FreeSimpleGUI as sg
from prettytable import PrettyTable
import pyglet
import sys
import os
import importlib
import inspect
from pathlib import Path

# Import base classes from your project files
from battle import Battle
from character import Character
from enemy import Enemy

def resource_path(relative_path):
    base_path = getattr(sys, '_MEIPASS', None)
    if base_path is None:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# --- Helper class to redirect print output to the GUI ---
class StdoutRedirector:
    """A class to redirect stdout to a FreeSimpleGUI Multiline element"""
    # We now pass the main window object to the initializer
    def __init__(self, text_element, window):
        self.text_element = text_element
        self.window = window

    def write(self, s):
        """Writes output to the Multiline element and forces a refresh."""
        self.text_element.update(s, append=True)
        # We now call refresh() on the window object we stored
        self.window.refresh()

    def flush(self):
        """Required for compatibility with the file-like object interface."""
        pass

# --- Dynamic Discovery of Characters and Enemies ---

def get_available_characters():
    """Dynamically finds all Character subclasses from the 'characters' directory."""
    characters = {}
    char_path_str = resource_path('characters')
    char_path = Path(char_path_str)
    if not char_path.is_dir():
        sg.popup_error(f"错误：找不到资源文件夹 '{char_path_str}'！")
        return {}
        
    for py_file in char_path.glob('*.py'):
        if py_file.stem == '__init__':
            continue
        try:
            module_name = f'characters.{py_file.stem}'
            module = importlib.import_module(module_name)
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if issubclass(obj, Character) and obj is not Character:
                    # Use the class name as the display name, or define a class attribute for display name
                    display_name = getattr(obj, "name", obj.__name__)
                    characters[display_name] = obj  # Map display name to the class
        except Exception as e:
            print(f"Could not load character from {py_file}: {e}")
            
    return characters

def get_available_enemies():
    """Dynamically finds all Enemy subclasses from the 'enemy' module."""
    enemies = {}
    try:
        module = importlib.import_module('enemy')
        for name, obj in inspect.getmembers(module, inspect.isclass):
            if issubclass(obj, Enemy) and obj is not Enemy:
                instance = obj()
                enemies[instance.name] = obj  # Map display name to the class
    except Exception as e:
        print(f"Could not load enemies: {e}")
        
    return enemies

# --- Main GUI Application ---

def main():
    pyglet.font.add_file(resource_path('resources/MapleMono-NF-CN-Regular.ttf'))

    # Discover available characters and enemies
    available_characters = get_available_characters()
    available_enemies = get_available_enemies()

    if not available_characters or not available_enemies:
        sg.popup_error("错误", "未能找到角色或敌人文件。\n请确保可执行程序与您的 `characters` 文件夹在同一目录下。")
        return
    
    available_characters = dict(sorted(available_characters.items(), key=lambda item: item[1]().internal_id))

    sg.theme('SystemDefault')

    # --- GUI Layout Definition ---
    character_frame = sg.Frame('选择队员（至少1名）', [
        [sg.Checkbox(name, key=f'char_{name}', font=('Maple Mono NF CN', 12))] for name in available_characters.keys()
    ], font=('Maple Mono NF CN', 12))
    
    enemy_frame = sg.Frame('选择敌人', [
        [sg.Radio(name, 'ENEMY_RADIO', key=f'enemy_{name}', default=(i==0), font=('Maple Mono NF CN', 12))] for i, name in enumerate(available_enemies.keys())
    ], font=('Maple Mono NF CN', 12))

    log_column = [
        [sg.Text('战斗日志', font=('Maple Mono NF CN', 12))],
        [sg.Multiline(size=(100, 30), key='-LOG-', autoscroll=True, disabled=True, font=('Maple Mono NF CN', 10))],
    ]
    
    layout = [
        [sg.Column([[character_frame], [enemy_frame]]), sg.Column(log_column)],
        [sg.Button('开始战斗', font=('Maple Mono NF CN', 12)), sg.Button('清空日志', font=('Maple Mono NF CN', 12)), sg.Button('退出', font=('Maple Mono NF CN', 12))]
    ]

    window = sg.Window('红烧小祥战斗模拟器', layout)
    original_stdout = sys.stdout

    # --- Event Loop ---
    while True:
        result = window.read()
        if result is None:
            break
        event, values = result

        if event == sg.WIN_CLOSED or event == '退出':
            break

        if event == '清空日志':
            log_elem = window['-LOG-']
            if log_elem is not None:
                log_elem.update(value='')

        if event == '开始战斗':
            selected_char_names = [name for name in available_characters if values[f'char_{name}']]
            selected_enemy_name = next((name for name in available_enemies if values[f'enemy_{name}']), None)

            if not selected_char_names:
                sg.popup('错误', '请至少选择一名队员。')
                continue
            
            log_elem = window['-LOG-']
            if log_elem is not None:
                log_elem.update(value='--- 正在准备战斗... ---\n')
            
            battle = Battle()
            for char_name in selected_char_names:
                char_class = available_characters[char_name]
                char_instance = char_class()
                battle.character_dict[char_instance.id] = char_instance
            
            enemy_class = available_enemies[selected_enemy_name]
            enemy_instance = enemy_class()
            battle.enemy_dict[enemy_instance.id] = enemy_instance

            # Reroute stdout and run the simulation
            sys.stdout = StdoutRedirector(window['-LOG-'], window)
            try:
                print("########## 战斗开始 ##########")
                
                while not battle.winned and not battle.lost:
                    battle.run_round()
                
                if battle.winned:
                    print("\n胜利！")
                else:
                    print("\n失败！")

                print("\n########## 战斗结束 ##########")
                print("########## 伤害统计 ##########")

                table = PrettyTable()
                table.field_names = ["队员", "aD", "rD"]
                for character in battle.character_dict.values():
                    table.add_row([character.name, f"{character.ad:>8.1f}", f"{character.rd:>8.1f}"])
                print(table)

            except Exception as e:
                print(f"\n--- 发生错误 ---\n模拟过程中出现异常: {e}")
            finally:
                # Restore original stdout
                sys.stdout = original_stdout 

    window.close()

if __name__ == "__main__":
    main()
