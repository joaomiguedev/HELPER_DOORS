import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import json
import os
import sys
import subprocess

# =========================================================
# DOORS INVESTIGATION TERMINAL
# Manual companion / investigation tool
# =========================================================


root = tk.Tk()
root.title("DOORS • Investigation Terminal")
root.geometry("1120x850")
root.minsize(1000, 720)
root.configure(bg="#10141c")


# =========================================================
# COLORS
# =========================================================

BG = "#10141c"
HEADER = "#171d28"
PANEL = "#181e29"
PANEL_LIGHT = "#202735"
WHITE = "#f1f5f9"
MUTED = "#8b97a8"

BLUE = "#5865F2"
BLUE_HOVER = "#4752c4"

GREEN = "#3ddc97"
RED = "#ff5c5c"
ORANGE = "#ffad42"
YELLOW = "#f5d76e"
CYAN = "#54d9ff"

BORDER = "#303949"
DARK = "#0c1017"


# =========================================================
# DATA
# =========================================================

current_room = 0
round_number = 0
round_active = False
danger_score = 0

selected_area = "Hotel"

rooms = []
entity_events = []
items = []
observations = []
timeline = []


# =========================================================
# DATA OPTIONS
# =========================================================

AREAS = [
    "Hotel",
    "Rooms",
    "The Mines",
    "Backdoor",
    "Retro Mode",
    "Unknown"
]


ENTITIES = [
    "None",
    "Rush",
    "Ambush",
    "Screech",
    "Eyes",
    "Seek",
    "Figure",
    "Halt",
    "Dupe",
    "Dread",
    "Timothy",
    "Jack",
    "Void",
    "Snare",
    "Other"
]


ITEMS = [
    "None",
    "Flashlight",
    "Lighter",
    "Vitamins",
    "Lockpick",
    "Skeleton Key",
    "Crucifix",
    "Bandage",
    "Glowsticks",
    "Battery",
    "Other"
]


ENTITY_DANGER = {
    "Rush": 5,
    "Ambush": 7,
    "Screech": 2,
    "Eyes": 2,
    "Seek": 5,
    "Figure": 6,
    "Halt": 4,
    "Dupe": 3,
    "Dread": 5,
    "Timothy": 1,
    "Jack": 1,
    "Void": 2,
    "Snare": 3,
    "Other": 2
}


# =========================================================
# HELPERS
# =========================================================

def timestamp():
    return datetime.now().strftime("%H:%M:%S")

def danger_color():
    if danger_score >= 15:
        return RED

    if danger_score >= 8:
        return ORANGE

    if danger_score >= 3:
        return YELLOW

    return GREEN


def update_status():

    room_status.config(
        text=f"●  Current door: {current_room}"
    )

    danger_status.config(
        text=f"⚠  Danger: {danger_score}",
        fg=danger_color()
    )


def add_timeline(event):

    timeline.append({
        "time": timestamp(),
        "room": current_room,
        "area": selected_area,
        "event": event
    })

    update_timeline()


# =========================================================
# CHRONIX TIME RECORDER
# =========================================================

def open_chronix():

    # Look for chronix.py in the same folder as doors.py
    chronix_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "chronix_part_api.py"
    )

    if not os.path.exists(chronix_path):
        messagebox.showerror(
            "Chronix Not Found",
            "chronix.py was not found.\n\n"
            "Put chronix.py in the same folder as doors.py."
        )
        return

    try:
        # Start Chronix as a completely separate Python process.
        subprocess.Popen(
            [sys.executable, chronix_path],
            cwd=os.path.dirname(chronix_path)
        )

    except Exception as error:
        messagebox.showerror(
            "Chronix Error",
            f"Could not open Chronix.\n\n{error}"
        )


# =========================================================
# ROUND SYSTEM
# =========================================================

def start_round():

    global round_active
    global round_number

    if round_active:
        messagebox.showinfo(
            "Round Active",
            "A round is already active."
        )
        return

    round_number += 1
    round_active = True

    clear_data()

    round_status.config(
        text=f"●  ROUND {round_number} ACTIVE",
        fg=GREEN
    )

    add_timeline(
        f"Started round {round_number}."
    )

    update_status()


def end_round():

    global round_active

    if not round_active:
        messagebox.showinfo(
            "No Round",
            "There is no active round."
        )
        return

    round_active = False

    round_status.config(
        text=f"●  ROUND {round_number} ENDED",
        fg=RED
    )

    add_timeline(
        f"Ended round {round_number}."
    )

    generate_report()


# =========================================================
# ROOM TRACKER
# =========================================================

def next_room():

    global current_room

    if not round_active:
        messagebox.showwarning(
            "Start Round",
            "Start a round before tracking rooms."
        )
        return

    current_room += 1

    rooms.append({
        "room": current_room,
        "time": timestamp(),
        "area": selected_area
    })

    add_timeline(
        f"Entered Door {current_room}."
    )

    update_status()


