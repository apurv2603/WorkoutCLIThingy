import cmd
from helpers import *
import os
import datetime

promptDefault = "ExerThing"
class ExerThing(cmd.Cmd):
    prompt = promptDefault + "> "
    WORKOUT_DIR = None
    WORKOUT_FILEDIR = None
    WORKOUT_FNAME = None

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
        print(my_intro)
    
    def promptLvl2(self):
        lst = self.WORKOUT_FNAME.split(':')
        word2 = ""
        if len(lst) > 1:
            word2 = "*" +lst[-1].split(".")[0]
        else:
            word2 = self.WORKOUT_FNAME.split(".")[0]
        return f"{promptDefault}/{word2}> "
    
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
            with open(self.WORKOUT_FILEDIR, "w") as f:
                f.write(f"{local_name}\n")
            print(f"Started workout \"{local_name}\"!")
            self.WORKOUT_ABBR = user_title if user_title else dt
            self.prompt = self.promptLvl2()
    do_b = do_begin

    def do_continue(self, arg):
        # Resume Exercise
        files = os.listdir(self.WORKOUT_DIR) if self.WORKOUT_DIR is not None else []
        N = len(files)
        if N == 0:
            print("No workouts found in workouts directory. Use 'begin' or 'begin <workout_name>' to start a workout.")
            return
        files.sort(key=lambda f: datetime.datetime.strptime((f.split(".")[0]).split(":")[0], "%m_%d_%Y"), reverse=True)
        files = files[:5]
        for i in range(len(files)):
            print(f"[{i}] {files[i]}")        
        choice = input("Enter workout number: ")
        if choice.isdigit() and int(choice) in range(len(files)):
            self.WORKOUT_FILEDIR = os.path.join(self.WORKOUT_DIR, files[int(choice)])
            self.WORKOUT_FNAME = files[int(choice)]
            self.prompt = self.promptLvl2()
            print(f"Resumed workout \"{self.WORKOUT_FNAME}\"!")
        else:
            print("Continue Cancelled.")
    do_c = do_cont = do_continue

    def do_log(self, arg):
        # Begin log exercise
        if self.testDirIsNull() or self.testWorkoutIsNull():
            return
        exerName = parse_exer(arg)
        print("Log ", exerName)
    
    def do_last(self, arg):
        # Get last case of exercise ARG[0]
        if self.testDirIsNull() or self.testWorkoutIsNull():
            return
        num = parse_num(arg)
        print("Last ", num)
    
    def do_set(self, arg):
        if self.testDirIsNull() or self.testWorkoutIsNull():
            return
        if arg is None or arg.strip() == "":
            print("No unit provided, use 'kilo' or 'pound'")
            return
        arg0 = arg.strip().lower()
        if arg0 == "k" or arg0 == "kilo" or arg0 == "kilos":
            print("Set to kilos")
            return
        if arg0 == "p" or arg0 == "pound" or arg0 == "pounds":
            print("Set to pounds")
            return
        else:
            print("Unknown unit, use 'k/kilos' or 'p/pounds'")
    
    def do_summary(self, arg):
        # Get last ARG[0] workout, If Arg[0] is None, Arg = 0
        if self.testDirIsNull() or self.testWorkoutIsNull():
            return
        num = parse_num(arg)
        print("Summary, ", num)
    do_sum = do_summary
    
    def do_exit(self, arg):
        # Take a step down in the hierarchy, or exit if at base level
        if self.WORKOUT_FILEDIR is not None:
            self.WORKOUT_FILEDIR = None
            self.WORKOUT_FNAME = None
            self.prompt = promptDefault + "> "
            print("Leaving Workout...")
        else:
            print("Exiting...")
            return True  # Returning True exits the loop
    do_EOF = do_q = do_exit

    def emptyline(self):
        # On enter reshow prompt and do nothing
        pass

    def testDirIsNull(self):
        if self.WORKOUT_DIR is None:
            print("Must initialize workout directory with 'init' first!")
            return True
        else:
            return False
    
    def testWorkoutIsNull(self):
        if self.WORKOUT_FILEDIR is None:
            print("Must begin a workout with 'begin' first!")
            return True
        else:
            return False
    
if __name__ == "__main__":
    try:
        ExerThing().cmdloop()
    except KeyboardInterrupt:
        print("\nExiting!")