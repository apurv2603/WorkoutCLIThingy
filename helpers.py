from datetime import datetime
from rich import print as print #as rich_print
from rich.panel import Panel
from rich.table import Table
from parser import *

from rich.text import Text

import os


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
    header = f"[bold {PLUM}]{workout.name}[/bold {PLUM}]\n"
    header += f"Start: [{TWI}]{workout.time}[/{TWI}]    Unit: [{TWI}]{workout.unit}[/{TWI}]\n"
    header += f"Exercises: [{X}]{len(workout.items)}[/{X}]"
    
    tables = []
    for ex in workout.items:
        t = Table(title=ex.name) #this assumes items can only be regular exercises, not supersets.
        t.add_column("#")
        t.add_column("Reps")
        t.add_column("Weight")
        for i, set in enumerate(ex.sets):
            t.add_row(str(i+1), str(set.reps), str(set.weight))
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
    
    print(st)
    print(Panel(header, title="Workout Summary", expand=False))

def history(workouts: list[Workout], exercise: str):
    if not workouts:
        print("no workouts found")
        return
    if not exercise:
        print("no exercise given")
        return
    tables = []
    for wrkout in workouts:
        for item in wrkout.items:
            if isinstance(item, Exercise) and item.name == exercise:
                t = Table(title=f"{wrkout.date}")
                t.add_column("#")
                t.add_column("Reps")
                t.add_column("Weight")
                for i, st in enumerate(item.sets):
                    t.add_row(str(i+1), str(st.reps), str(st.weight) + " " + wrkout.unit)
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
                for i, set in enumerate(item.sets):
                    t.add_row(str(i+1), str(set.reps), str(set.weight) + " " + workout.unit)
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
    

    