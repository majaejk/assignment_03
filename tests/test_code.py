"""Code structure tests — read each app's source and check it is built the right way.

The Streamlit tests in test_streamlit.py check what the page *says*. These check
*how it was built*: that the apps import the modules they are supposed to, call
the functions they are supposed to call, and use the widgets the assignment asks
for. A page can say the right thing for the wrong reasons — parsing the string
by hand instead of calling `parse_packaging`, say — and this is the file that
notices.

The checks read the **parsed** source (Python's `ast` module), not the text. A
function named in a comment or a docstring does not count as having been called,
and a call cannot hide behind a comment either. If a test here fails, the message
names the exact import, call or widget it was looking for.
"""

import ast

from helpers import repo_path

ONE_PACKAGE = "code/one_package.py"
PROCESS_FILE = "code/process_file.py"
PROCESS_FILES = "code/process_files.py"

PARSER_FUNCTIONS = ("parse_packaging", "calc_total_units", "get_unit")


# --- Reading the source ------------------------------------------------------------


def parse(script: str) -> ast.Module:
    with open(repo_path(script), encoding="utf-8") as source_file:
        return ast.parse(source_file.read(), filename=script)


def imported_modules(tree: ast.Module) -> set[str]:
    """Top-level names of every module the file imports, however it imports them.

    `import streamlit as st`, `import json` and `from packaging_parser import ...`
    contribute "streamlit", "json" and "packaging_parser".
    """
    modules = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.add(node.module.split(".")[0])
    return modules


def called_names(tree: ast.Module) -> set[str]:
    """The name of every function called, whichever way it was reached.

    `parse_packaging(line)` and `packaging_parser.parse_packaging(line)` both
    contribute "parse_packaging"; `st.text_input(...)` contributes "text_input";
    `json.dump(...)` contributes "dump".
    """
    names = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if isinstance(node.func, ast.Name):
            names.add(node.func.id)
        elif isinstance(node.func, ast.Attribute):
            names.add(node.func.attr)
    return names


def defined_functions(tree: ast.Module) -> set[str]:
    return {node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)}


def uses_session_state(tree: ast.Module) -> bool:
    """True if `session_state` is touched anywhere — `st.session_state.count`,
    `st.session_state["count"]`, `"count" in st.session_state`, all count."""
    return any(
        isinstance(node, ast.Attribute) and node.attr == "session_state"
        for node in ast.walk(tree)
    )


# --- What every app must do --------------------------------------------------------


def check_uses_the_parser_module(script: str, functions: tuple[str, ...]) -> None:
    """The app imports packaging_parser and calls its functions — it does not
    parse the string itself, and it does not paste the module's code in."""
    tree = parse(script)

    assert "packaging_parser" in imported_modules(tree), (
        f"{script} should import the parser, e.g. "
        "`from packaging_parser import parse_packaging, calc_total_units, get_unit`"
    )
    assert "streamlit" in imported_modules(tree), (
        f"{script} is a Streamlit app — it should `import streamlit as st`"
    )

    called = called_names(tree)
    for name in functions:
        assert name in called, f"{script} should call {name}() from packaging_parser"

    copied = defined_functions(tree) & set(PARSER_FUNCTIONS)
    assert not copied, (
        f"{script} defines {sorted(copied)} itself — import them from packaging_parser instead"
    )
    assert "input" not in called, (
        f"{script} calls input() — a web app reads from widgets, not the console"
    )


# --- Part 1: one_package.py --------------------------------------------------------


def test_one_package_uses_the_parser_module():
    """Imports packaging_parser and streamlit; calls all three parser functions."""
    check_uses_the_parser_module(ONE_PACKAGE, PARSER_FUNCTIONS)


def test_one_package_uses_the_right_widgets():
    """A title and a text box in; results out through Streamlit, not print()."""
    called = called_names(parse(ONE_PACKAGE))

    assert "title" in called, f"{ONE_PACKAGE} should call st.title(...)"
    assert "text_input" in called, f"{ONE_PACKAGE} should read the description with st.text_input(...)"
    assert "file_uploader" not in called, f"{ONE_PACKAGE} takes one typed description, not a file"
    assert "print" not in called, (
        f"{ONE_PACKAGE} calls print() — that goes to the terminal, not the page. "
        "Use an output widget such as st.info or st.success."
    )


# --- Part 2: process_file.py -------------------------------------------------------


def test_process_file_uses_the_parser_module():
    """Imports packaging_parser and streamlit; calls all three parser functions."""
    check_uses_the_parser_module(PROCESS_FILE, PARSER_FUNCTIONS)


def test_process_file_uploads_and_writes_json():
    """A file uploader in; json.dump to an opened file out."""
    tree = parse(PROCESS_FILE)
    called = called_names(tree)

    assert "file_uploader" in called, f"{PROCESS_FILE} should read the file with st.file_uploader(...)"
    assert "decode" in called, (
        f"{PROCESS_FILE} should decode the upload — it arrives as bytes, "
        "e.g. uploaded_file.getvalue().decode('utf-8')"
    )
    assert "json" in imported_modules(tree), f"{PROCESS_FILE} should `import json`"
    assert "dump" in called, f"{PROCESS_FILE} should write the packages with json.dump(...)"
    assert "open" in called, f"{PROCESS_FILE} should open() the JSON file for writing"
    assert "print" not in called, f"{PROCESS_FILE} calls print() — use an output widget instead"


# --- Part 3: process_files.py ------------------------------------------------------


def test_process_files_uses_the_parser_module():
    """Imports packaging_parser and streamlit; calls parse_packaging.

    Only parse_packaging is required here: the summary is a count of packages,
    so this app has no need to total anything — but calling the other two does no harm.
    """
    check_uses_the_parser_module(PROCESS_FILES, ("parse_packaging",))


def test_process_files_uploads_and_writes_json():
    """The same upload-decode-dump chain as process_file.py."""
    tree = parse(PROCESS_FILES)
    called = called_names(tree)

    assert "file_uploader" in called, f"{PROCESS_FILES} should read the file with st.file_uploader(...)"
    assert "decode" in called, f"{PROCESS_FILES} should decode the upload from bytes to text"
    assert "json" in imported_modules(tree), f"{PROCESS_FILES} should `import json`"
    assert "dump" in called, f"{PROCESS_FILES} should write the packages with json.dump(...)"
    assert "open" in called, f"{PROCESS_FILES} should open() the JSON file for writing"


def test_process_files_remembers_with_session_state():
    """A button triggers the work; session_state keeps the counts; st.metric shows them.

    An ordinary variable is reset on every rerun. The only way the count from a
    previous upload can still be there is `st.session_state`, so its absence means
    the app cannot be accumulating anything.
    """
    tree = parse(PROCESS_FILES)
    called = called_names(tree)

    assert "button" in called, f"{PROCESS_FILES} should process on an st.button(...) click"
    assert uses_session_state(tree), (
        f"{PROCESS_FILES} never touches st.session_state — nothing it counts can "
        "survive a rerun. See README Reference #6."
    )
    assert "metric" in called, (
        f"{PROCESS_FILES} should show the running totals with st.metric(...)"
    )
    assert "print" not in called, f"{PROCESS_FILES} calls print() — use an output widget instead"
