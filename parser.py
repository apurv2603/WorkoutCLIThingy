from __future__ import annotations
import re
from pathlib import Path
from typing import Optional, Union
WorkoutItem = Union["Exercise", "SuperSet"]
class SetEntry:
    def __init__(self, reps: int, weight: float, unit: str = None):
        self.reps = reps
        self.weight = weight
        self.unit = unit
         #TODO #SOEMTHINGSOMETHINSOMETHING
        # Has Rep, Weight, Unit
class Note:
    def __init__(self, text: str):
        self.text = text
    #string of notes
class MuscleGroup:
    def __init__(self, name: str):
        self.name = name
class Exercise:
    def __init__(self, name: str, sets: list[SetEntry], muscle_groups: list[MuscleGroup] = None):
        self.name = name
        self.sets = sets
        self.muscle_groups = muscle_groups if muscle_groups is not None else []    # Has Sets or Sup Sets, Has a muscle group(s) 

class SuperSet:
    #TODO
    def __init__(self, exercises: list[Exercise]):
        self.exercises = exercises

class Workout:
    #TODO
    def __init__(self, date: str , time: str, unit: str = "pounds", name: str = None, items: Optional[list[WorkoutItem]] = None, notes=None):
        self.name = name
        self.date = date
        self.time = time
        self.unit = unit
        self.items: list[WorkoutItem] = [] if items is None else items #this should be a list of exercises and supersets
        self.notes = notes if notes is not None else []
    # Has Name, Units, Time?, Has exercises

_SET_RE = re.compile(
    r"""^\s*>\s*
        (?P<reps>\d+)
        \s*@\s*
        (?P<weight>-?\d+(?:\.\d+)?)
        (?:\s*(?P<unit>[A-Za-z]+))?
        \s*$""",
    re.VERBOSE,
)

_HEADER_RE = re.compile(r"(\${1,3})\s*([^$]*)")

# -------------------------
# Helpers
# -------------------------
def _is_blank_or_comment(line: str) -> bool:
    s = line.strip()
    return (not s)

def _parse_filename_defaults(file_path: str) -> tuple[str | None, str | None]:
    """
    From: 02_28_2026:arms.workout
      date -> 02_28_2026
      name -> arms
    """
    fname = Path(file_path).name
    base = fname.split(".", 1)[0]  # "02_28_2026" or "02_28_2026:arms"
    base = base.strip()

    if ":" not in base:
        return base, None
    date_part, name_part = base.split(":", 1)
    date_part = date_part.strip() or None
    name_part = name_part.strip() or None
    return date_part, name_part

def _parse_header_line(line: str) -> dict:
    """
    Parses a single line that may contain:
      $   -> name
      $$  -> unit
      $$$ -> time
    Missing ones are ignored.
    """
    out: dict = {}
    for marker, raw_val in _HEADER_RE.findall(line.strip()):
        val = raw_val.strip()
        if not val:
            continue
        if marker == "$":
            out["name"] = val
        elif marker == "$$":
            out["unit"] = val
        elif marker == "$$$":
            out["time"] = val
    return out

def _parse_set_line(line: str) -> SetEntry:
    m = _SET_RE.match(line)
    if not m:
        raise ValueError(f"Bad set line (expected > reps@weight[unit]): {line!r}")
    reps = int(m.group("reps"))
    weight = float(m.group("weight"))
    unit = m.group("unit")
    return SetEntry(reps=reps, weight=weight, unit=unit)


# -------------------------
# Main parser
# -------------------------

