"""
process_file.py — Part 2: one file of package descriptions, uploaded.

A Streamlit app that accepts an uploaded text file with one package description
per line, shows the total for every line, and writes the parsed packages to a
JSON file in the `data/` folder — `data/packaging1.txt` in, `data/packaging1.json`
out.

New here: an uploaded file arrives as **bytes**, not text, so it has to be
decoded before it can be split into lines. And a text file usually ends with a
newline, so the last "line" is empty and must be skipped rather than parsed.

Run it:  Run and Debug -> "Streamlit Run: Current File"   (see README Reference #1)
Test it: pytest tests/test_streamlit.py -k process_file
"""

# --- The page ---------------------------------------------------------------------
#
# Less scaffolding this time. The steps are described, but which widget and which
# function does each job — and what to call the result — is now yours to work out.
# `one_package.py` is your worked example for anything structural, and README
# Reference #4 and #5 cover the two things that are new here.

# TODO: imports — streamlit, json, and what you need from packaging_parser.
import streamlit as st
import json
from packaging_parser import calc_total_units, get_unit, parse_packaging

# TODO: the title, exactly:   Process File of Packages
st.title("Process File of Packages")

# key="package_file"

uploaded_file = st.file_uploader("Upload package file:", key="package_file")
if uploaded_file:
    packages = []
    text = uploaded_file.getvalue().decode("utf-8")
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        parsed_line = parse_packaging(line)
        packages.append(parsed_line)
        st.info(f"{line} ➡️ Total 📦 Size: {calc_total_units(parsed_line)} {get_unit(parsed_line)}")
    file_name = uploaded_file.name.split(".")[0]
    with open(f"data/{file_name}.json", "w") as json_file:
        json.dump(packages, json_file, indent=4)
    st.success(f"{len(packages)} packages written to data/{file_name}.json")
