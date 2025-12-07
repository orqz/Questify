import os
import shutil
import time
import subprocess
import webbrowser
import sys

games = {
    "1": "Fortnite",
    "2": "PUBG",
    "3": "Destiny 2",
    "4": "Storm-Lancers",
    "5": "Where Winds Meet",
    "6": "Fallout-76",
    "7" : "Terminull Brigade"
}

game_exe_name = {
    "Fortnite": "FortniteClient-Win64-Shipping",
    "PUBG": "TslGame",
    "Destiny 2": "destiny2",
    "Storm-Lancers": "StormLancersDemo",
    "Where Winds Meet": "wwm",
    "Fallout-76": "Fallout76",
    "Terminull Brigade" : "Rouge-Win64-Shipping"
}



print("""
   ___                  _   _  __       
  / _ \\ _   _  ___  ___| |_(_)/ _|_   _ 
 | | | | | | |/ _ \\/ __| __| | |_| | | |
 | |_| | |_| |  __/\\__ \\ |_| |  _| |_| |
  \\__\\_\\\\__,_|\\___||___/\\__|_|_|  \\__, |
                                  |___/
""")

print("            QUESTIFY\n")


print("1) Fortnite        | 2) PUBG        | 3) Destiny 2")
print("4) Storm-Lancers   | 5) Where Winds Meet | 6) Fallout-76")
print ("7) Terminull Brigade  |")

selection = input("\nSelect a game: ")


if selection in games:
    game_name = games[selection]
    exe_name = game_exe_name[game_name]
    print(f"You selected: {game_name}")
    print(f"Game EXE is {exe_name}")
    base_path = os.path.dirname(os.path.abspath(__file__))
    print(f"Launcher folder: {base_path}")
    win64_folder = os.path.join(base_path, "win64")
    os.makedirs(win64_folder, exist_ok=True)
    print(f"Created win64 folder at: {win64_folder}")

    timer_code = f"""
import tkinter as tk
import time


total_seconds = 16 * 60


root = tk.Tk()
root.title("{exe_name} Timer") 
root.geometry("400x150")
root.resizable(False, False)


label1 = tk.Label(root, text="Questify has started :)", font=("Arial", 16))
label1.pack(pady=10)

label2 = tk.Label(root, text="", font=("Arial", 14))
label2.pack()


def countdown(seconds):
    if seconds >= 0:
        mins, secs = divmod(seconds, 60)
        label2.config(text=f"Time remaining {{mins:02d}}:{{secs:02d}}")
        root.after(1000, countdown, seconds-1)
    else:
        root.destroy()  # Close window when time is up


countdown(total_seconds)
root.mainloop()
"""

    timer_script_path = os.path.join(win64_folder, f"{exe_name}.py")
    print(f"Timer script will be created at: {timer_script_path}")
    with open(timer_script_path, "w") as f:
        f.write(timer_code)
    print(f"Timer script written at: {timer_script_path}")

    subprocess.run([
        "python", "-m", "PyInstaller",
        "--onefile",
        "--noconsole",
        "--name", exe_name,
        timer_script_path
    ], cwd=win64_folder)

    exe_path = os.path.join(win64_folder, "dist", f"{exe_name}.exe")
    subprocess.Popen([exe_path], cwd=win64_folder)
    print(f"Timer EXE launched: {exe_name}")
    os.remove(timer_script_path)  
    shutil.rmtree(os.path.join(win64_folder, "build"), ignore_errors=True)
    shutil.rmtree(os.path.join(win64_folder, f"{exe_name}.spec"), ignore_errors=True)


    
else:
    print("Invalid selection!")


