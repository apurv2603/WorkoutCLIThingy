import cmd

class ExerThing(cmd.Cmd):
    prompt = "ExerThing> "
    intro = "Welcome to ExerThing! Type help or ? to list commands.\n"

    def do_log(self, arg):
        # Begin log exercise
        exerName = parse_exer(arg)
        print("Log ", exerName)

    def do_last(self, arg):
        # Get last case of exercise ARG[0]
        num = self.parse_num(arg)
        print("Last ", num)
    
    def do_set(self, arg):
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
        # Get last ARG[0] workout
        # If Arg[0] is None, Arg = 0
        num = self.parse_num(arg)
        print("Summary, ", num)
    def do_sum(self, arg):
        self.do_summary(arg)
    
    def do_exit(self, arg):
        # EXIT SHELL
        print("Goodbye!")
        return True  # Returning True exits the loop
    def do_q(self, arg):
        self.do_exit(arg)

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
        argExer = arg.split(" ")[0]
        try: 
            exer = argExer.lower()
        except Exception:
            pass
    return exer

if __name__ == "__main__":
    ExerThing().cmdloop()