def previous_room():

    global current_room

    if current_room <= 0:
        return

    current_room -= 1

    add_timeline(
        f"Moved back to Door {current_room}."
    )

    update_status()


def set_room():

    global current_room

    value = room_entry.get().strip()

    try:
        number = int(value)

        if number < 0:
            raise ValueError

        current_room = number

        rooms.append({
            "room": current_room,
            "time": timestamp(),
            "area": selected_area
        })

        add_timeline(
            f"Room manually changed to Door {current_room}."
        )

        update_status()

    except ValueError:

        messagebox.showwarning(
            "Invalid Room",
            "Enter a valid positive room number."
        )


# =========================================================
# AREA
# =========================================================

def area_changed(event=None):

    global selected_area

    selected_area = area_combo.get()

    area_status.config(
        text=f"●  Area: {selected_area}",
        fg=GREEN
    )

    add_timeline(
        f"Area changed to {selected_area}."
    )


# =========================================================
# ENTITY TRACKER
# =========================================================

def record_entity():

    global danger_score

    entity = entity_combo.get()

    if not entity or entity == "None":

        messagebox.showwarning(
            "Entity",
            "Select an entity first."
        )

        return

    added_danger = ENTITY_DANGER.get(
        entity,
        1
    )

    danger_score += added_danger

    event = {
        "time": timestamp(),
        "room": current_room,
        "area": selected_area,
        "entity": entity,
        "danger": added_danger
    }

    entity_events.append(event)

    add_timeline(
        f"Recorded {entity} (+{added_danger} danger)."
    )

    update_entity_log()
    update_status()

    entity_status.config(
        text=f"●  Recorded: {entity}",
        fg=GREEN
    )


def reset_danger():

    global danger_score

    danger_score = 0

    danger_status.config(
        text="⚠  Danger: 0",
        fg=GREEN
    )

    add_timeline(
        "Danger level reset manually."
    )


# =========================================================
# ITEM TRACKER
# =========================================================

def record_item():

    item = item_combo.get()
    note = item_note.get().strip()

    # Remove placeholder text
    if note == "Optional item note...":
        note = ""

    if not item or item == "None":

        messagebox.showwarning(
            "Item",
            "Select an item first."
        )

        return

    data = {
        "time": timestamp(),
        "room": current_room,
        "area": selected_area,
        "item": item,
        "note": note
    }

    items.append(data)

    extra = f" — {note}" if note else ""

    add_timeline(
        f"Found {item}{extra}."
    )

    update_item_log()

    item_status.config(
        text=f"●  Recorded: {item}",
        fg=GREEN
    )

    item_note.delete(
        0,
        tk.END
    )


# =========================================================
# OBSERVATIONS
# =========================================================

def record_observation():

    text = observation_entry.get().strip()

    if text == "Example: Heard a loud sound...":
        text = ""

    if not text:

        messagebox.showwarning(
            "Observation",
            "Enter an observation first."
        )

        return

    data = {
        "time": timestamp(),
        "room": current_room,
        "area": selected_area,
        "text": text
    }

    observations.append(data)

    add_timeline(
        f"Observation: {text}"
    )

    update_observation_log()

    observation_entry.delete(
        0,
        tk.END
    )

    observation_status.config(
        text="●  Observation recorded",
        fg=GREEN
    )


# =========================================================
# TIMELINE
# =========================================================

def update_timeline():

    timeline_list.delete(
        0,
        tk.END
    )

    for event in timeline:

        timeline_list.insert(
            tk.END,
            f"[{event['time']}] "
            f"Door {event['room']} • "
            f"{event['event']}"
        )


def update_entity_log():

    entity_list.delete(
        0,
        tk.END
    )

    for event in entity_events:

        entity_list.insert(
            tk.END,
            f"[{event['time']}] "
            f"Door {event['room']} • "
            f"{event['entity']} "
            f"(+{event['danger']})"
        )


def update_item_log():

    item_list.delete(
        0,
        tk.END
    )

    for item in items:

        line = (
            f"[{item['time']}] "
            f"Door {item['room']} • "
            f"{item['item']}"
        )

        if item["note"]:
            line += f" • {item['note']}"

        item_list.insert(
            tk.END,
            line
        )


def update_observation_log():

    observation_list.delete(
        0,
        tk.END
    )

    for observation in observations:

        observation_list.insert(
            tk.END,
            f"[{observation['time']}] "
            f"Door {observation['room']} • "
            f"{observation['text']}"
        )


# =========================================================
# REPORT
# =========================================================

