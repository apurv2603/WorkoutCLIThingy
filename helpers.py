from datetime import datetime
from rich import print as print #as rich_print
from rich.panel import Panel
from rich.table import Table
from parser import *

from rich.text import Text

import os

# EXPORT 
EXERCISE_LIST = ["squat", "bench-press", "deadlift", 
                "overhead-press", "barbell-row", "pull-up", "dip", "lunge", "leg-press", "leg-curl", 
                "leg-ext", "calf-raise", "bicep-curl", "shoulder-press", "pull-up", "chin-up",
                "tricep-ext", "shoulder-fly", "lat-pulldown", "chest-fly", "db-row", "db-press", "db-curl", "db-lat-raise"]
# EXPORT
MUSCLE_GROUPS = ["legs", "chest", "back", "shoulders", "arms", "core"]

A = "#7a153d"
B = "#b22b4e", 
C = "#c53648"
D = "#d94c3a"

Z = "#f4e1c1"
Y = "#f9c8a5"
X = "#f6a76f"
W = "#f57b2a"

PLUM = "#B33C86"
TWI = "#990E4F"

light_red = "#ff7f7f"
light_orange = "#ffb347"
light_yellow = "#ffff99"
light_green = "#90ee90"

def rep_to_color(reps):
    if reps <= 1:
        return light_red
    elif reps <= 3:
        return light_orange
    elif reps <= 5:
        return light_yellow
    else:
        return light_green

def weight_to_color(weight, weight_max):
    if weight <= 0.70 * weight_max:
        return light_red
    elif weight <= 0.80 * weight_max:
        return light_orange
    elif weight <= 0.90 * weight_max:
        return light_yellow
    else:
        return light_green

def parse_num(arg):
        num = 0
        if arg:
            argNum = arg.split()[0]
            try: 
                num = max(0, int(argNum))
            except Exception:
                pass
        return num

def parse_exer(arg):
    exer = ""
    if arg:
        argExer = arg.strip().replace(" ", "-").lower()
        if is_valid_exer(argExer):
            exer = argExer
    return exer

def is_valid_exer(s):
    return all(c.isalpha() or c == '-' for c in s) and len(s) > 0

def parse_date(s):
    parts = s.split('_')
    return datetime.strptime(f"{parts[0]}_{parts[1]}_{parts[2]}", "%m_%d_%y")

def summary(workout):
    header = f"Title/Date: [bold {PLUM}]{workout.name}[/bold {PLUM}]\n"
    header += f"Start: [{TWI}]{workout.time}[/{TWI}]    Unit: [{TWI}]{workout.unit}[/{TWI}]\n"
    header += f"Exercises: [{X}]{len(workout.items)}[/{X}]"
    
    tables = []
    for ex in workout.items:
        t = Table(title= ex.name) #this assumes items can only be regular exercises, not supersets.
        t.add_column("#")
        t.add_column(f"Reps")
        t.add_column("Weight")
        max_weight = max(st.weight for st in ex.sets) if ex.sets else 0

        for i, st in enumerate(ex.sets):
            repColor = rep_to_color(st.reps)
            repStr = f"[{repColor}]{st.reps}[/{repColor}]"

            weightColor = weight_to_color(st.weight, max(max_weight, st.weight))
            weightStr = f"[{weightColor}]{st.weight}[/{weightColor}]"

            t.add_row(str(i+1), repStr, weightStr)
        tables.append(t)

    st = Table(title="[bold underline]Exercise Summary[/bold underline]\n", show_header=False, show_edge=False, show_lines=False, box=None)
    tableList = []
    for i in range(0, min(5, len(tables))):
        st.add_column()
    for i, tab in enumerate(tables):
        # reset row every 5
        if i % 5 == 0:
            tableList = []
        tableList.append(tab)
        if len(tableList) == 5 or i == len(tables) - 1:
            st.add_row(*tableList)
    
    NotesPanel = Panel("\n".join([f"➤ [italic]{note.text}[/italic]" for note in workout.notes]), title="[bold]Notes[/bold]", border_style=W, expand=False)
    SummaryPanel = Panel(header, title="Workout Summary", expand=False, border_style=X)
    st_2 = Table(title="", show_header=False, show_edge=False, show_lines=False, box=None)
    st_2.add_column()
    st_2.add_column()
    st_2.add_row(SummaryPanel, NotesPanel)
    
    print("")
    print(st) # MAIN EXER TABLE
    print(st_2)
    print()

