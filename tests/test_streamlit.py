"""Streamlit tests — run each app the way a person would, and read the page.

These use `streamlit.testing.v1.AppTest`, which runs your script in-process with
no browser: it types into the text box, "uploads" a file, clicks the button, and
then looks at what the page says. No screenshots, no guessing — the same widgets
you see, read as data.

The tests check *what the page says*, not which widget said it, so st.info
versus st.success versus st.write is your call. What they do insist on:

- the app **starts quiet** — opening it does nothing until there is input
- the numbers and file names in the messages are right, for files the tests
  make up as well as the ones in data/
- the JSON files land in data/ with the right content
- process_files.py remembers across reruns and does not double-count

Each part's tests are independent, so finish Part 1 and its tests go green while
Parts 2 and 3 are still red. Run one part at a time with `-k`:

    pytest tests/test_streamlit.py -k one_package
"""

import os

import pytest

from helpers import (
    counts, data_file, load_app, no_exception, page_text, read_json, upload, widget,
)

ONE_PACKAGE = "code/one_package.py"
PROCESS_FILE = "code/process_file.py"
PROCESS_FILES = "code/process_files.py"

# Expected parse of data/packaging1.txt — what the apps must write to data/packaging1.json.
PACKAGING1_JSON = [
    [{"eggs": 12}, {"cartons": 3}, {"box": 1}],
    [{"baseballs": 12}, {"boxes": 12}, {"case": 1}],
    [{"cards": 52}, {"decks": 8}, {"shoes": 12}, {"casino": 1}],
]

# A file the tests invent, so the JSON cannot be produced by hand. Note the blank
# line in the middle and the newline at the end — a real text file has both.
FRUIT_TXT = "5 apples in 1 bag / 2 bags in 1 crate\n\n7 pens in 1 box\n"
FRUIT_JSON = [
    [{"apples": 5}, {"bags": 2}, {"crate": 1}],
    [{"pens": 7}, {"box": 1}],
]


@pytest.fixture(autouse=True)
def clean_json_outputs():
    """The apps write data/*.json; start and finish each test without any."""
    def remove_outputs():
        for name in os.listdir("data"):
            if name.endswith(".json"):
                os.remove(os.path.join("data", name))
    remove_outputs()
    yield
    remove_outputs()


# --- Part 1: one_package.py --------------------------------------------------------


def test_one_package_starts_quiet():
    """Opening the page shows the title and the text box, and nothing else.

    The text box is empty on the first run, and the script runs anyway. An app
    that parses unconditionally either crashes here or prints a total for a
    package that was never entered.
    """
    app = load_app(ONE_PACKAGE)
    no_exception(app, ONE_PACKAGE)

    assert "Process One Package" in page_text(app)
    widget(app.text_input, "package_data", "text_input")
    assert "Total" not in page_text(app), "nothing should be processed before any input"


def test_one_package_shows_each_level_and_the_total():
    """Typing a description shows every level and the total number of units."""
    app = load_app(ONE_PACKAGE)
    widget(app.text_input, "package_data", "text_input").set_value(
        "12 eggs in 1 carton / 3 cartons in 1 box"
    )
    app.run()
    no_exception(app, ONE_PACKAGE)

    text = page_text(app)
    for level in ("eggs", "cartons", "box"):
        assert level in text, f"the {level!r} level should be shown"
    assert "36 eggs" in text, "the total should be 36 eggs (12 * 3 * 1)"


def test_one_package_recomputes_for_new_input():
    """A new description gives a new answer — the page is computed, not typed in."""
    app = load_app(ONE_PACKAGE)

    widget(app.text_input, "package_data", "text_input").set_value(
        "25 balls in 1 bucket / 4 buckets in 1 bin"
    )
    app.run()
    assert "100 balls" in page_text(app)

    # Every run rebuilds the page, so look the text box up again before using it.
    widget(app.text_input, "package_data", "text_input").set_value(
        "6 bars in 1 pack / 12 packs in 1 carton"
    )
    app.run()
    no_exception(app, ONE_PACKAGE)
    text = page_text(app)
    assert "72 bars" in text
    assert "100 balls" not in text, "the previous answer should be gone after a rerun"


# --- Part 2: process_file.py -------------------------------------------------------


def test_process_file_starts_quiet():
    """Opening the page shows the title and the uploader, writes nothing, says nothing."""
    app = load_app(PROCESS_FILE)
    no_exception(app, PROCESS_FILE)

    assert "Process File of Packages" in page_text(app)
    widget(app.file_uploader, "package_file", "file_uploader")
    assert "written" not in page_text(app), "nothing should be processed before an upload"
    assert not [n for n in os.listdir("data") if n.endswith(".json")], "no JSON should be written yet"


