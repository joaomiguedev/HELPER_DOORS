import tkinter as tk
from tkinter import messagebox, filedialog
from datetime import datetime
import json
import os

# ============================================================
# CHRONIX — TIME RECORD
# ============================================================

WIDTH = 500
HEIGHT = 620

BG = "#000000"
PANEL = "#080d0a"
GREEN = "#39ff88"
DARK_GREEN = "#10291b"
BRIGHT_GREEN = "#70ffad"
WHITE = "#d8ffe7"
GRAY = "#668574"
RED = "#ff4d6d"

DATA_FILE = "chronix_history.json"


# ============================================================
# WINDOW
# ============================================================

root = tk.Tk()
root.overrideredirect(True)
root.configure(bg=BG)
root.geometry(f"{WIDTH}x{HEIGHT}")

root.update_idletasks()

screen_w = root.winfo_screenwidth()
screen_h = root.winfo_screenheight()

x = (screen_w - WIDTH) // 2
y = (screen_h - HEIGHT) // 2

root.geometry(f"{WIDTH}x{HEIGHT}+{x}+{y}")

always_on_top = False
root.attributes("-topmost", always_on_top)


# ============================================================
# TIMER STATE
# ============================================================

running = False
paused = False

start_time = None
pause_started = None
paused_total = 0.0

laps = []
session_history = []


# ============================================================
# HISTORY
# ============================================================

def load_history():
    global session_history

    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as file:
                session_history = json.load(file)
        except Exception:
            session_history = []


def save_history():
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as file:
            json.dump(session_history, file, indent=4)
    except Exception as error:
        messagebox.showerror("Chronix", str(error))


load_history()


# ============================================================
# WINDOW MOVEMENT
# ============================================================

def start_move(event):
    root.drag_x = event.x
    root.drag_y = event.y


def move_window(event):
    new_x = root.winfo_x() + event.x - root.drag_x
    new_y = root.winfo_y() + event.y - root.drag_y

    root.geometry(f"+{new_x}+{new_y}")


# ============================================================
# TIME FORMAT
# ============================================================

