# Keywords:
-  `# `: Exercise name
    - this will be a child of a root node
    - it can have `>` or `note` as children

- `>`: Set

- `@`: seperator for weight and reps
    -format: reps@weight
    -example: 12@30 means 12 reps and 30 kg

- `##`:Superset
    - Its needs at least two children
    - each child is denoted with a `###`

- `###`: Supetset exercise
    -it will have `>` as children which represents the metric for
    that set

- `#`: Muscle group
    - Hashtag no space
    - no chilren is a leaf node 
    - only one muscle group per `!`

- `$`: Header Separator. (CHANGE?? - AJT)
    - `$` Name
    - `$$` Unit
    - `$$$` HH:MM Time
