"""
one_package.py — Part 1: one package description, typed in.

A Streamlit app that asks for a single package description, parses it with the
`packaging_parser` module, and shows each level of packaging plus the total number of
units inside.

This is the smallest possible Streamlit app that does real work, and it exists to
teach one thing: a Streamlit script runs **top to bottom on every interaction**.
When the page first opens, the text box is empty — and your code still runs. So
the work has to sit behind a guard: only parse when there is something to parse.

Run it:  Run and Debug -> "Streamlit Run: Current File"   (see README Reference #1)
Test it: pytest tests/test_streamlit.py -k one_package
"""

import streamlit as st

# TODO: import the three functions this app needs from packaging_parser. Put the
#       import here, under `import streamlit as st`:
#
#       from packaging_parser import calc_total_units, get_unit, parse_packaging


# --- The page ---------------------------------------------------------------------
#
# These two lines are GIVEN to you, in this app only. Read them: st.title draws the
# heading, and st.text_input draws the box AND RETURNS whatever is in it. On the
# very first run, before anyone has typed, that is an empty string — and the rest
# of this script runs anyway. See README Reference #2 and #3.

st.title("Process One Package")

package_data = st.text_input(
    "Enter package data:",
    key="package_data",
    placeholder="12 eggs in 1 carton / 3 cartons in 1 box",
)

# --- The work ---------------------------------------------------------------------
#
# Fill in each TODO below, in order. This first app names the exact function to
# call and what to store it in; the second app will describe the steps and leave the
# calls to you; the third gives you neither.

# TODO: guard the work — an `if` on package_data, so that nothing below runs while
#       the text box is empty. Everything that follows is indented inside it.

    # 1. Parse.
    #    TODO: call parse_packaging(package_data) and store the result in `package`.

    # 2. Total.
    #    TODO: call calc_total_units(package) and store it in `total`.
    #    TODO: call get_unit(package) and store it in `unit`.

    # 3. Show each level. `package` is a list of one-item dictionaries, so a loop over
    #    it, and a loop over each item's .items(), gives you the name and quantity.
    #    TODO: for each level, st.info(f"{name} ➡️ {quantity}")

    # 4. Show the total.
    #    TODO: st.success(f"Total 📦 Size: {total} {unit}")
