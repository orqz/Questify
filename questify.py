import os
import sys
import shutil
import time
import re
import random
import string
import subprocess
import requests
import webbrowser
import difflib
import threading
import msvcrt
import json
import tempfile

VERSION = "4.0"
GITHUB_REPO = "orqz/questify"

url = "https://discord.com/api/applications/detectable"
gamelist = requests.get(url).json()

SELF_PATH = os.path.abspath(sys.argv[0])
SELF_DIR = os.path.dirname(SELF_PATH)
SELF_NAME = os.path.basename(SELF_PATH).lower()
STATE_FILE = os.path.join(SELF_DIR, ".questify_state")

def random_folder_name():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))

def get_random_base_path():
    bases = [
        os.path.join(os.environ.get("APPDATA", "C:\\Users"), random_folder_name()),
        os.path.join(os.environ.get("LOCALAPPDATA", "C:\\Users"), random_folder_name()),
        os.path.join(os.path.expanduser("~"), "Documents", random_folder_name()),
        os.path.join(os.path.expanduser("~"), random_folder_name()),
    ]
    return random.choice(bases)

def save_state(base_folder, exe_path, safe_name, parts, exe_file):
    data = {
        "folder": base_folder,
        "exe_path": exe_path,
        "safe_name": safe_name,
        "parts": parts,
        "exe_file": exe_file,
        "launcher": SELF_PATH,
    }
    state_path = os.path.join(os.path.dirname(exe_path), ".questify_state")
    with open(state_path, "w") as f:
        json.dump(data, f)

def load_state():
    state_path = os.path.join(SELF_DIR, ".questify_state")
    if os.path.exists(state_path):
        with open(state_path, "r") as f:
            return json.load(f)
    return None

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
    print(" [2] Discord Server")
    print(" [3] Exit")
    choice = input("> ")
    if choice == "1":
        start_questify()
    elif choice == "2":
        webbrowser.open_new_tab("https://discord.gg/vRFXc3pvt4")
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

        rand_base = get_random_base_path()
        folder = os.path.join(rand_base, safe_name)
        index = 0
        while index < len(parts) - 1:
            folder = os.path.join(folder, parts[index])
            index = index + 1

        os.makedirs(folder, exist_ok=True)
        dst = os.path.join(folder, exe_file)
        shutil.copy(SELF_PATH, dst)

        save_state(rand_base, dst, safe_name, parts, exe_file)

        print(f"\nInstalled to: {dst}")
        print("Launching and closing this window...")

        subprocess.Popen(
            [dst],
            creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
        )
        time.sleep(0.5)
        os._exit(0)

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

    new_base = get_random_base_path()
    while new_base == old_base:
        new_base = get_random_base_path()

    new_folder = os.path.join(new_base, safe_name)
    index = 0
    while index < len(parts) - 1:
        new_folder = os.path.join(new_folder, parts[index])
        index = index + 1

    new_exe = os.path.join(new_folder, exe_file)

    new_state = json.dumps({
        "folder": new_base,
        "exe_path": new_exe,
        "safe_name": safe_name,
        "parts": parts,
        "exe_file": exe_file,
        "launcher": state.get("launcher", SELF_PATH),
    })

    bat_path = os.path.join(tempfile.gettempdir(), f"qr_{random_folder_name()}.bat")

    bat_content = f'''@echo off
title Questify Reset
ping 127.0.0.1 -n 3 > nul
mkdir "{new_folder}"
copy /Y "{SELF_PATH}" "{new_exe}" > nul
echo {new_state.replace('"', '^^^"')} > "{os.path.join(new_folder, '.questify_state')}"
rmdir /S /Q "{old_base}" 2>nul
start "" "{new_exe}"
del "%~f0"
'''

    with open(bat_path, "w") as f:
        f.write(bat_content)

    print(f"\n\nResetting to: {new_exe}")
    print("Closing...")

    subprocess.Popen(
        ["cmd", "/c", bat_path],
        creationflags=subprocess.CREATE_NO_WINDOW
    )

    os._exit(0)

def deployed_mode():
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