def parse(file_path: str) -> Workout:
    text = Path(file_path).read_text()
    lines = text.splitlines()

    # Defaults from filename
    date_default, name_default = _parse_filename_defaults(file_path)

    # Create Workout root.
    # Your Workout __init__ expects (date, time, unit="pounds", name=None, items=None)
    # time might be missing; we allow None initially.
    workout = Workout(
        date=date_default if date_default else "unknown_date",
        time=None,
        unit="pounds",
        name=name_default,
        items=[],
    )

    # Parser state
    current_exercise: Optional[Exercise] = None
    current_superset: Optional[SuperSet] = None    
    in_superset = False

    # Consume first non-blank/comment line if it's a header containing '$'
    i = 0
    while i < len(lines) and _is_blank_or_comment(lines[i]):
        i += 1

    if i < len(lines) and "$" in lines[i]:
        hdr = _parse_header_line(lines[i])
        if "name" in hdr:
            workout.name = hdr["name"]
        if "unit" in hdr:
            workout.unit = hdr["unit"]
        if "time" in hdr:
            workout.time = hdr["time"]
        i += 1  # move past header line

    # Local constructors (ensure we don't hit your mutable default pitfalls)
    def _new_exercise(name: str) -> Exercise:
        # IMPORTANT: pass a fresh list so we never use Exercise's default [] shared list
        return Exercise(name=name, sets=[], muscle_groups=[])

    def _new_superset() -> SuperSet:
        return SuperSet(exercises=[])

    def _start_normal_exercise(name: str) -> None:
        nonlocal current_exercise, current_superset, in_superset
        in_superset = False
        current_superset = None
        ex = _new_exercise(name)
        workout.items.append(ex)
        current_exercise = ex

    def _start_superset() -> None:
        nonlocal current_exercise, current_superset, in_superset
        in_superset = True
        current_exercise = None
        ss = _new_superset()
        workout.items.append(ss)
        current_superset = ss

    def _start_superset_exercise(name: str) -> None:
        nonlocal current_exercise
        if not in_superset or current_superset is None:
            raise ValueError("Found '###' outside of a superset ('##').")
        ex = _new_exercise(name)
        current_superset.exercises.append(ex)
        current_exercise = ex

    # Parse remaining lines
    for line_no in range(i, len(lines)):
        raw = lines[line_no]
        if _is_blank_or_comment(raw):
            continue

        s = raw.strip()

        # Notes: "note ..." or "note: ..."
        if s.lower().startswith("//"):
            # Your classes do not store notes yet; ignore for now (per your current class set).
            # If you add notes later, we can attach it to workout/exercise/superset here.
            continue

        # Superset start
        if s.startswith("##") and not s.startswith("###"):
            _start_superset()
            continue

        # Superset exercise
        if s.startswith("###"):
            name = s[3:].strip()
            if not name:
                raise ValueError(f"Line {line_no+1}: empty superset exercise name.")
            _start_superset_exercise(name)
            continue

        # Normal exercise: "# " (hash + space)
        if s.startswith("# "):
            name = s[2:].strip()
            if not name:
                raise ValueError(f"Line {line_no+1}: empty exercise name.")
            _start_normal_exercise(name)
            continue

        # Muscle group: "#NoSpace" (hash with no following space)
        if s.startswith("#") and not s.startswith("# "):
            if current_exercise is None:
                raise ValueError(f"Line {line_no+1}: muscle group with no active exercise: {s!r}")
            mg_name = s[1:].strip()
            if not mg_name:
                raise ValueError(f"Line {line_no+1}: empty muscle group.")
            # You said one muscle group per exercise
            parts = s.split()  # split by whitespace
            for part in parts:
                if not part.startswith("#") or part.startswith("# "):
                    raise ValueError(f"Line {line_no+1}: invalid muscle group token: {part!r}")

                mg_name = part[1:].strip()
                if not mg_name:
                    raise ValueError(f"Line {line_no+1}: empty muscle group token in: {s!r}")
                current_exercise.muscle_groups.append(MuscleGroup(mg_name))
            continue
        # Set line: "> reps@weight"
        if s.startswith(">"):
            if current_exercise is None:
                raise ValueError(f"Line {line_no+1}: set with no active exercise: {s!r}")
            current_exercise.sets.append(_parse_set_line(s))
            continue
        if s.startswith("//"):
            text = s[2:].strip()
            # keep even empty notes if you want; usually better to skip empties
            if text:
                workout.notes.append(Note(text))
            continue

        raise ValueError(f"Line {line_no+1}: unrecognized syntax: {s!r}")

    # Validation: each superset must have >= 2 exercises
    for item in workout.items:
        if isinstance(item, SuperSet) and len(item.exercises) < 2:
            raise ValueError("Superset must contain at least 2 '###' exercises.")

    # Your Workout.items might be None if someone constructed it that way; normalize
    if workout.items is None:
        workout.items = []

    return workout


if __name__ == "__main__":
    w = parse("./workouts/02_28_2026:arms.workout")
    print("Workout:", w.name, w.date, w.unit, w.time)
    for it in w.items:
        if isinstance(it, SuperSet):
            print("SUPERSET:")
            for ex in it.exercises:
                mg = ex.muscle_groups[0].name if ex.muscle_groups else None
                print("  -", ex.name, "MG:", mg, "Sets:", [(se.reps, se.weight, se.unit) for se in ex.sets])
        else:
            mg = it.muscle_groups[0].name if it.muscle_groups else None
            print("EXERCISE:", it.name, "MG:", mg, "Sets:", [(se.reps, se.weight, se.unit) for se in it.sets])