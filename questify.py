import os
import sys
import shutil
import time
import re
import subprocess
import requests
import webbrowser
import difflib
import threading
import msvcrt
import json

VERSION = "4.1"
GITHUB_REPO = "orqz/questify"

url = "https://discord.com/api/applications/detectable"
gamelist = requests.get(url).json()

SELF_PATH = os.path.abspath(sys.argv[0])
SELF_DIR = os.path.dirname(SELF_PATH)
SELF_NAME = os.path.basename(SELF_PATH).lower()

QUESTIFY_HOME = os.path.join(
    os.environ.get("LOCALAPPDATA", os.path.expanduser("~")),
    "Questify", "games"
)

def get_slot_path(slot):
    return os.path.join(QUESTIFY_HOME, f"slot_{slot}")

def build_game_folder(base, safe_name, parts):
    folder = os.path.join(base, safe_name)
    index = 0
    while index < len(parts) - 1:
        folder = os.path.join(folder, parts[index])
        index = index + 1
    return folder

def save_state(base_folder, exe_path, safe_name, parts, exe_file, slot):
    data = {
        "app": "Questify",
        "version": VERSION,
        "folder": base_folder,
        "exe_path": exe_path,
        "safe_name": safe_name,
        "parts": parts,
        "exe_file": exe_file,
        "launcher": SELF_PATH,
        "slot": slot,
    }
    state_path = os.path.join(os.path.dirname(exe_path), "questify_config.json")
    with open(state_path, "w") as f:
        json.dump(data, f, indent=2)

def load_state():
    state_path = os.path.join(SELF_DIR, "questify_config.json")
    if os.path.exists(state_path):
        with open(state_path, "r") as f:
            return json.load(f)
    return None

def cleanup_previous():
    cleanup_path = os.path.join(SELF_DIR, "questify_cleanup.txt")
    if not os.path.exists(cleanup_path):
        return
    try:
        with open(cleanup_path, "r") as f:
            old_folder = f.read().strip()
        if old_folder and os.path.isdir(old_folder) and os.path.normpath(old_folder) != os.path.normpath(SELF_DIR):
            shutil.rmtree(old_folder, ignore_errors=True)
        os.remove(cleanup_path)
    except Exception:
        pass

