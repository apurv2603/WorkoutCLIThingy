"""
Converts parsed Workout objects to HTML output.
"""
from parser import parse, Workout, Exercise, SuperSet, SetEntry, MuscleGroup, Note
from pathlib import Path
import html

def workout_to_html(workout: Workout) -> str:
    """Convert a Workout object to an HTML string."""

    parts = []

    # HTML header
    parts.append("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        * {{
            box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background: linear-gradient(180deg, #0a0e1a 0%, #111827 100%);
            min-height: 100vh;
            color: #e2e8f0;
        }}
        .workout-header {{
            background: linear-gradient(135deg, #1e3a5f 0%, #0ea5e9 50%, #06b6d4 100%);
            color: white;
            padding: 25px;
            border-radius: 16px;
            margin-bottom: 25px;
            box-shadow: 0 0 30px rgba(14, 165, 233, 0.3), 0 4px 20px rgba(0, 0, 0, 0.4);
            border: 1px solid rgba(56, 189, 248, 0.2);
        }}
        .workout-header h1 {{
            margin: 0 0 12px 0;
            font-size: 1.8em;
            text-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
        }}
        .workout-meta {{
            display: flex;
            gap: 20px;
            flex-wrap: wrap;
            font-size: 0.9em;
            opacity: 0.95;
        }}
        .exercise {{
            background: linear-gradient(145deg, #1e293b 0%, #0f172a 100%);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 15px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(56, 189, 248, 0.15);
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        .exercise:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(14, 165, 233, 0.2), inset 0 1px 0 rgba(255, 255, 255, 0.05);
        }}
        .exercise h2 {{
            margin: 0 0 12px 0;
            color: #38bdf8;
            font-size: 1.3em;
            text-shadow: 0 0 20px rgba(56, 189, 248, 0.3);
        }}
        .muscle-groups {{
            display: flex;
            gap: 8px;
            margin-bottom: 15px;
            flex-wrap: wrap;
        }}
        .muscle-tag {{
            background: linear-gradient(135deg, #0c4a6e 0%, #0369a1 100%);
            color: #7dd3fc;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.8em;
            font-weight: 600;
            border: 1px solid rgba(56, 189, 248, 0.3);
            box-shadow: 0 2px 8px rgba(14, 165, 233, 0.2);
        }}
        .sets-table {{
            width: 100%;
            border-collapse: collapse;
        }}
        .sets-table th, .sets-table td {{
            padding: 12px 15px;
            text-align: left;
            border-bottom: 1px solid rgba(56, 189, 248, 0.1);
        }}
        .sets-table th {{
            background: rgba(14, 165, 233, 0.1);
            font-weight: 600;
            color: #38bdf8;
            font-size: 0.85em;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .sets-table td {{
            color: #cbd5e1;
        }}
        .sets-table tr:hover td {{
            background: rgba(14, 165, 233, 0.05);
        }}
        .sets-table tr:last-child td {{
            border-bottom: none;
        }}
        .superset {{
            background: linear-gradient(135deg, #1e1b4b 0%, #312e81 100%);
            border-radius: 16px;
            padding: 20px;
            margin-bottom: 15px;
            border: 1px solid rgba(129, 140, 248, 0.3);
            box-shadow: 0 0 25px rgba(99, 102, 241, 0.15), 0 4px 15px rgba(0, 0, 0, 0.3);
        }}
        .superset-label {{
            font-weight: bold;
            color: #a5b4fc;
            margin-bottom: 15px;
            font-size: 0.85em;
            text-transform: uppercase;
            letter-spacing: 2px;
            text-shadow: 0 0 15px rgba(165, 180, 252, 0.5);
        }}
        .superset .exercise {{
            margin-bottom: 12px;
            background: linear-gradient(145deg, #1e1b4b 0%, #0f0d2e 100%);
            border-color: rgba(129, 140, 248, 0.2);
        }}
        .superset .exercise:last-child {{
            margin-bottom: 0;
        }}
        .superset .exercise h2 {{
            color: #a5b4fc;
        }}
        .notes {{
            background: linear-gradient(145deg, #172554 0%, #1e3a8a 100%);
            border-left: 4px solid #3b82f6;
            padding: 20px;
            border-radius: 0 12px 12px 0;
            margin-top: 25px;
            box-shadow: 0 4px 15px rgba(59, 130, 246, 0.2);
        }}
        .notes h3 {{
            margin: 0 0 12px 0;
            color: #60a5fa;
            text-shadow: 0 0 15px rgba(96, 165, 250, 0.4);
        }}
        .notes ul {{
            margin: 0;
            padding-left: 20px;
        }}
        .notes li {{
            margin-bottom: 8px;
            color: #93c5fd;
        }}
    </style>
</head>
<body>
""".format(title=html.escape(workout.name or f"Workout - {workout.date}")))

    # Workout header
    name_display = html.escape(workout.name) if workout.name else "Workout"
    parts.append(f'<div class="workout-header">')
    parts.append(f'    <h1>{name_display}</h1>')
    parts.append(f'    <div class="workout-meta">')
    parts.append(f'        <span><strong>Date:</strong> {html.escape(workout.date)}</span>')
    if workout.time:
        parts.append(f'        <span><strong>Time:</strong> {html.escape(workout.time)}</span>')
    parts.append(f'        <span><strong>Unit:</strong> {html.escape(workout.unit)}</span>')
    parts.append(f'    </div>')
    parts.append(f'</div>')

    # Exercises and supersets
    for item in workout.items:
        if isinstance(item, SuperSet):
            parts.append(_superset_to_html(item, workout.unit))
        elif isinstance(item, Exercise):
            parts.append(_exercise_to_html(item, workout.unit))

    # Notes
    if workout.notes:
        parts.append('<div class="notes">')
        parts.append('    <h3>Notes</h3>')
        parts.append('    <ul>')
        for note in workout.notes:
            parts.append(f'        <li>{html.escape(note.text)}</li>')
        parts.append('    </ul>')
        parts.append('</div>')

    # Close HTML
    parts.append('</body>')
    parts.append('</html>')

    return '\n'.join(parts)


def _exercise_to_html(exercise: Exercise, default_unit: str) -> str:
    """Convert an Exercise to HTML."""
    lines = []
    lines.append('<div class="exercise">')
    lines.append(f'    <h2>{html.escape(exercise.name)}</h2>')

    # Muscle groups
    if exercise.muscle_groups:
        lines.append('    <div class="muscle-groups">')
        for mg in exercise.muscle_groups:
            lines.append(f'        <span class="muscle-tag">{html.escape(mg.name)}</span>')
        lines.append('    </div>')

    # Sets table
    if exercise.sets:
        lines.append('    <table class="sets-table">')
        lines.append('        <thead>')
        lines.append('            <tr>')
        lines.append('                <th>Set</th>')
        lines.append('                <th>Reps</th>')
        lines.append('                <th>Weight</th>')
        lines.append('            </tr>')
        lines.append('        </thead>')
        lines.append('        <tbody>')
        for i, s in enumerate(exercise.sets, 1):
            unit = s.unit if s.unit else default_unit
            weight_display = f"{s.weight:g} {html.escape(unit)}"
            lines.append('            <tr>')
            lines.append(f'                <td>{i}</td>')
            lines.append(f'                <td>{s.reps}</td>')
            lines.append(f'                <td>{weight_display}</td>')
            lines.append('            </tr>')
        lines.append('        </tbody>')
        lines.append('    </table>')

    lines.append('</div>')
    return '\n'.join(lines)


def _superset_to_html(superset: SuperSet, default_unit: str) -> str:
    """Convert a SuperSet to HTML."""
    lines = []
    lines.append('<div class="superset">')
    lines.append('    <div class="superset-label">SUPERSET</div>')
    for exercise in superset.exercises:
        lines.append(_exercise_to_html(exercise, default_unit))
    lines.append('</div>')
    return '\n'.join(lines)


OUTPUT_DIR = Path("renders")


def parse_to_html(file_path: str, output_path: str = None) -> str:
    """
    Parse a .workout file and convert it to HTML.

    Args:
        file_path: Path to the .workout file
        output_path: Optional path to write HTML output. If None, outputs to renders folder.

    Returns:
        The generated HTML string.
    """
    workout = parse(file_path)
    html_content = workout_to_html(workout)
    
    if output_path is None:
        OUTPUT_DIR.mkdir(exist_ok=True)
        input_path = Path(file_path)
        output_path = OUTPUT_DIR / input_path.with_suffix('.html').name
    
    Path(output_path).write_text(html_content)
    return html_content


def render_and_open(file_path: str, output_path: str = None) -> Path:
    """
    Parse a .workout file, convert to HTML, and open in browser.

    Args:
        file_path: Path to the .workout file
        output_path: Optional path to write HTML output.

    Returns:
        Path to the generated HTML file.
    """
    import webbrowser

    parse_to_html(file_path, output_path)

    if output_path is None:
        input_path = Path(file_path)
        output_path = OUTPUT_DIR / input_path.with_suffix('.html').name
    
    print("path: ", output_path, "outputdir: ", OUTPUT_DIR)
    output_path = Path(output_path).resolve()
    webbrowser.open(f"file://{output_path}")
    return output_path


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python parse_to_html.py <workout_file> [output_file] [--open]")
        sys.exit(1)

    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    flags = [a for a in sys.argv[1:] if a.startswith('--')]

    input_file = args[0]
    output_file = args[1] if len(args) > 1 else None

    if '--open' in flags:
        output_path = render_and_open(input_file, output_file)
        print(f"Opened: {output_path}")
    else:
        html_output = parse_to_html(input_file, output_file)
        output_path = output_file if output_file else OUTPUT_DIR / Path(input_file).with_suffix('.html').name
        print(f"Generated HTML: {output_path}")
