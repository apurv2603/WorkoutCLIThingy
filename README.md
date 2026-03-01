# WorkoutCLIThingy

# Improvements:
- Currently if someone does a regular version of an exercise they cant then do a seperate superset of that same exercise of even the opposite.
- What is a good action to deal with files that are entirely empty
-Need to force that workout items can only be Exercise or Superset objects
-we assume filenames cannot be created by user

useful functions:
- have a function so if you already did an exercise it will match your current string to an exercise that already
 exists

 # Command ideas
- `Summarize` prints the workout in a readable format
- `last X` returns last time exercise X was done and details of that exercise
 - `pr X` gives the pr for exercise X
-  `history X` prints history for exercise X



 - `progress X` prints a graph that plots weight lifted against time for exercise X
    - maybe this can be done be generating a png graph and then opening it to display
- some sort of command to see your consistency as a glance

# Ignored commands
- `muscles X.workout` prints the muscles groups used in session X