def generate_report():

    report = []

    report.append(
        "=============================================="
    )

    report.append(
        "             DOORS INVESTIGATION"
    )

    report.append(
        "=============================================="
    )

    report.append("")

    report.append(
        f"Round: {round_number}"
    )

    report.append(
        f"Current Door: {current_room}"
    )

    report.append(
        f"Area: {selected_area}"
    )

    report.append(
        f"Danger Score: {danger_score}"
    )

    report.append("")

    report.append(
        "ENTITY EVENTS"
    )

    report.append(
        "----------------------------------------------"
    )

    if entity_events:

        for event in entity_events:

            report.append(
                f"[{event['time']}] "
                f"Door {event['room']} - "
                f"{event['entity']} "
                f"(+{event['danger']})"
            )

    else:

        report.append(
            "No entities recorded."
        )

    report.append("")

    report.append(
        "ITEMS"
    )

    report.append(
        "----------------------------------------------"
    )

    if items:

        for item in items:

            line = (
                f"[{item['time']}] "
                f"Door {item['room']} - "
                f"{item['item']}"
            )

            if item["note"]:
                line += f" - {item['note']}"

            report.append(line)

    else:

        report.append(
            "No items recorded."
        )

    report.append("")

    report.append(
        "OBSERVATIONS"
    )

    report.append(
        "----------------------------------------------"
    )

    if observations:

        for observation in observations:

            report.append(
                f"[{observation['time']}] "
                f"Door {observation['room']} - "
                f"{observation['text']}"
            )

    else:

        report.append(
            "No observations recorded."
        )

    report.append("")

    report.append(
        "TIMELINE"
    )

    report.append(
        "----------------------------------------------"
    )

    if timeline:

        for event in timeline:

            report.append(
                f"[{event['time']}] "
                f"Door {event['room']} - "
                f"{event['event']}"
            )

    else:

        report.append(
            "No timeline events."
        )

    report.append("")

    report.append(
        "This is a manual evidence organizer."
    )

    report.append(
        "It does not automatically control or read Roblox."
    )

    show_report(
        "\n".join(report)
    )


def show_report(report):

    window = tk.Toplevel(root)

    window.title(
        "DOORS • Investigation Report"
    )

    window.geometry(
        "780x650"
    )

    window.configure(
        bg=BG
    )

    header = tk.Frame(
        window,
        bg=HEADER,
        height=75
    )

    header.pack(
        fill="x"
    )

    tk.Label(
        header,
        text="📋  INVESTIGATION REPORT",
        font=("Segoe UI", 19, "bold"),
        fg=WHITE,
        bg=HEADER
    ).pack(
        pady=(17, 2)
    )

    tk.Label(
        header,
        text="Recorded evidence and timeline",
        font=("Segoe UI", 9),
        fg=MUTED,
        bg=HEADER
    ).pack()

    text = tk.Text(
        window,
        bg=DARK,
        fg=WHITE,
        insertbackground=WHITE,
        font=("Consolas", 10),
        relief="flat",
        wrap="word"
    )

    text.pack(
        fill="both",
        expand=True,
        padx=18,
        pady=18
    )

    text.insert(
        "1.0",
        report
    )

    text.config(
        state="disabled"
    )


# =========================================================
# SAVE
# =========================================================

def save_session():

    filename = filedialog.asksaveasfilename(
        title="Save DOORS Investigation",
        defaultextension=".json",
        filetypes=[
            ("DOORS Session", "*.json"),
            ("All Files", "*.*")
        ]
    )

    if not filename:
        return

    data = {
        "round_number": round_number,
        "current_room": current_room,
        "round_active": round_active,
        "danger_score": danger_score,
        "selected_area": selected_area,
        "rooms": rooms,
        "entity_events": entity_events,
        "items": items,
        "observations": observations,
        "timeline": timeline
    }

    try:

        with open(
            filename,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                data,
                file,
                indent=4
            )

        save_status.config(
            text="●  Session saved",
            fg=GREEN
        )

    except Exception as error:

        messagebox.showerror(
            "Save Error",
            str(error)
        )


# =========================================================
# LOAD
# =========================================================