def test_process_file_reports_every_line_and_writes_json():
    """Uploading data/packaging1.txt: one total per line, and the JSON file appears."""
    app = load_app(PROCESS_FILE)
    upload(app, "packaging1.txt", data_file("packaging1.txt"))
    app.run()
    no_exception(app, PROCESS_FILE)

    text = page_text(app)
    for total in ("36 eggs", "144 baseballs", "4992 cards"):
        assert total in text, f"the page should show the total {total!r}"
    assert "3 packages written to data/packaging1.json" in text

    assert read_json("packaging1.json") == PACKAGING1_JSON


def test_process_file_handles_a_file_it_has_never_seen():
    """A made-up file with a blank line and a trailing newline: 2 packages, not 3 or 4.

    `text.splitlines()` on a file that ends in a newline gives you an empty last
    line, and a blank line in the middle is empty too. Both must be skipped —
    parse_packaging raises on an empty string.
    """
    app = load_app(PROCESS_FILE)
    upload(app, "fruit.txt", FRUIT_TXT)
    app.run()
    no_exception(app, PROCESS_FILE)

    text = page_text(app)
    assert "10 apples" in text
    assert "7 pens" in text
    assert "2 packages written to data/fruit.json" in text
    assert read_json("fruit.json") == FRUIT_JSON


def test_process_file_counts_a_longer_file():
    """data/packaging3.txt has eight descriptions; every one is reported."""
    app = load_app(PROCESS_FILE)
    upload(app, "packaging3.txt", data_file("packaging3.txt"))
    app.run()
    no_exception(app, PROCESS_FILE)

    assert "8 packages written to data/packaging3.json" in page_text(app)
    assert len(read_json("packaging3.json")) == 8
    assert "1000000 mm" in page_text(app)


# --- Part 3: process_files.py ------------------------------------------------------


def test_process_files_starts_at_zero():
    """The two metric cards are on the page from the start, both reading 0."""
    app = load_app(PROCESS_FILES)
    no_exception(app, PROCESS_FILES)

    assert "Process Package Files" in page_text(app)
    widget(app.file_uploader, "package_file", "file_uploader")
    widget(app.button, "process", "button")
    assert counts(app) == ("0", "0")


def test_process_files_waits_for_the_button():
    """Choosing a file is not processing it. Nothing changes until the button is clicked."""
    app = load_app(PROCESS_FILES)
    upload(app, "packaging1.txt", data_file("packaging1.txt"))
    app.run()
    no_exception(app, PROCESS_FILES)

    assert counts(app) == ("0", "0")
    assert "written" not in page_text(app)
    assert not os.path.exists(os.path.join("data", "packaging1.json"))


def test_process_files_accumulates_across_uploads():
    """Two files, two clicks: the counts add up and every file's summary stays on the page.

    This is the session-state test. The second click happens on a *later rerun*
    than the first, so the count from the first click has to have been kept
    somewhere that survives a rerun.
    """
    app = load_app(PROCESS_FILES)

    upload(app, "packaging1.txt", data_file("packaging1.txt"))
    widget(app.button, "process", "button").click()
    app.run()
    no_exception(app, PROCESS_FILES)
    assert counts(app) == ("1", "3")
    assert "3 packages written to data/packaging1.json" in page_text(app)
    assert read_json("packaging1.json") == PACKAGING1_JSON

    upload(app, "fruit.txt", FRUIT_TXT)
    widget(app.button, "process", "button").click()  # fresh handle: the page was rebuilt
    app.run()
    no_exception(app, PROCESS_FILES)
    assert counts(app) == ("2", "5")
    text = page_text(app)
    assert "3 packages written to data/packaging1.json" in text, "the history should keep earlier files"
    assert "2 packages written to data/fruit.json" in text
    assert read_json("fruit.json") == FRUIT_JSON


def test_process_files_does_not_double_count_on_rerun():
    """A rerun with the same file still chosen — and no click — changes nothing.

    The uploader keeps its file across reruns. An app that processes whenever a
    file is present counts that file again every time anything on the page
    changes; this is the test that catches it.
    """
    app = load_app(PROCESS_FILES)

    upload(app, "packaging2.txt", data_file("packaging2.txt"))
    widget(app.button, "process", "button").click()
    app.run()
    assert counts(app) == ("1", "4")

    app.run()  # no click this time — the same file is still in the uploader
    app.run()
    no_exception(app, PROCESS_FILES)
    assert counts(app) == ("1", "4")
    assert page_text(app).count("4 packages written to data/packaging2.json") == 1
