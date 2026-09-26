"""
packaging_parser.py — a module for parsing packaging data.  *(This module is provided for you.)*

You do not write this module; you **use** it. All three Streamlit apps in this
assignment import it and call its three functions. That is the normal case in
real work — most of the code you build on is code somebody else wrote — and it
makes this assignment about the *user interface*, not about parsing strings.

Read it before you start. The docstrings tell you exactly what each function
takes and what it gives back, which is everything your apps need to know.

A **package description** is a string like:

    "12 eggs in 1 carton / 3 cartons in 1 box"

Read it left to right: 12 eggs go in a carton, and 3 cartons go in a box. Each
"N things in 1 container" is one **level** of packaging, and levels are separated
by " / ". A description can have one level or many.

    python code/packaging_parser.py        # runs the demo at the bottom of this file
"""


def parse_packaging(packaging_data: str) -> list[dict]:
    """Parse one package description into a list of levels, outermost last.

    Each level is a one-item dictionary, {name: quantity}. The order of the list
    is the order the levels appear in the string, so the *first* entry is the
    smallest unit (the thing being packaged) and the *last* entry is the
    outermost container, which always has a quantity of 1.

    Examples:

        parse_packaging("12 eggs in 1 carton")
        [{'eggs': 12}, {'carton': 1}]

        parse_packaging("6 bars in 1 pack / 12 packs in 1 carton")
        [{'bars': 6}, {'packs': 12}, {'carton': 1}]

        parse_packaging("20 pieces in 1 pack / 10 packs in 1 carton / 4 cartons in 1 box")
        [{'pieces': 20}, {'packs': 10}, {'cartons': 4}, {'box': 1}]

    Names may be more than one word ("30 tablets in 1 blister pack") — everything
    after the number is the name. A description that does not follow the pattern
    (no number where one is expected, an empty string) raises a ValueError.
    """
    package = []
    levels = packaging_data.split("/")

    for level in levels:
        # "12 eggs in 1 carton" -> the left side, "12 eggs", is this level
        left_side = level.split(" in ")[0]
        package.append(_parse_item(left_side))

    # The right side of the LAST level, "1 box", is the outermost container.
    right_side = levels[-1].split(" in ")[-1]
    package.append(_parse_item(right_side))

    return package


def _parse_item(item: str) -> dict:
    """Turn "12 eggs" into {'eggs': 12}. Internal helper — the apps never call it."""
    words = item.split()
    if len(words) < 2 or not words[0].isdigit():
        raise ValueError(f"expected '<number> <name>', got {item.strip()!r}")
    quantity = int(words[0])
    name = " ".join(words[1:])
    return {name: quantity}


def calc_total_units(package: list[dict]) -> int:
    """Multiply every level's quantity together — the total number of units inside.

    Examples:

        calc_total_units([{'bars': 6}, {'packs': 12}, {'carton': 1}])
        72                      # 6 * 12 * 1

        calc_total_units([{'pieces': 20}, {'packs': 10}, {'cartons': 4}, {'box': 1}])
        800                     # 20 * 10 * 4 * 1
    """
    total = 1
    for level in package:
        total *= list(level.values())[0]
    return total


def get_unit(package: list[dict]) -> str:
    """The name of the smallest unit — the first level's name.

    Examples:

        get_unit([{'bars': 6}, {'packs': 12}, {'carton': 1}])
        'bars'

        get_unit([{'pieces': 20}, {'packs': 10}, {'cartons': 4}, {'box': 1}])
        'pieces'
    """
    return list(package[0].keys())[0]


# This block only runs when you run this file directly (python code/packaging_parser.py
# or "Python Debugger: Current File"). It does NOT run when an app imports the
# module. Use it to try the functions out, or to step through them in the debugger.
if __name__ == "__main__":
    text = "25 balls in 1 bucket / 4 buckets in 1 bin"
    package = parse_packaging(text)
    print(package)

    total = calc_total_units(package)
    unit = get_unit(package)
    print(f"{total} {unit} total")