def load_session():

    global round_number
    global current_room
    global round_active
    global danger_score
    global selected_area
    global rooms
    global entity_events
    global items
    global observations
    global timeline

    filename = filedialog.askopenfilename(
        title="Load DOORS Investigation",
        filetypes=[
            ("DOORS Session", "*.json"),
            ("All Files", "*.*")
        ]
    )

    if not filename:
        return

    try:

        with open(
            filename,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

        round_number = data.get(
            "round_number",
            0
        )

        current_room = data.get(
            "current_room",
            0
        )

        round_active = data.get(
            "round_active",
            False
        )

        danger_score = data.get(
            "danger_score",
            0
        )

        selected_area = data.get(
            "selected_area",
            "Hotel"
        )

        rooms = data.get(
            "rooms",
            []
        )

        entity_events = data.get(
            "entity_events",
            []
        )

        items = data.get(
            "items",
            []
        )

        observations = data.get(
            "observations",
            []
        )

        timeline = data.get(
            "timeline",
            []
        )

        area_combo.set(
            selected_area
        )

        update_all_logs()
        update_status()

        if round_active:

            round_status.config(
                text=f"●  ROUND {round_number} ACTIVE",
                fg=GREEN
            )

        else:

            round_status.config(
                text=f"●  ROUND {round_number} LOADED",
                fg=MUTED
            )

        load_status.config(
            text="●  Session loaded",
            fg=GREEN
        )

    except Exception as error:

        messagebox.showerror(
            "Load Error",
            str(error)
        )


# =========================================================
# CLEAR
# =========================================================

def clear_data():

    global current_room
    global danger_score

    rooms.clear()
    entity_events.clear()
    items.clear()
    observations.clear()
    timeline.clear()

    current_room = 0
    danger_score = 0

    update_all_logs()
    update_status()


def reset_everything():

    global round_number
    global round_active
    global selected_area

    answer = messagebox.askyesno(
        "Reset Everything",
        "Are you sure you want to delete all investigation data?"
    )

    if not answer:
        return

    clear_data()

    round_number = 0
    round_active = False
    selected_area = "Hotel"

    area_combo.set(
        "Hotel"
    )

    round_status.config(
        text="●  NO ACTIVE ROUND",
        fg=MUTED
    )

    entity_status.config(
        text="●  Waiting for entity...",
        fg=MUTED
    )

    item_status.config(
        text="●  Waiting for item...",
        fg=MUTED
    )

    observation_status.config(
        text="●  Waiting for observation...",
        fg=MUTED
    )


def update_all_logs():

    update_timeline()
    update_entity_log()
    update_item_log()
    update_observation_log()


# =========================================================
# HELP
# =========================================================

def show_help():

    window = tk.Toplevel(root)

    window.title(
        "DOORS • Help"
    )

    window.geometry(
        "700x700"
    )

    window.configure(
        bg=BG
    )

    header = tk.Frame(
        window,
        bg=HEADER,
        height=90
    )

    header.pack(
        fill="x"
    )

    tk.Label(
        header,
        text="💡  DOORS INVESTIGATION",
        font=("Segoe UI", 21, "bold"),
        fg=WHITE,
        bg=HEADER
    ).pack(
        pady=(18, 2)
    )

    tk.Label(
        header,
        text="How to use the companion",
        font=("Segoe UI", 10),
        fg=MUTED,
        bg=HEADER
    ).pack()

    help_text = """
STARTING A ROUND
────────────────────────────────────────

Press START ROUND before recording evidence.

TIME RECORD
────────────────────────────────────────

Press TIME RECORD to open the Chronix timer.

chronix.py must be in the same folder as
doors.py.

Chronix runs in its own separate window.

ROOM TRACKER
────────────────────────────────────────

NEXT DOOR increases your current door number.

PREVIOUS moves the counter backwards.

You can also type a room number and press SET.

AREA
────────────────────────────────────────

Select the area you are currently investigating.

ENTITY TRACKER
────────────────────────────────────────

Record entities you encounter.

The danger number is only an organizational
score based on the entity you entered.

ITEM TRACKER
────────────────────────────────────────

Record items and optionally add a note.

OBSERVATIONS
────────────────────────────────────────

Record anything you notice.

TIMELINE
────────────────────────────────────────

Every action receives a timestamp and door number.

SAVE / LOAD
────────────────────────────────────────

Save your investigation as a JSON file.

You can load it again later.

REPORT
────────────────────────────────────────

Creates a readable investigation report.

IMPORTANT
────────────────────────────────────────

This program is a manual companion.

It does not read Roblox memory,
inject into Roblox, or automatically
control the game.
"""

    text = tk.Text(
        window,
        bg=DARK,
        fg=WHITE,
        font=("Segoe UI", 10),
        relief="flat",
        wrap="word"
    )

    text.pack(
        fill="both",
        expand=True,
        padx=18,
        pady=18
    )

    text.insert(
        "1.0",
        help_text
    )

    text.config(
        state="disabled"
    )


# =========================================================
# STYLE
# =========================================================

style = ttk.Style()

style.theme_use(
    "clam"
)


style.configure(
    "Modern.TCombobox",
    fieldbackground=PANEL_LIGHT,
    background=PANEL_LIGHT,
    foreground=WHITE,
    arrowcolor=BLUE,
    bordercolor=BORDER,
    lightcolor=BORDER,
    darkcolor=BORDER,
    padding=9,
    font=("Segoe UI", 10)
)

style.map(
    "Modern.TCombobox",
    fieldbackground=[
        ("readonly", PANEL_LIGHT)
    ],
    foreground=[
        ("readonly", WHITE)
    ]
)


style.configure(
    "Primary.TButton",
    font=("Segoe UI", 10, "bold"),
    foreground="white",
    background=BLUE,
    borderwidth=0,
    padding=(18, 11)
)

style.map(
    "Primary.TButton",
    background=[
        ("active", BLUE_HOVER),
        ("pressed", "#3c45a5")
    ]
)


# =========================================================
# HEADER
# =========================================================

header = tk.Frame(
    root,
    bg=HEADER,
    height=105
)

header.pack(
    fill="x"
)

tk.Label(
    header,
    text="🚪  DOORS INVESTIGATION",
    font=("Segoe UI", 24, "bold"),
    fg=WHITE,
    bg=HEADER
).pack(
    pady=(18, 2)
)

tk.Label(
    header,
    text="ROOMS  •  ENTITIES  •  ITEMS  •  TIMELINE  •  EVIDENCE",
    font=("Segoe UI", 10),
    fg=MUTED,
    bg=HEADER
).pack()


# =========================================================
# TOP CONTROLS
# =========================================================

controls = tk.Frame(
    root,
    bg=BG
)

controls.pack(
    fill="x",
    padx=25,
    pady=15
)


tk.Button(
    controls,
    text="▶  START ROUND",
    command=start_round,
    font=("Segoe UI", 10, "bold"),
    fg=WHITE,
    bg=BLUE,
    activeforeground=WHITE,
    activebackground=BLUE_HOVER,
    relief="flat",
    padx=15,
    pady=9,
    cursor="hand2"
).pack(
    side="left",
    padx=4
)


tk.Button(
    controls,
    text="■  END ROUND",
    command=end_round,
    font=("Segoe UI", 10, "bold"),
    fg=WHITE,
    bg="#8e3d48",
    activeforeground=WHITE,
    activebackground="#a94a57",
    relief="flat",
    padx=15,
    pady=9,
    cursor="hand2"
).pack(
    side="left",
    padx=4
)


# =========================================================
# TIME RECORD BUTTON
# =========================================================

tk.Button(
    controls,
    text="⏱  TIME RECORD",
    command=open_chronix,
    font=("Segoe UI", 10, "bold"),
    fg=WHITE,
    bg="#168a62",
    activeforeground=WHITE,
    activebackground="#20a875",
    relief="flat",
    padx=15,
    pady=9,
    cursor="hand2"
).pack(
    side="left",
    padx=4
)


tk.Button(
    controls,
    text="💾  SAVE",
    command=save_session,
    font=("Segoe UI", 10, "bold"),
    fg=MUTED,
    bg=PANEL_LIGHT,
    activeforeground=WHITE,
    activebackground=BORDER,
    relief="flat",
    padx=15,
    pady=9,
    cursor="hand2"
).pack(
    side="left",
    padx=4
)


tk.Button(
    controls,
    text="📂  LOAD",
    command=load_session,
    font=("Segoe UI", 10, "bold"),
    fg=MUTED,
    bg=PANEL_LIGHT,
    activeforeground=WHITE,
    activebackground=BORDER,
    relief="flat",
    padx=15,
    pady=9,
    cursor="hand2"
).pack(
    side="left",
    padx=4
)


tk.Button(
    controls,
    text="📋  REPORT",
    command=generate_report,
    font=("Segoe UI", 10, "bold"),
    fg=MUTED,
    bg=PANEL_LIGHT,
    activeforeground=WHITE,
    activebackground=BORDER,
    relief="flat",
    padx=15,
    pady=9,
    cursor="hand2"
).pack(
    side="left",
    padx=4
)


tk.Button(
    controls,
    text="💡  HELP",
    command=show_help,
    font=("Segoe UI", 10, "bold"),
    fg=MUTED,
    bg=PANEL_LIGHT,
    activeforeground=WHITE,
    activebackground=BORDER,
    relief="flat",
    padx=15,
    pady=9,
    cursor="hand2"
).pack(
    side="left",
    padx=4
)


round_status = tk.Label(
    controls,
    text="●  NO ACTIVE ROUND",
    font=("Segoe UI", 10, "bold"),
    fg=MUTED,
    bg=BG
)

round_status.pack(
    side="right",
    padx=10
)


# =========================================================
# MAIN
# =========================================================

main = tk.Frame(
    root,
    bg=BG
)

main.pack(
    fill="both",
    expand=True,
    padx=25
)


left = tk.Frame(
    main,
    bg=BG
)

left.pack(
    side="left",
    fill="both",
    expand=True,
    padx=(0, 8)
)


right = tk.Frame(
    main,
    bg=BG
)

right.pack(
    side="right",
    fill="both",
    expand=True,
    padx=(8, 0)
)


# =========================================================
# ROOM PANEL
# =========================================================

room_panel = tk.Frame(
    left,
    bg=PANEL,
    highlightbackground=BORDER,
    highlightthickness=1
)

room_panel.pack(
    fill="x",
    pady=5
)


tk.Label(
    room_panel,
    text="🚪  ROOM TRACKER",
    font=("Segoe UI", 11, "bold"),
    fg=WHITE,
    bg=PANEL
).pack(
    anchor="w",
    padx=18,
    pady=(12, 6)
)


room_controls = tk.Frame(
    room_panel,
    bg=PANEL
)

room_controls.pack(
    fill="x",
    padx=18,
    pady=(0, 12)
)


tk.Button(
    room_controls,
    text="◀",
    command=previous_room,
    font=("Segoe UI", 10, "bold"),
    fg=MUTED,
    bg=PANEL_LIGHT,
    activeforeground=WHITE,
    activebackground=BORDER,
    relief="flat",
    width=4,
    cursor="hand2"
).pack(
    side="left",
    padx=(0, 5)
)


tk.Button(
    room_controls,
    text="NEXT DOOR ▶",
    command=next_room,
    font=("Segoe UI", 10, "bold"),
    fg=WHITE,
    bg=BLUE,
    activeforeground=WHITE,
    activebackground=BLUE_HOVER,
    relief="flat",
    padx=12,
    pady=7,
    cursor="hand2"
).pack(
    side="left",
    padx=5
)


room_entry = tk.Entry(
    room_controls,
    bg=PANEL_LIGHT,
    fg=WHITE,
    insertbackground=WHITE,
    relief="flat",
    width=8,
    font=("Segoe UI", 10)
)

room_entry.pack(
    side="left",
    padx=(12, 4),
    ipady=6
)


tk.Button(
    room_controls,
    text="SET",
    command=set_room,
    font=("Segoe UI", 9, "bold"),
    fg=MUTED,
    bg=PANEL_LIGHT,
    activeforeground=WHITE,
    activebackground=BORDER,
    relief="flat",
    padx=10,
    pady=7,
    cursor="hand2"
).pack(
    side="left"
)


room_status = tk.Label(
    room_controls,
    text="●  Current door: 0",
    font=("Segoe UI", 9, "bold"),
    fg=MUTED,
    bg=PANEL
)

room_status.pack(
    side="right"
)


# =========================================================
# AREA PANEL
# =========================================================

area_panel = tk.Frame(
    left,
    bg=PANEL,
    highlightbackground=BORDER,
    highlightthickness=1
)

area_panel.pack(
    fill="x",
    pady=5
)


tk.Label(
    area_panel,
    text="🗺️  AREA",
    font=("Segoe UI", 11, "bold"),
    fg=WHITE,
    bg=PANEL
).pack(
    anchor="w",
    padx=18,
    pady=(12, 6)
)


area_combo = ttk.Combobox(
    area_panel,
    values=AREAS,
    state="readonly",
    style="Modern.TCombobox",
    width=30
)

area_combo.set(
    "Hotel"
)

area_combo.pack(
    side="left",
    padx=(18, 10),
    pady=(0, 12)
)

area_combo.bind(
    "<<ComboboxSelected>>",
    area_changed
)


area_status = tk.Label(
    area_panel,
    text="●  Area: Hotel",
    font=("Segoe UI", 9),
    fg=MUTED,
    bg=PANEL
)

area_status.pack(
    side="left"
)


# =========================================================
# ENTITY PANEL
# =========================================================

entity_panel = tk.Frame(
    left,
    bg=PANEL,
    highlightbackground=BORDER,
    highlightthickness=1
)

entity_panel.pack(
    fill="x",
    pady=5
)


tk.Label(
    entity_panel,
    text="👹  ENTITY TRACKER",
    font=("Segoe UI", 11, "bold"),
    fg=WHITE,
    bg=PANEL
).pack(
    anchor="w",
    padx=18,
    pady=(12, 6)
)


entity_controls = tk.Frame(
    entity_panel,
    bg=PANEL
)

entity_controls.pack(
    fill="x",
    padx=18,
    pady=(0, 5)
)


entity_combo = ttk.Combobox(
    entity_controls,
    values=ENTITIES,
    state="readonly",
    style="Modern.TCombobox",
    width=22
)

entity_combo.set(
    "None"
)

entity_combo.pack(
    side="left"
)


tk.Button(
    entity_controls,
    text="⚠  RECORD",
    command=record_entity,
    font=("Segoe UI", 9, "bold"),
    fg=WHITE,
    bg="#8e3d48",
    activeforeground=WHITE,
    activebackground="#a94a57",
    relief="flat",
    padx=12,
    pady=8,
    cursor="hand2"
).pack(
    side="left",
    padx=7
)


tk.Button(
    entity_controls,
    text="RESET",
    command=reset_danger,
    font=("Segoe UI", 9, "bold"),
    fg=MUTED,
    bg=PANEL_LIGHT,
    activeforeground=WHITE,
    activebackground=BORDER,
    relief="flat",
    padx=12,
    pady=8,
    cursor="hand2"
).pack(
    side="left"
)


danger_status = tk.Label(
    entity_panel,
    text="⚠  Danger: 0",
    font=("Segoe UI", 10, "bold"),
    fg=GREEN,
    bg=PANEL
)

danger_status.pack(
    anchor="w",
    padx=18,
    pady=(3, 4)
)


entity_status = tk.Label(
    entity_panel,
    text="●  Waiting for entity...",
    font=("Segoe UI", 9),
    fg=MUTED,
    bg=PANEL
)

entity_status.pack(
    anchor="w",
    padx=18,
    pady=(0, 12)
)


# =========================================================
# ITEM PANEL
# =========================================================

item_panel = tk.Frame(
    left,
    bg=PANEL,
    highlightbackground=BORDER,
    highlightthickness=1
)

item_panel.pack(
    fill="x",
    pady=5
)


tk.Label(
    item_panel,
    text="🎒  ITEM TRACKER",
    font=("Segoe UI", 11, "bold"),
    fg=WHITE,
    bg=PANEL
).pack(
    anchor="w",
    padx=18,
    pady=(12, 6)
)


item_combo = ttk.Combobox(
    item_panel,
    values=ITEMS,
    state="readonly",
    style="Modern.TCombobox",
    width=22
)

item_combo.set(
    "None"
)

item_combo.pack(
    padx=18,
    pady=(0, 6)
)


item_note = tk.Entry(
    item_panel,
    bg=PANEL_LIGHT,
    fg=WHITE,
    insertbackground=WHITE,
    relief="flat",
    font=("Segoe UI", 10)
)

item_note.pack(
    fill="x",
    padx=18,
    pady=5,
    ipady=7
)

item_note.insert(
    0,
    "Optional item note..."
)


tk.Button(
    item_panel,
    text="➕  RECORD ITEM",
    command=record_item,
    font=("Segoe UI", 10, "bold"),
    fg=WHITE,
    bg=BLUE,
    activeforeground=WHITE,
    activebackground=BLUE_HOVER,
    relief="flat",
    padx=15,
    pady=8,
    cursor="hand2"
).pack(
    pady=7
)


item_status = tk.Label(
    item_panel,
    text="●  Waiting for item...",
    font=("Segoe UI", 9),
    fg=MUTED,
    bg=PANEL
)

item_status.pack(
    pady=(0, 10)
)


# =========================================================
# OBSERVATION PANEL
# =========================================================

observation_panel = tk.Frame(
    left,
    bg=PANEL,
    highlightbackground=BORDER,
    highlightthickness=1
)

observation_panel.pack(
    fill="x",
    pady=5
)


tk.Label(
    observation_panel,
    text="👀  OBSERVATION",
    font=("Segoe UI", 11, "bold"),
    fg=WHITE,
    bg=PANEL
).pack(
    anchor="w",
    padx=18,
    pady=(12, 6)
)


observation_entry = tk.Entry(
    observation_panel,
    bg=PANEL_LIGHT,
    fg=WHITE,
    insertbackground=WHITE,
    relief="flat",
    font=("Segoe UI", 10)
)

observation_entry.pack(
    fill="x",
    padx=18,
    pady=5,
    ipady=8
)

observation_entry.insert(
    0,
    "Example: Heard a loud sound..."
)


tk.Button(
    observation_panel,
    text="➕  RECORD OBSERVATION",
    command=record_observation,
    font=("Segoe UI", 10, "bold"),
    fg=WHITE,
    bg=BLUE,
    activeforeground=WHITE,
    activebackground=BLUE_HOVER,
    relief="flat",
    padx=15,
    pady=8,
    cursor="hand2"
).pack(
    pady=7
)


observation_status = tk.Label(
    observation_panel,
    text="●  Waiting for observation...",
    font=("Segoe UI", 9),
    fg=MUTED,
    bg=PANEL
)

observation_status.pack(
    pady=(0, 10)
)


# =========================================================
# RIGHT LOGS
# =========================================================

logs_title = tk.Label(
    right,
    text="INVESTIGATION LOGS",
    font=("Segoe UI", 11, "bold"),
    fg=MUTED,
    bg=BG
)

logs_title.pack(
    anchor="w",
    pady=(5, 2)
)


# =========================================================
# ENTITY LOG
# =========================================================

entity_log_panel = tk.Frame(
    right,
    bg=PANEL,
    highlightbackground=BORDER,
    highlightthickness=1
)

entity_log_panel.pack(
    fill="both",
    expand=True,
    pady=5
)


tk.Label(
    entity_log_panel,
    text="👹  ENTITY EVENTS",
    font=("Segoe UI", 10, "bold"),
    fg=MUTED,
    bg=PANEL
).pack(
    anchor="w",
    padx=15,
    pady=(10, 5)
)


entity_list = tk.Listbox(
    entity_log_panel,
    bg=DARK,
    fg=RED,
    selectbackground=BLUE,
    selectforeground=WHITE,
    font=("Consolas", 9),
    relief="flat",
    borderwidth=0
)

entity_list.pack(
    fill="both",
    expand=True,
    padx=15,
    pady=(0, 12)
)


# =========================================================
# ITEM LOG
# =========================================================

item_log_panel = tk.Frame(
    right,
    bg=PANEL,
    highlightbackground=BORDER,
    highlightthickness=1
)

item_log_panel.pack(
    fill="both",
    expand=True,
    pady=5
)


tk.Label(
    item_log_panel,
    text="🎒  ITEMS",
    font=("Segoe UI", 10, "bold"),
    fg=MUTED,
    bg=PANEL
).pack(
    anchor="w",
    padx=15,
    pady=(10, 5)
)


item_list = tk.Listbox(
    item_log_panel,
    bg=DARK,
    fg=CYAN,
    selectbackground=BLUE,
    selectforeground=WHITE,
    font=("Consolas", 9),
    relief="flat",
    borderwidth=0
)

item_list.pack(
    fill="both",
    expand=True,
    padx=15,
    pady=(0, 12)
)


# =========================================================
# OBSERVATION LOG
# =========================================================

observation_log_panel = tk.Frame(
    right,
    bg=PANEL,
    highlightbackground=BORDER,
    highlightthickness=1
)

observation_log_panel.pack(
    fill="both",
    expand=True,
    pady=5
)


tk.Label(
    observation_log_panel,
    text="👀  OBSERVATIONS",
    font=("Segoe UI", 10, "bold"),
    fg=MUTED,
    bg=PANEL
).pack(
    anchor="w",
    padx=15,
    pady=(10, 5)
)


observation_list = tk.Listbox(
    observation_log_panel,
    bg=DARK,
    fg=GREEN,
    selectbackground=BLUE,
    selectforeground=WHITE,
    font=("Consolas", 9),
    relief="flat",
    borderwidth=0
)

observation_list.pack(
    fill="both",
    expand=True,
    padx=15,
    pady=(0, 12)
)


# =========================================================
# TIMELINE
# =========================================================

timeline_panel = tk.Frame(
    right,
    bg=PANEL,
    highlightbackground=BORDER,
    highlightthickness=1
)

timeline_panel.pack(
    fill="both",
    expand=True,
    pady=5
)


tk.Label(
    timeline_panel,
    text="⏱️  TIMELINE",
    font=("Segoe UI", 10, "bold"),
    fg=MUTED,
    bg=PANEL
).pack(
    anchor="w",
    padx=15,
    pady=(10, 5)
)


timeline_list = tk.Listbox(
    timeline_panel,
    bg=DARK,
    fg=YELLOW,
    selectbackground=BLUE,
    selectforeground=WHITE,
    font=("Consolas", 9),
    relief="flat",
    borderwidth=0
)

timeline_list.pack(
    fill="both",
    expand=True,
    padx=15,
    pady=(0, 12)
)


# =========================================================
# BOTTOM BAR
# =========================================================

bottom = tk.Frame(
    root,
    bg=HEADER,
    height=45
)

bottom.pack(
    fill="x"
)


tk.Button(
    bottom,
    text="↻  RESET ALL",
    command=reset_everything,
    font=("Segoe UI", 9, "bold"),
    fg=MUTED,
    bg=PANEL_LIGHT,
    activeforeground=WHITE,
    activebackground=BORDER,
    relief="flat",
    padx=15,
    pady=6,
    cursor="hand2"
).pack(
    side="left",
    padx=20,
    pady=7
)


save_status = tk.Label(
    bottom,
    text="",
    font=("Segoe UI", 9),
    fg=GREEN,
    bg=HEADER
)

save_status.pack(
    side="left",
    padx=10
)


load_status = tk.Label(
    bottom,
    text="",
    font=("Segoe UI", 9),
    fg=GREEN,
    bg=HEADER
)

load_status.pack(
    side="left",
    padx=10
)


tk.Label(
    bottom,
    text="DOORS Investigation • Manual Companion",
    font=("Segoe UI", 9),
    fg="#606a7c",
    bg=HEADER
).pack(
    side="right",
    padx=20
)


# =========================================================
# START
# =========================================================

update_status()

root.mainloop()