def format_time(seconds):
    seconds = max(0, seconds)

    days = int(seconds // 86400)
    hours = int((seconds % 86400) // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = seconds % 60

    return f"{days:02d}d {hours:02d}:{minutes:02d}:{secs:05.2f}"


def get_elapsed():
    if start_time is None:
        return 0.0

    if paused:
        current = pause_started
    else:
        current = datetime.now()

    elapsed = (current - start_time).total_seconds()
    elapsed -= paused_total

    return max(0, elapsed)


# ============================================================
# TIMER
# ============================================================

def start_timer():
    global running
    global paused
    global start_time
    global pause_started
    global paused_total
    global laps

    if not running:
        start_time = datetime.now()
        pause_started = None
        paused_total = 0.0
        laps = []

        clear_laps()

        running = True
        paused = False

        status_label.config(
            text="● RUNNING",
            fg=GREEN
        )

        start_button.config(
            text="PAUSE",
            command=pause_timer
        )

        update_timer()


def pause_timer():
    global paused
    global pause_started

    if running and not paused:
        paused = True
        pause_started = datetime.now()

        status_label.config(
            text="Ⅱ PAUSED",
            fg="#ffd84d"
        )

        start_button.config(
            text="RESUME",
            command=resume_timer
        )


def resume_timer():
    global paused
    global pause_started
    global paused_total

    if running and paused:
        now = datetime.now()

        if pause_started:
            paused_total += (
                now - pause_started
            ).total_seconds()

        pause_started = None
        paused = False

        status_label.config(
            text="● RUNNING",
            fg=GREEN
        )

        start_button.config(
            text="PAUSE",
            command=pause_timer
        )

        update_timer()


def stop_timer():
    global running
    global paused

    if running:
        elapsed = get_elapsed()
        save_session(elapsed)

    running = False
    paused = False

    status_label.config(
        text="● STOPPED",
        fg=GRAY
    )

    start_button.config(
        text="START",
        command=start_timer
    )


def reset_timer():
    global running
    global paused
    global start_time
    global pause_started
    global paused_total
    global laps

    running = False
    paused = False

    start_time = None
    pause_started = None
    paused_total = 0.0
    laps = []

    time_label.config(
        text="00d 00:00:00.00"
    )

    status_label.config(
        text="● READY",
        fg=GRAY
    )

    start_button.config(
        text="START",
        command=start_timer
    )

    clear_laps()


def update_timer():
    if running and not paused:
        time_label.config(
            text=format_time(get_elapsed())
        )

        root.after(50, update_timer)


# ============================================================
# LAP
# ============================================================

def add_lap():
    if not running:
        return

    elapsed = get_elapsed()

    lap_number = len(laps) + 1

    previous = (
        laps[-1]["total"]
        if laps
        else 0
    )

    lap_time = elapsed - previous

    lap = {
        "number": lap_number,
        "lap": lap_time,
        "total": elapsed
    }

    laps.append(lap)

    lap_list.insert(
        0,
        f"  LAP {lap_number:02d}    "
        f"{format_time(lap_time)}    "
        f"TOTAL {format_time(elapsed)}"
    )


def clear_laps():
    lap_list.delete(0, tk.END)


# ============================================================
# SAVE SESSION
# ============================================================

def save_session(duration=None):
    if duration is None:
        duration = get_elapsed()

    if duration <= 0:
        return

    session = {
        "date": datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
        "duration": duration,
        "laps": laps.copy()
    }

    session_history.insert(
        0,
        session
    )

    del session_history[100:]

    save_history()


def export_history():
    if not session_history:
        messagebox.showinfo(
            "Chronix",
            "No session history to export."
        )
        return

    filename = filedialog.asksaveasfilename(
        title="Export Chronix History",
        defaultextension=".json",
        filetypes=[
            ("JSON files", "*.json"),
            ("Text files", "*.txt"),
            ("All files", "*.*")
        ]
    )

    if not filename:
        return

    try:
        with open(
            filename,
            "w",
            encoding="utf-8"
        ) as file:
            json.dump(
                session_history,
                file,
                indent=4
            )

        messagebox.showinfo(
            "Chronix",
            "History exported successfully."
        )

    except Exception as error:
        messagebox.showerror(
            "Chronix",
            str(error)
        )


# ============================================================
# HISTORY WINDOW
# ============================================================

def show_history():
    history_window = tk.Toplevel(root)

    history_window.title(
        "Chronix History"
    )

    history_window.geometry(
        "500x450"
    )

    history_window.configure(
        bg=BG
    )

    history_window.attributes(
        "-topmost",
        always_on_top
    )

    title = tk.Label(
        history_window,
        text="SESSION HISTORY",
        fg=GREEN,
        bg=BG,
        font=("Arial", 14, "bold")
    )

    title.pack(
        pady=15
    )

    listbox = tk.Listbox(
        history_window,
        bg=PANEL,
        fg=WHITE,
        selectbackground=DARK_GREEN,
        selectforeground=GREEN,
        font=("Consolas", 10),
        border=0,
        highlightthickness=1,
        highlightbackground=DARK_GREEN
    )

    listbox.pack(
        fill="both",
        expand=True,
        padx=15,
        pady=10
    )

    for session in session_history:
        date = session.get(
            "date",
            "Unknown"
        )

        duration = session.get(
            "duration",
            0
        )

        listbox.insert(
            tk.END,
            f"{date}   {format_time(duration)}"
        )

    export_button = tk.Button(
        history_window,
        text="EXPORT HISTORY",
        command=export_history,
        fg=BG,
        bg=GREEN,
        activebackground=BRIGHT_GREEN,
        font=("Arial", 10, "bold"),
        relief="flat",
        border=0,
        padx=20,
        pady=8
    )

    export_button.pack(
        pady=15
    )


# ============================================================
# CLOCK
# ============================================================

def update_clock():
    current_time = datetime.now().strftime(
        "%H:%M:%S"
    )

    clock_label.config(
        text=current_time
    )

    root.after(
        500,
        update_clock
    )


# ============================================================
# ALWAYS ON TOP
# ============================================================

def toggle_topmost():
    global always_on_top

    always_on_top = not always_on_top

    root.attributes(
        "-topmost",
        always_on_top
    )

    if always_on_top:
        top_button.config(
            text="📌 ON",
            fg=GREEN
        )
    else:
        top_button.config(
            text="📌 OFF",
            fg=GRAY
        )


# ============================================================
# CLOSE
# ============================================================

def close_app():
    if running:
        answer = messagebox.askyesno(
            "Chronix",
            "Timer is still running.\n\nClose Chronix?"
        )

        if not answer:
            return

    root.destroy()


# ============================================================
# KEYBOARD SHORTCUTS
# ============================================================

def keyboard_start(event=None):
    if not running:
        start_timer()
    elif paused:
        resume_timer()


def keyboard_space(event=None):
    if not running:
        start_timer()
    elif paused:
        resume_timer()
    else:
        pause_timer()


def keyboard_reset(event=None):
    reset_timer()


def keyboard_lap(event=None):
    add_lap()


def keyboard_stop(event=None):
    stop_timer()


root.bind(
    "<space>",
    keyboard_space
)

root.bind(
    "<Return>",
    keyboard_start
)

root.bind(
    "<r>",
    keyboard_reset
)

root.bind(
    "<R>",
    keyboard_reset
)

root.bind(
    "<l>",
    keyboard_lap
)

root.bind(
    "<L>",
    keyboard_lap
)

root.bind(
    "<s>",
    keyboard_stop
)

root.bind(
    "<S>",
    keyboard_stop
)


# ============================================================
# TOP BAR
# ============================================================

top = tk.Frame(
    root,
    bg=BG,
    height=42
)

top.pack(
    fill="x"
)

top.bind(
    "<Button-1>",
    start_move
)

top.bind(
    "<B1-Motion>",
    move_window
)


title = tk.Label(
    top,
    text="CHRONIX",
    fg=GREEN,
    bg=BG,
    font=("Arial", 11, "bold")
)

title.pack(
    side="left",
    padx=15
)

title.bind(
    "<Button-1>",
    start_move
)

title.bind(
    "<B1-Motion>",
    move_window
)


top_button = tk.Button(
    top,
    text="📌 OFF",
    command=toggle_topmost,
    fg=GRAY,
    bg=BG,
    activebackground=BG,
    activeforeground=GREEN,
    border=0,
    font=("Arial", 8, "bold")
)

top_button.pack(
    side="right",
    padx=5
)


close_button = tk.Button(
    top,
    text="×",
    command=close_app,
    fg=GREEN,
    bg=BG,
    activebackground=GREEN,
    activeforeground=BG,
    border=0,
    font=("Arial", 18, "bold")
)

close_button.pack(
    side="right",
    padx=8
)


# ============================================================
# MAIN PANEL
# ============================================================

main = tk.Frame(
    root,
    bg=BG
)

main.pack(
    fill="both",
    expand=True
)


status_label = tk.Label(
    main,
    text="● READY",
    fg=GRAY,
    bg=BG,
    font=("Arial", 9, "bold")
)

status_label.pack(
    pady=(5, 2)
)


time_label = tk.Label(
    main,
    text="00d 00:00:00.00",
    fg=GREEN,
    bg=BG,
    font=("Consolas", 27, "bold")
)

time_label.pack(
    pady=(10, 2)
)


clock_label = tk.Label(
    main,
    text="00:00:00",
    fg=GRAY,
    bg=BG,
    font=("Consolas", 11)
)

clock_label.pack(
    pady=(0, 15)
)


# ============================================================
# BUTTON STYLE
# ============================================================

def make_button(
    parent,
    text,
    command,
    width=9
):
    return tk.Button(
        parent,
        text=text,
        command=command,
        fg=GREEN,
        bg=PANEL,
        activebackground=DARK_GREEN,
        activeforeground=BRIGHT_GREEN,
        font=("Arial", 9, "bold"),
        relief="flat",
        border=0,
        width=width,
        padx=5,
        pady=8,
        cursor="hand2"
    )


# ============================================================
# BUTTON ROW 1
# ============================================================

row1 = tk.Frame(
    main,
    bg=BG
)

row1.pack(
    pady=4
)


start_button = make_button(
    row1,
    "START",
    start_timer
)

start_button.pack(
    side="left",
    padx=3
)


stop_button = make_button(
    row1,
    "STOP",
    stop_timer
)

stop_button.pack(
    side="left",
    padx=3
)


reset_button = make_button(
    row1,
    "RESET",
    reset_timer
)

reset_button.pack(
    side="left",
    padx=3
)


# ============================================================
# BUTTON ROW 2
# ============================================================

row2 = tk.Frame(
    main,
    bg=BG
)

row2.pack(
    pady=4
)


lap_button = make_button(
    row2,
    "LAP",
    add_lap
)

lap_button.pack(
    side="left",
    padx=3
)


history_button = make_button(
    row2,
    "HISTORY",
    show_history
)

history_button.pack(
    side="left",
    padx=3
)


save_button = make_button(
    row2,
    "SAVE",
    lambda: save_session()
)

save_button.pack(
    side="left",
    padx=3
)


# ============================================================
# LAP PANEL
# ============================================================

lap_title = tk.Label(
    main,
    text="LAP TIMES",
    fg=GREEN,
    bg=BG,
    font=("Arial", 9, "bold")
)

lap_title.pack(
    anchor="w",
    padx=22,
    pady=(15, 5)
)


lap_frame = tk.Frame(
    main,
    bg=PANEL
)

lap_frame.pack(
    fill="both",
    expand=True,
    padx=20,
    pady=(0, 10)
)


lap_list = tk.Listbox(
    lap_frame,
    bg=PANEL,
    fg=WHITE,
    selectbackground=DARK_GREEN,
    selectforeground=GREEN,
    font=("Consolas", 9),
    border=0,
    highlightthickness=1,
    highlightbackground=DARK_GREEN
)

lap_list.pack(
    fill="both",
    expand=True,
    padx=5,
    pady=5
)


# ============================================================
# FOOTER
# ============================================================

footer = tk.Label(
    main,
    text="SPACE Pause/Resume   •   L Lap   •   R Reset   •   S Stop",
    fg=GRAY,
    bg=BG,
    font=("Arial", 8)
)

footer.pack(
    pady=(0, 12)
)


# ============================================================
# START
# ============================================================

update_clock()

root.mainloop()