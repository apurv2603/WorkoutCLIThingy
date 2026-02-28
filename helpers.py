from datetime import datetime
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

def parse_date(s):
    parts = s.split('_')
    return datetime.strptime(f"{parts[0]}_{parts[1]}_{parts[2]}", "%m_%d_%y")
