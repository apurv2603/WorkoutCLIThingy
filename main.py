import cmd
from importlib.metadata import files
from helpers import *
import os
import datetime
from rich import print as print #as rich_print
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from parser import parse

A = "#7a153d"
B = "#b22b4e" 
C = "#c53648"
D = "#d94c3a"

Z = "#f4e1c1"
Y = "#f9c8a5"
X = "#f6a76f"
W = "#f57b2a"


promptDefault = "ExerThing"
SET_KEYWORD = ">"
class ExerThing(cmd.Cmd):
    prompt = promptDefault + "> "
    WORKOUT_DIR = None
    WORKOUT_FILEDIR = None
    WORKOUT_FNAME = None
    EXER_NAME = None
    EXER_WRITE_AT = -1
    UNIT_ABBR = "lbs"

    # doc_header = "Commands:"  # help header
    # ruler = "="               # separator char in help

    def __init__(self):
        super().__init__()
        dirs = [d for d in os.listdir(".") if os.path.isdir(d)]
        if "workouts" in dirs:
            self.WORKOUT_DIR = os.path.join(os.getcwd(), "workouts")
        else:
            self.WORKOUT_DIR = None
        self.WORKOUT_FILEDIR = None
        self.WORKOUT_FNAME = None
        my_intro = "\nWelcome to ExerThing!"
        my_intro += " Directory Init: ✅." if self.WORKOUT_DIR is not None else " Directory Init: ❌."
        my_intro += " Type help or ? to list commands."
        print("[bold]" +  my_intro + "[/bold]" )
    
    def default(self, line):
        if line.startswith("ls") or line.startswith("dir") or line.startswith("cd") or line.startswith("pwd") or line.startswith("clear") or line.startswith("cat"):
            os.system(line)
            return
        # NOTES
        if line.startswith("//"):
            if self.addNotesLine(line[2:].strip()):
                print("Added Note!")
            return

        # LOG REPS AND WEIGHT
        line = line.lower().strip()
        if self.EXER_NAME is not None:
            parts = []
            if "@" in line:
                parts = line.split("@")
            elif "x" in line:
                parts = line.split("x")
            if len(parts) == 2 :
                reps = parts[0].strip()   # "10"
                weight = parts[1].strip() # "23"
                if reps.isdigit() and weight.isdigit():
                    self.logSet(int(reps), int(weight))
                    print(f"Logged set: {reps} reps @ {weight} {self.UNIT_ABBR}")
                    return
        else:
            print(f"Unknown command: {line}")
    

    
    def do_init(self, arg):
        # Create workouts folder
        if self.WORKOUT_DIR is None:
            doCreate = "" if arg.strip() == "" else arg.strip().lower()
            if doCreate == "":
                doCreate = input("No 'workouts' directory found. Create one? (y/n) ")
            if doCreate.lower() == "n":
                print("Cannot continue without workouts directory.")
                return
            if doCreate.lower() == "y":
                os.mkdir("workouts")
                self.WORKOUT_DIR = os.path.join(os.getcwd(), "workouts")
                print("Initialized workouts directory at " + self.WORKOUT_DIR)
        else:
            print("Workouts directory already initialized at " + self.WORKOUT_DIR)

    def do_begin(self, arg):
        # Begin exercise ARG[0]
        if self.testDirIsNull():
            return
        user_title = arg.strip() if arg else ""
        dt = datetime.datetime.now().strftime("%m_%d_%Y")
        local_name = dt + ":" + user_title if user_title else dt
        doCreate = input(f"Start Workout \"{local_name}\"? (y/n) ")
        if doCreate.lower() == "n":
            return
        if doCreate.lower() == "y":
            self.WORKOUT_FNAME = local_name
            self.WORKOUT_FILEDIR = os.path.join(self.WORKOUT_DIR, local_name + ".workout")
            init_time = datetime.datetime.now().strftime("%H:%M")     
            with open(self.WORKOUT_FILEDIR, "w") as f:
                f.write(f"$ {local_name} ")
                f.write(f"$$ {self.UNIT_ABBR} ")
                f.write(f"$$$ {init_time}\n")
                f.write(f"\n")
                f.write(f"// ")
            print(f"Started workout \"{local_name}\"!")
            self.WORKOUT_ABBR = user_title if user_title else dt
            self.updatePrompt()
    do_b = do_begin

    def do_continue(self, arg):
        # IF NOT IN A DIR AT ALL
        if self.testDirIsNull():
            return
        
        # Resume Exercise if in Exercises, else resume Workout
        if self.WORKOUT_FILEDIR is not None:

            # CHECK EXER EXISTS IN WORKOUT
            exerName = parse_exer(arg)
            if exerName != "":
                spot = self.exerExistsWriteLoc(exerName)
                if spot != -1:
                    self.EXER_WRITE_AT = spot
                    self.EXER_NAME = exerName
                    self.updatePrompt()
                    return
            # Else prompt all
            i = 0
            iToExerName = {}
            with open(self.WORKOUT_FILEDIR, "r") as f:
                lines = f.readlines()
            for line in lines:
                if line.startswith("# "):
                    COL = A if i % 2 == 0 else C
                    print(f"[{i}] [{COL}]{line[2:].strip()}[/{COL}]")
                    iToExerName[i] = line[2:].strip()
                    i += 1
            if i <= 0:
                print("No exercises found")
                return
            choice = input("Enter exercise number: ") 
            if choice.isdigit() and int(choice) in iToExerName:
                self.do_continue(iToExerName[int(choice)])
            else:
                print("Continue Exercise Cancelled.")
            return
        
        files = os.listdir(self.WORKOUT_DIR) if self.WORKOUT_DIR is not None else []
        N = len(files)
        if N == 0:
            print("No workouts found in workouts directory. Use 'begin' or 'begin <workout_name>' to start a workout.")
            return
        files.sort(key=lambda f: datetime.datetime.strptime((f.split(".")[0]).split(":")[0], "%m_%d_%Y"), reverse=True)
        files = files[:5]
        for i in range(len(files)):
            COL = A if i % 2 == 0 else C
            print(f"[{i}] [{COL}]{files[i]}[/{COL}]")        
        choice = input("Enter workout number: ")
        if choice.isdigit() and int(choice) in range(len(files)):
            self.WORKOUT_FILEDIR = os.path.join(self.WORKOUT_DIR, files[int(choice)])
            self.WORKOUT_FNAME = files[int(choice)]
            self.updatePrompt()
            print(f"Resumed workout \"{self.WORKOUT_FNAME}\"!")
        else:
            print("Continue Cancelled.")
    do_c = do_cont = do_continue

    def do_list(self, arg):
        # List workouts, If arg is a number, list that many most recent workouts
        files = os.listdir(self.WORKOUT_DIR) if self.WORKOUT_DIR is not None else []
        files.sort(key=lambda f: datetime.datetime.strptime((f.split(".")[0]).split(":")[0], "%m_%d_%Y"), reverse=True)
        if arg.isdigit() and int(arg) in range(len(files)):
            if int(arg) == 0:
                return
            print(" | ".join(files[:int(arg)]))
        else:
            print(" | ".join(files))

    def do_log(self, arg):
        # Begin log exercise
        if self.testDirIsNull() or self.testWorkoutIsNull():
            return
        exerName = parse_exer(arg)

        if exerName == "":
            print("No exercise name provided, or invalid exercise name. Exercise names may only contain letters and dashes.")
            return
        
        # IF LOG ALR EXISTS
        spot = self.exerExistsWriteLoc(exerName)
        if spot != -1:
            choice = input(f"Exercise {exerName} already exists, continue? (y/n) ")
            if choice.lower() == "y":
                self.EXER_WRITE_AT = spot
                self.EXER_NAME = exerName
                self.updatePrompt()
                return
            else:
                print("Log cancelled.")
                return
        
        # ELSE CREATE NEW LOG
        if spot < 0:
            self.createNewExer(exerName)
        
    def do_set_unit(self, arg):
        if self.testDirIsNull() or self.testWorkoutIsNull():
            return
        if arg is None or arg.strip() == "":
            print("Usage: set_unit <k/kg/kilo | p/lb/lbs/pound>")
            return
        arg0 = arg.strip().lower()
        if arg0 == "k" or arg0 == "kg" or arg0 == "kilo" or arg0 == "kilos":
            print("Weight set to kilos")
            self.UNIT_ABBR = "kg"
            return
        if arg0 == "p" or arg0 == "lb" or arg0 == "lbs" or arg0 == "pound" or arg0 == "pounds":
            print("Weight set to pounds")
            self.UNIT_ABBR = "lbs"
            return
        else:
            print("Usage: set_unit <k/kg/kilo | p/lb/lbs/pound>")
    do_set = do_set_unit

    def do_last(self, arg):
        if self.testDirIsNull():
            return
        exerName = parse_exer(arg)
        if exerName == "":
            print("Invalid exercise name.")
            return
        workouts = []
        files = os.listdir(self.WORKOUT_DIR)
        files.sort(key=lambda f: datetime.datetime.strptime((f.split(".")[0]).split(":")[0], "%m_%d_%Y"))
        for file in files:
            workout = parse(os.path.join(self.WORKOUT_DIR, file))
            workouts.append(workout)
        last(workouts, exerName)
    
    def do_pr(self, arg):
        if self.testDirIsNull():
            return
        exerName = parse_exer(arg)
        if exerName == "":
            print("Invalid exercise name.")
            return
        workouts = []
        files = os.listdir(self.WORKOUT_DIR)
        for file in files:
            workout = parse(os.path.join(self.WORKOUT_DIR, file))
            workouts.append(workout)
        pr(workouts, exerName)

    def do_history(self, arg):
        if self.testDirIsNull():
            return
        exerName = parse_exer(arg)
        if exerName == "":
            print("Invalid exercise name.")
            return
        workouts = []
        files = os.listdir(self.WORKOUT_DIR)
        files.sort(key=lambda f: datetime.datetime.strptime((f.split(".")[0]).split(":")[0], "%m_%d_%Y"))
        for file in files:
            workout = parse(os.path.join(self.WORKOUT_DIR, file))
            workouts.append(workout)
        history(workouts, exerName)
    do_h = do_hist = do_history
    
    

    def do_summary(self, arg):
        if self.testDirIsNull() or self.testWorkoutIsNull():
            return

        workout = parse(self.WORKOUT_FILEDIR)  # your parser
        summary(workout)
    do_s = do_sum = do_summary

    def do_exit(self, arg):
        # Take a step down in the hierarchy, or exit if at base level
        if self.EXER_NAME is not None:
            print(f"Leaving Exercise {self.EXER_NAME}...")
            self.EXER_NAME = None
            self.updatePrompt()
            return
        elif self.WORKOUT_FILEDIR is not None:
            self.WORKOUT_FILEDIR = None
            self.WORKOUT_FNAME = None
            self.updatePrompt()
            print("Leaving Workout...")
            return
        else:
            print("Exiting...")
            return True  # Returning True exits the loop
    do_EOF = do_done = do_d = do_q = do_exit

    def do_frequency(self):
        frequency()
    do_freq = do_f = do_frequency
    ## END DO_ FXNS ##
    ## END DO_ FXNS ##
    ## END DO_ FXNS ##

    def updatePrompt(self):
        if self.WORKOUT_FILEDIR is None or self.WORKOUT_FNAME is None:
            self.prompt = promptDefault + "> "
            return
        lst = self.WORKOUT_FNAME.split(':')
        word2 = ""
        if len(lst) > 1:
            word2 = "*" +lst[-1].split(".")[0]
        else:
            word2 = self.WORKOUT_FNAME.split(".")[0]
        if self.EXER_NAME is not None:
            self.prompt = f"{promptDefault}/{word2}/{self.EXER_NAME}> "
        else:
            self.prompt = f"{promptDefault}/{word2}> "
    
    def emptyline(self):
        # On enter reshow prompt and do nothing
        pass

    def addNotesLine(self, line):
        if self.testDirIsNull() or self.testWorkoutIsNull():
            return
        with open(self.WORKOUT_FILEDIR, "a") as f:
            f.write(f"// {line}\n")
        return
    
    def testDirIsNull(self):
        if self.WORKOUT_DIR is None:
            print("Must initialize workout directory with 'init' first!")
            return True
        else:
            return False
    
    def testWorkoutIsNull(self):
        if self.WORKOUT_FILEDIR is None:
            print("Must begin/continue a workout with 'begin'/'continue' !")
            return True
        else:
            return False
    
    def exerExistsWriteLoc(self, exerName):
        if self.WORKOUT_FILEDIR is None:
            return -1
        with open(self.WORKOUT_FILEDIR, "r") as f:
            lines = f.readlines()
        spot = -1
        find = ("# " + exerName)
        for i, line in enumerate(lines):
            if find in line:
                spot = i
                break
        if spot != -1:
            # Get to line to write at next
            while spot < len(lines) and (lines[spot] != "\n"): # lines[spot].startswith(SET_KEYWORD) or lines[spot].startswith("# ")
                spot += 1
        return spot
    
    def getNotesLines(self):
        if self.WORKOUT_FILEDIR is None:
            return []
        with open(self.WORKOUT_FILEDIR, "r") as f:
            lines = f.readlines()
        notesLines = []
        for i, line in enumerate(lines):
            if "//" in line:
                notesLines.append(i)
        return notesLines
    
    def createNewExer(self, exerName):
        notesLines = self.getNotesLines()
        newLine0 = f"\n"
        newLine1 = f"# {exerName}\n"
        with open(self.WORKOUT_FILEDIR, "r") as f:
            lines = f.readlines()
            insertAt = notesLines[0] - 1 if len(notesLines) > 0 else len(lines)
        
        lines.insert(insertAt, newLine0)
        lines.insert(insertAt + 1, newLine1)
        with open(self.WORKOUT_FILEDIR, "w") as f:
            f.writelines(lines)
            
        
        self.EXER_NAME = exerName
        self.EXER_WRITE_AT = self.exerExistsWriteLoc(exerName)
        self.updatePrompt()
    
    def logSet(self, reps, weight):
        with open(self.WORKOUT_FILEDIR, "r") as f:
            lines = f.readlines()
        
        newLine = SET_KEYWORD + f" {reps} @ {weight} {self.UNIT_ABBR}\n"
        lines.insert(self.EXER_WRITE_AT, newLine)

        with open(self.WORKOUT_FILEDIR, "w") as f:
            f.writelines(lines)
    
    ### BEGIN HELP FXNS ###
    ### BEGIN HELP FXNS ###
    ### BEGIN HELP FXNS ###

    def help_begin(self):
        print("Begin a new workout. Optionally provide a title.")
        print("Usage: begin [title]")
        print("Alias: b")

    def help_init(self):
        print("Initialize the workouts directory.")
        print("Usage: init [y/n]")

    def help_continue(self):
        print("Resume a recent workout or exercise within current workout.")
        print("Usage: continue [exercise_name]")
        print("Alias: c, cont")

    def help_exit(self):
        print("Step back in hierarchy (exercise → workout → shell) or exit.")
        print("Alias: done, d, q, EOF")

    def help_log(self):
        print("Begin logging an exercise. Creates new or resumes existing.")
        print("Usage: log <exercise-name>")

    def help_list(self):
        print("List workouts. Optionally pass a number to limit results.")
        print("Usage: list [n]")

    def help_last(self):
        print("Show last N instances of current exercise.")
        print("Usage: last [n]")

    def help_set_unit(self):
        print("Set weight unit to kilos or pounds.")
        print("Usage: set_unit <k/kg/kilo | p/lb/lbs/pound>")

    def help_summary(self):
        print("Print full contents of current workout file.")
        print("Usage: summary")
        print("Alias: sum")

    def help_history(self):
        print("Get history of all workouts for a given exercise.")
        print("Usage: history [exercise_name]")
        print("Alias: hist, h")
    
    help_b = help_begin
    help_c = help_cont = help_continue
    help_d = help_done = help_q = help_EOF = help_exit
    help_s = help_sum = help_summary
    help_set = help_set_unit

if __name__ == "__main__":
    try:
        ExerThing().cmdloop()
    except KeyboardInterrupt:
        print("\nExiting!")