from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from collections import Counter
import calendar

from rich.console import Console
from rich.table import Table
from rich.text import Text
from rich.panel import Panel
from rich.align import Align
from rich import box

console = Console()

# Tune these to match your vibe
DOT_COLOR = "bright_red"        # small dot
CHECK_COLOR = "dodger_blue1"    # checkmark
NUM_COLOR = "grey85"            # day numbers
FUTURE_NUM_COLOR = "grey50"     # future day numbers
BG_EMPTY = "grey11"             # background for no activity
BG_ACTIVE = "grey19"            # background for active day (subtle, not heat)
BG_FUTURE = "grey10"            # background for future days

def parse_mm_dd_yyyy(s: str) -> date | None:
    try:
        mm, dd, yyyy = s.split("_")
        return date(int(yyyy), int(mm), int(dd))
    except Exception:
        return None

def _cell(day_num: int, d: date | None, count: int, today: date) -> Text:
    if day_num == 0 or d is None:
        return Text("   \n   ")

    is_future = d > today
    bg = BG_FUTURE if is_future else (BG_ACTIVE if count > 0 else BG_EMPTY)

    t = Text()
    t.append(f"{day_num:>2}")
    t.append("\n")

    if is_future:
        t.append("  ")          # blank for future
    elif count > 0:
        t.append("✓")           # workout happened
    else:
        t.append("•")           # no workout

    t.stylize(f"on {bg}")
    t.stylize(FUTURE_NUM_COLOR if is_future else NUM_COLOR, 0, 2)

    last = len(t.plain) - 1
    if t.plain[last] == "•":
        t.stylize(DOT_COLOR, last, last + 1)
    elif t.plain[last] == "✓":
        t.stylize(CHECK_COLOR, last, last + 1)

    return t

def display_month_calendar_from_dates(
    date_strings: list[str],
    *,
    year: int | None = None,
    month: int | None = None,
):
    """Render one month calendar like your screenshot."""
    today = date.today()
    year = year if year is not None else today.year
    month = month if month is not None else today.month

    # Count occurrences per day (lets you do dot vs check thresholds, etc.)
    counts: Counter[date] = Counter()
    for s in date_strings:
        d = parse_mm_dd_yyyy(s)
        if d:
            counts[d] += 1

    cal = calendar.Calendar(firstweekday=6)  # Sunday-first
    weeks = cal.monthdatescalendar(year, month)

    table = Table(
        box=box.SIMPLE,
        show_header=True,
        header_style="grey70",
        show_edge=False,
        pad_edge=False,
    )

    for h in ["S", "M", "T", "W", "T", "F", "S"]:
        table.add_column(h, justify="center", no_wrap=True, width=3)

    for week in weeks:
        row = []
        for d in week:
            if d.month != month:
                row.append(Text("   \n   "))
            else:
                row.append(_cell(d.day, d, counts.get(d, 0), today))
        table.add_row(*row)

    title = f"{calendar.month_name[month]} {year}"
    console.print()
    console.print(Panel(Align.center(table), title=title, box=box.ROUNDED, style="grey37"))
    console.print()

# ---- CLI wiring idea ----
# If your CLI has workouts already parsed, do this:
#
# date_strings = [w.date for w in workouts]  # assuming w.date is "MM_DD_YYYY"
# display_month_calendar_from_dates(date_strings)

if __name__ == "__main__":
    # pick a month you can easily see (current month)
    today = date.today()
    y, m = today.year, today.month

    # fake “workout happened” dates (MM_DD_YYYY)
    test_dates = [
        f"{m:02d}_01_{y}",
        f"{m:02d}_02_{y}",
        f"{m:02d}_05_{y}",
        f"{m:02d}_05_{y}",  # duplicate doesn't matter for check vs dot
        f"{m:02d}_18_{y}",
    ]

    display_month_calendar_from_dates(test_dates, year=y, month=m)

    #ok so display_month_calendar_from_dates only displays it for the month m and year y, so for cli interaction
    #we want it to be for last x months so run this x times with keeping in mind that year might need to change