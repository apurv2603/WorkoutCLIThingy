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


# Sometimes fixes mac autocomp. Sometimes breaks keyboard input.
try:
    import readline
    # readline.parse_and_bind("bind ^I rl_complete")
except ImportError:
    pass

# A = "#7a153d"
# B = "#b22b4e" 
# C = "#c53648"
# D = "#d94c3a"

# Z = "#f4e1c1"
# Y = "#f9c8a5"
# X = "#f6a76f"
# W = "#f57b2a"


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
    ruler = "="               # separator char in help

    def __init__(self):
        super().__init__()
        dirs = [d for d in os.listdir(".") if os.path.isdir(d)]
        if "workouts" in dirs:
            self.WORKOUT_DIR = os.path.join(os.getcwd(), "workouts")
        else:
            self.WORKOUT_DIR = None
        self.WORKOUT_FILEDIR = None
        self.WORKOUT_FNAME = None
        my_intro = "\n[orange3]Welcome to Exer[gold3]Thing[/gold3]![/orange3]"
        my_intro += " [green]Directory Initialized.[/green]" if self.WORKOUT_DIR is not None else " [red]Directory Not Initialized.[/red]"
        my_intro += " Type [cyan bold]help[/cyan bold] or [cyan bold]?[/cyan bold] to list commands."
        print("[bold]" +  my_intro + "[/bold]" )
    
    def default(self, line):
        if line.startswith("ls") or line.startswith("dir")  or line.startswith("pwd") or line.startswith("clear") or line.startswith("cat"):
            os.system(line)
            return
        # NOTES
        if line.startswith("//"):
            if self.addNotesLine(line[2:].strip()):
                print("[bold green]Added Note![/bold green]")
            else:
                print("[bold red]Failed to add note[/bold red]")
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
                try:
                    doCreate = input("No 'workouts' directory found. Create one? (y/n) ")
                except EOFError:
                    print("Cannot continue without workouts directory.")
                    return
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
        try:
            doCreate = input(f"Start Workout \"{local_name}\"? (y/n) ")
        except EOFError:
            print("Begin cancelled.")
            return
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
            try:
                choice = input("Enter exercise number: ") 
            except EOFError:
                print("Continue Exercise Cancelled.")
                return
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

        
        try:
            choice = input("Enter workout number: ")
        except EOFError:
            print("Continue Cancelled.")
            return
        
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
            try:
                choice = input(f"Exercise {exerName} already exists, continue? (y/n) ")
            except EOFError:
                print("Log cancelled.")
                return
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
        pass
    #     frequency()
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
            return False
        try:
            with open(self.WORKOUT_FILEDIR, "a") as f:
                f.write(f"// {line}\n")
        except Exception as e:
            return False
        return True
    
    def testDirIsNull(self):
        if self.WORKOUT_DIR is None:
            print("\nMust initialize workout directory with [cyan bold]init[/cyan bold] first!\n")
            return True
        else:
            return False
    
    def testWorkoutIsNull(self):
        if self.WORKOUT_FILEDIR is None:
            print("\nMust begin/continue a workout with [cyan bold]begin[/cyan bold] or [cyan bold]continue[/cyan bold]!\n")
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
        print("[bold]Begin a new workout.[/bold] Optionally provide a title.")
        print("[cyan]Usage:[/cyan] begin [orange3]<title>[/orange3]")
        print("[cyan]Alias:[/cyan] b")
        print("")

    def help_init(self):
        print("[bold]Initialize the workouts directory.[/bold]")
        print("[cyan]Usage:[/cyan] init [orange3]<y/n>[/orange3]")
        print("")

    def help_continue(self):
        print("[bold]Resume a recent workout or exercise within current workout.[/bold]")
        print("[cyan]Usage:[/cyan] continue [italic](Outside Workout)[/italic]")
        print("[cyan]Usage:[/cyan] continue [orange3]<exercise_name>[/orange3] [italic](Inside Workout)[/italic]")
        print("[cyan]Alias:[/cyan] c, cont")
        print("")

    def help_exit(self):
        print("[bold]Step back in hierarchy (exercise → workout → shell) or exit.[/bold]")
        print("[cyan]Alias:[/cyan] done, d, q, EOF")
        print("")

    def help_log(self):
        print("[bold]Begin logging an exercise.[/bold] Creates new or resumes existing.")
        print("[cyan]Usage:[/cyan] log [orange3]<exercise-name>[/orange3]")
        print("")

    def help_list(self):
        print("[bold]List workouts.[/bold] Optionally pass a number to limit results.")
        print("[cyan]Usage:[/cyan] list [orange3]<n>[/orange3]")
        print("")

    def help_last(self):
        print("[bold]Show last N instances of current exercise.[/bold]")
        print("[cyan]Usage:[/cyan] last [orange3]<n>[/orange3]")
        print("")

    def help_set_unit(self):
        print("[bold]Set weight unit to kilos or pounds.[/bold]")
        print("[cyan]Usage:[/cyan] set_unit [orange3] k/kg/kilo | p/lb/lbs/pound [/orange3]")
        print("")

    def help_summary(self):
        print("[bold]Print full contents of current workout file.[/bold]")
        print("[cyan]Usage:[/cyan] summary")
        print("[cyan]Alias:[/cyan] sum, s")
        print("")

    def help_history(self):
        print("[bold]Show history of all workouts for an exercise.[/bold]")
        print("[cyan]Usage:[/cyan] history [orange3]<exercise_name>[/orange3]")
        print("[cyan]Alias:[/cyan] hist, h")
        print("")

    def help_frequency(self):
        print("[bold]Get frequency of your workouts.[/bold]")
        print("[cyan]Usage:[/cyan] frequency")
        print("[cyan]Alias:[/cyan] freq, f")
        print("")

    def help_pr(self):
        print("[bold]Show all-time personal record for an exercise.[/bold]")
        print("[cyan]Usage:[/cyan] pr [orange3]<exercise_name>[/orange3]")
        print("")

    def help_help(self):
        self.do_help("")
    
    def do_help(self, arg):
        print("")
        if arg:
            # If specific command help is requested, use default behavior
            return super().do_help(arg)
        else:
            # Otherwise, show custom help message
            print("[bold underline]Available Commands:[/bold underline]")
            print(" - [cyan]init[/cyan]: Initialize workouts directory.")
            print(" - [cyan]begin [title][/cyan]: Start a new workout with optional title.")
            print(" - [cyan]continue [exercise_name][/cyan]: Resume a recent workout or exercise.")
            print(" - [cyan]log <exercise-name>[/cyan]: Begin logging an exercise.")
            print(" - [cyan]list [n][/cyan]: List workouts, optionally limit to n most recent.")
            print(" - [cyan]last [n][/cyan]: Show last n instances of current exercise.")
            print(" - [cyan]set_unit k/kg/p/kilo | p/lb/lbs/p/pound [/cyan]: Set weight unit.")
            print(" - [cyan]summary[/cyan]: Print full contents of current workout file.")
            print(" - [cyan]history <exercise_name>[/cyan]: Get history of all workouts for an exercise.")
            print(" - [cyan]pr <exercise_name>[/cyan]: Show all-time personal record for an exercise.")
            print(" - [cyan]frequency[/cyan]: Get frequency of your workouts.")
            print(" - [cyan]exit[/cyan]: Step back in hierarchy or exit.")
            print(" - [cyan]// <...>[/cyan]: Adds following information as a note to the workout file.")
            print("Type 'help <command>' for more details on a specific command.")
        print("")
    help_hist = help_h = help_history
    help_f = help_freq = help_frequency
    help_b = help_begin
    help_c = help_cont = help_continue
    help_d = help_done = help_q = help_EOF = help_exit
    help_s = help_sum = help_summary
    help_set = help_set_unit

    ## DO COMPLETE FXNS ##
    def complete_last(self, text, line, begidx, endidx):
        return [e for e in EXERCISE_LIST if e.startswith(text)]
    
    complete_pr = complete_history = complete_log = complete_last
    
    


if __name__ == "__main__":
    try:
        ExerThing().cmdloop()
    except KeyboardInterrupt:
        print("\nExiting!")