def check_version():
    try:
        r = requests.get(f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest", timeout=5)
        if r.status_code != 200:
            return
        latest = r.json().get("tag_name", "").lstrip("v")
        if latest and latest != VERSION:
            print(f"\n  [!] Update available: v{latest} (you have v{VERSION})")
            print(f"  --> https://github.com/{GITHUB_REPO}/releases/latest")
            input("\n  Press Enter to continue anyway... ")
    except Exception:
        pass

def menu():
    print(banner)
    check_version()
    print(" [1] Start Questify")
    print(" [2] Star the Repo")
    print(" [3] Exit")
    choice = input("> ")
    if choice == "1":
        start_questify()
    elif choice == "2":
        webbrowser.open_new_tab(f"https://github.com/{GITHUB_REPO}")
    elif choice == "3":
        sys.exit(0)

def start_questify():
    names = []
    for app in gamelist:
        if app["name"]:
            names.append(app["name"])

    while True:
        gselect = input("Select game (0 to go back): ").strip().lower()

        if gselect == "0":
            return

        q = gselect
        exact   = [n for n in names if n.lower() == q]
        starts  = [n for n in names if n.lower().startswith(q) and n not in exact]
        contains = [n for n in names if q in n.lower() and n not in exact and n not in starts]
        rest    = [n for n in names if n not in exact and n not in starts and n not in contains]
        fuzzy   = difflib.get_close_matches(q, rest, n=10, cutoff=0.45)
        matches = (exact + starts + contains + fuzzy)[:15]

        if len(matches) == 0:
            print("No matches.")
            continue

        i = 1
        for name in matches:
            print(f"[{i}] --> {name}")
            i = i + 1

        sel_raw = input("Select number (0 to search again): ")

        if not sel_raw.isdigit():
            print("Invalid.")
            continue

        sel = int(sel_raw)

        if sel == 0:
            continue

        if sel > len(matches):
            print("Invalid.")
            continue

        selected_name = matches[sel - 1]
        print("Selected:", selected_name)

        exename = None
        for app in gamelist:
            if app["name"] == selected_name:
                for exe in app["executables"]:
                    if exe["os"] == "win32" and exe["is_launcher"] == False:
                        exename = exe["name"]
                        break

        if exename is None:
            print("No Windows executable found.")
            continue

        safe_name = re.sub(r'[<>:"/\\|?*]', '', selected_name).strip()
        parts = exename.split("/")
        exe_file = parts[-1]

        slot = 0
        base = get_slot_path(slot)
        folder = build_game_folder(base, safe_name, parts)

        os.makedirs(folder, exist_ok=True)
        dst = os.path.join(folder, exe_file)
        if os.path.exists(dst):
            try:
                os.remove(dst)
            except PermissionError:
                shutil.rmtree(os.path.dirname(dst), ignore_errors=True)
                os.makedirs(folder, exist_ok=True)
        shutil.copy(SELF_PATH, dst)

        save_state(base, dst, safe_name, parts, exe_file, slot)

        print(f"\nInstalled to: {dst}")
        print("Launching and closing this window...")

        subprocess.Popen([dst], creationflags=subprocess.CREATE_NEW_CONSOLE)
        time.sleep(0.5)
        sys.exit(0)

def timer_with_reset():
    total = 15 * 60 + 30
    reset_flag = [False]

    def key_listener():
        while True:
            if msvcrt.kbhit():
                key = msvcrt.getch()
                if key == b'7':
                    reset_flag[0] = True
                    return

    listener = threading.Thread(target=key_listener, daemon=True)
    listener.start()

    print("\n  Press 7 to reset (close, move, relaunch)\n")

    while total > 0:
        if reset_flag[0]:
            do_reset()
            return

        m = total // 60
        s = total % 60
        print(f"\rTime left: {m:02d}:{s:02d}  [Press 7 to reset]", end="", flush=True)
        time.sleep(1)
        total = total - 1

    print("\rTime left: 00:00                        ")
    sys.exit(0)

def do_reset():
    state = load_state()
    if state is None:
        print("\nNo state found, can't reset.")
        return

    old_base = state["folder"]
    safe_name = state["safe_name"]
    parts = state["parts"]
    exe_file = state["exe_file"]
    old_slot = state.get("slot", 0)

    new_slot = (old_slot + 1) % 10
    new_base = get_slot_path(new_slot)

    new_folder = build_game_folder(new_base, safe_name, parts)
    os.makedirs(new_folder, exist_ok=True)
    new_exe = os.path.join(new_folder, exe_file)

    if os.path.exists(new_exe):
        try:
            os.remove(new_exe)
        except PermissionError:
            shutil.rmtree(os.path.dirname(new_exe), ignore_errors=True)
            os.makedirs(new_folder, exist_ok=True)
    shutil.copy(SELF_PATH, new_exe)
    save_state(new_base, new_exe, safe_name, parts, exe_file, new_slot)

    cleanup_path = os.path.join(new_folder, "questify_cleanup.txt")
    with open(cleanup_path, "w") as f:
        f.write(old_base)

    print(f"\n\nResetting to: {new_exe}")
    print("Closing...")

    subprocess.Popen([new_exe], creationflags=subprocess.CREATE_NEW_CONSOLE)
    time.sleep(0.5)
    sys.exit(0)

def deployed_mode():
    cleanup_previous()
    print(banner)
    print(f"  Running as: {SELF_NAME}")
    print(f"  Location:   {SELF_DIR}\n")
    timer_with_reset()

banner = r"""
                              __           ___
                             /\ \__  __  /'___\
   __   __  __     __    ____\ \ ,_\/\_\/\ \__/  __  __
 /'__`\/\ \/\ \  /'__`\ /',__\\ \ \/\/\ \ \ ,__\/\ \/\ \
/\ \L\ \ \ \_\ \/\  __//\__, `\\ \ \_\ \ \ \ \_/\ \ \_\ \
\ \___, \ \____/\ \____\/\____/ \ \__\\ \_\ \_\  \/`____ \
 \/___/\ \/___/  \/____/\/___/   \/__/ \/_/\/_/   `/___/> \
      \ \_\                                          /\___/
       \/_/                                          \/__/
                     >> github.com/orqz <<
"""

is_launcher = SELF_NAME == "questify.exe"

if is_launcher:
    menu()
else:
    deployed_mode()