def history(workouts: list[Workout], exercise: str):
    if not workouts:
        print("no workouts found")
        return
    if not exercise:
        print("no exercise given")
        return
    tables = []
    
    for wrkout in workouts:
        max_weight = 0
        for item in wrkout.items:
            if isinstance(item, Exercise) and item.name == exercise:
                for st in item.sets:
                    if st.weight > max_weight:
                            max_weight = st.weight
        for item in wrkout.items:
            if isinstance(item, Exercise) and item.name == exercise:
                t = Table(title=f"{wrkout.date}")
                t.add_column("#")
                t.add_column("Reps")
                t.add_column("Weight")
                for i, st in enumerate(item.sets):
                    repColor = rep_to_color(st.reps)
                    repStr = f"[{repColor}]{st.reps}[/{repColor}]"

                    weightColor = weight_to_color(st.weight, max_weight)
                    weightStr = f"[{weightColor}]{st.weight}[/{weightColor}]"

                    t.add_row(str(i+1), repStr, weightStr)

                tables.append(t)
    st = Table(title="[bold underline]"+exercise+" History[/bold underline]\n", show_header=False, show_edge=False, show_lines=False, box=None)
    tableList = []
    for i in range(0, min(4, len(tables))):
        st.add_column()
    for i, tab in enumerate(tables):
        # reset row every 4
        if i % 4 == 0:
            tableList = []
        tableList.append(tab)
        if len(tableList) == 4 or i == len(tables) - 1:
            st.add_row(*tableList)
    print("")
    print(st)
    return



def last(workouts: list[Workout], exercise: str):
    if not workouts:
        print("no workouts found")
        return
    if not exercise:
        print("no exercise given")
        return
    for workout in reversed(workouts):
        for item in workout.items:
            if isinstance(item, Exercise) and item.name == exercise:
                t = Table(title="[bold underline]"+item.name+"[/bold underline]")
                t.add_column("#")
                t.add_column("Reps")
                t.add_column("Weight")
                max_weight = max(st.weight for st in item.sets) if item.sets else 0
                for i, st in enumerate(item.sets):
                    repColor = rep_to_color(st.reps)
                    repStr = f"[{repColor}]{st.reps}[/{repColor}]"

                    weightColor = weight_to_color(st.weight, max(max_weight, st.weight))
                    weightStr = f"[{weightColor}]{st.weight}[/{weightColor}]"

                    t.add_row(str(i+1), repStr, weightStr)
                print(t)
                print(f"Last workout with {exercise} was on {workout.date} at {workout.time}")

                return

def pr(workouts: list[Workout], exercise: str):
    if not workouts:
        print("no workouts found")
        return
    if not exercise:
        print("no exercise given")
        return
    pr = None
    pr_workout = None
    best_set = None 
    t = Table(title="[bold underline]"+exercise+" PR[/bold underline]")

    for workout in workouts:
        for item in workout.items:
            if isinstance(item, Exercise) and item.name == exercise:
                for st in item.sets: 
                    if pr is None or st.weight > pr:
                        pr = st.weight
                        pr_workout = workout
                        best_set = st
    if pr is not None:
        t.add_column("Reps")
        t.add_column("Weight")
        t.add_row(str(best_set.reps), str(best_set.weight) + " " + best_set.unit)
        print(t)
        print(f"PR for {exercise} is {pr} {pr_workout.unit}, achieved on {pr_workout.date} at {pr_workout.time}")
    else:
        print(f"No sets found for exercise: {exercise}")

def pr(workouts: list[Workout], exercise: str):
    if not workouts:
        print("no workouts found")
        return
    if not exercise:
        print("no exercise given")
        return
    pr = None
    pr_workout = None
    best_set = None 
    t = Table(title="[bold underline]"+exercise+" PR[/bold underline]")

    for workout in workouts:
        for item in workout.items:
            if isinstance(item, Exercise) and item.name == exercise:
                for st in item.sets: 
                    if pr is None or st.weight > pr:
                        pr = st.weight
                        pr_workout = workout
                        best_set = st
    if pr is not None:
        t.add_column("Reps")
        t.add_column("Weight")
        t.add_row(str(best_set.reps), str(best_set.weight) + " " + best_set.unit)
        print(t)
        print(f"PR for {exercise} is {pr} {pr_workout.unit}, achieved on {pr_workout.date} at {pr_workout.time}")
    else:
        print(f"No sets found for exercise: {exercise}")

def frequency(workout_dir):
    files = os.listdir(workout_dir)
    dates = list(set([f.split(':')[0].split(".")[0] for f in files]))
    

    