# IST356 Assignment 03 — Packaging Apps in Streamlit

In Assignment 02 you built a package and put three console programs on top of it.
Console programs are fine for you; they are useless for anyone else. Nobody in the
warehouse is going to open a terminal to find out how many eggs are in a box.

So this time the programs are **web apps**, written with **Streamlit** — the same
Python, drawn in a browser, with a text box and an upload button instead of `input()`
and `sys.argv`. The job is small on purpose: a module that parses **package
descriptions** like `"12 eggs in 1 carton / 3 cartons in 1 box"` is written for you,
and you build three apps that use it, each a step up from the last:

1. **One package, typed in.** A text box, a parse, a total.
2. **One file, uploaded.** The same job for every line in a file, and the results
   written out as JSON.
3. **Many files, one after another** — with a running count of how many files and
   packages the app has seen *so far*.

That third app is where Streamlit stops behaving like the Python you know. A Streamlit
script does not run once; it runs **from the top, again, on every click and keystroke**.
Any variable you set at the top is reset to that value every time. So a counter that
has to survive from one upload to the next cannot live in a variable — it has to live
in **session state**, and you have to decide *when* the counting happens. Getting that
right, and understanding why the obvious version is wrong, is the whole point of the
assignment.

## Meta

### Learning Objectives

By the end of this assignment you will be able to:

1. **Run a Streamlit app** from VS Code and open it in the browser — locally or in Codespaces
2. **Explain Streamlit's execution model**: the script reruns top-to-bottom on every interaction
3. **Use input widgets** (`st.text_input`, `st.file_uploader`, `st.button`) and read the value each one returns
4. **Use output widgets** (`st.info`, `st.success`, `st.metric`, `st.columns`) instead of `print()`
5. **Guard the work behind the input** — do nothing until there is something to do
6. **Use a module you did not write**, by reading its docstrings rather than its code
7. **Convert an uploaded file from bytes to text** and process it line by line, skipping blank lines
8. **Write Python data to a JSON file** with `json.dump`
9. **Keep values across reruns** with `st.session_state`, and trigger work with a button
10. **Read two kinds of tests** — behaviour tests that drive the page, and structure tests that read your source
11. **Commit after each part, submit for grading**, and act on the feedback

### Assignment Layout

- `code/` — **where you write code.** Only files in this folder are reviewed for grading.
  - `packaging_parser.py` — **provided for you.** Parses package descriptions. Read it, don't change it
  - `one_package.py` — **Part 1**, one typed description (walked through step by step)
  - `process_file.py` — **Part 2**, one uploaded file (the steps described, the code yours)
  - `process_files.py` — **Part 3**, many files with a running count (**you write this one yourself**)
  - `reflection.txt` — **where you write your reflection** (graded)
- `data/` — three sample files to upload, one package description per line. The apps write their `.json` output here too
- `tests/` — the automated tests that check your apps
  - `test_streamlit.py` — **Streamlit Tests**: run each app and read the page
  - `test_code.py` — **Code Structure Tests**: read each app's source
- `grader/` — the autograder used by GraderThan (you don't touch this)
- `.devcontainer/` — configures the pre-built course dev container (`mafudge/ist356:latest`)
- `.streamlit/` / `.vscode/` — Streamlit settings and run / debug / test configurations
- `README.md` — these instructions
- `reflection.md` — how to write a good reflection
- `rubric.json` / `requirements.txt` — grading rubric and Python dependencies
- `one_package.png`, `process_file.png`, `process_files.png` — screenshots of the finished apps

You write **three Streamlit apps**. `packaging_parser.py` is given to you — read it, but
don't change it.

> **Why is it called `packaging_parser.py` and not `packaging.py`?** Because a module
> named `packaging` is already installed in every Python environment (pip and Streamlit
> both depend on it), and `import packaging` finds *that* one first. Naming a module the
> same as something already installed is a classic mistake, and this is what it looks
> like: an `ImportError` for a function that is plainly right there in your file.

### Prerequisites

Same environment as Assignments 01 and 02. Streamlit is already installed in the course
container. `requirements.txt` asks for a recent version (`streamlit>=1.56`), because the
tests use Streamlit's own testing module to drive your apps; the dev container installs
it when it first builds, so normally there is nothing for you to do. If `pytest` ever
complains about `streamlit.testing`, [Reference #7](#7-how-do-i-run-automated-tests)
shows you the one-line fix.

If you haven't done the one-time course setup yet:

👉 https://mafudge.github.io/ist356/0-intro/0-0-setup.html

This assignment runs inside the pre-built course dev container
(`mafudge/ist356:latest`), the same one Assignments 01 and 02 used.

> **No computer setup? Use GitHub Codespaces** to run everything in your browser — you
> only need a GitHub account.

---

## Prep — Open the assignment

Same as before: **first fork, then** pick **one** of two ways to open your fork in the
course environment.

1. **Fork this repository.** At the top-right of this repo's GitHub page, click
   **Fork**. This makes your own personal copy under your GitHub account. You submit
   and are graded on *your fork* — work done anywhere else cannot be graded.

Now choose **Option A** (in the browser — nothing to install) **or** **Option B** (on
your own computer). Everything in the Walkthrough works the same either way.

### Option A — GitHub Codespaces (in the browser) ⭐ easiest

A Codespace runs the exact same course container **in the cloud** and opens VS Code in
your browser — nothing to install, so this works on a Chromebook, a lab machine, or a
locked-down laptop.

1. Go to **your fork's** page on GitHub. Click the green **Code** button, then the
   **Codespaces** tab.
2. Click **Create codespace on main**. The container builds (the first time takes a few
   minutes) and installs this assignment's dependencies for you.
3. VS Code opens in your browser, already **inside the course container**, with your
   fork's code loaded and Git signed in. You can skip cloning — you're ready.

> Reopen an existing Codespace anytime from **https://github.com/codespaces** (or the
> **Code → Codespaces** tab on your fork). Codespaces have monthly free hours, so
> **stop** yours when you're done: `github.com/codespaces` → **⋯ → Stop codespace**.

### Option B — Your own computer (local dev container)

Requires Docker Desktop and VS Code from the [course setup](https://mafudge.github.io/ist356/0-intro/0-0-setup.html).

1. **Clone your fork.** On your fork's page, click the green **Code** button and copy
   the HTTPS URL, then clone it. Easiest way: in VS Code press `Ctrl+Shift+P` →
   **Git: Clone**, paste the URL, and pick a folder. Or from a terminal:

   ```sh
   git clone https://github.com/YOUR-GITHUB-USERNAME/assignment_03.git
   ```

   > Make sure the URL has **your** username in it, not `ist356`. If it doesn't, you
   > cloned the wrong repo — and nothing you commit will reach your grade.

2. **Open the folder and reopen in the container.** Choose **File → Open Folder** and
   select the cloned `assignment_03` folder. VS Code detects the dev container and pops
   up a notification — click **Reopen in Container**. (If you miss it:
   `Ctrl+Shift+P` → **Dev Containers: Reopen in Container**.) The first build takes a
   few minutes; after that you're working *inside* the course environment.

### Check you're ready

Open the **Testing** panel (View → Testing) and run the tests
([Reference #7](#7-how-do-i-run-automated-tests)). You should see **2 passing and 16
failing** — that is exactly right. The two that pass only look for the title and the
text box in `one_package.py`, which are written for you; everything else is about
code you haven't written yet. Nearly all red is the correct starting line.

If instead you see *no tests at all*, that is a different problem — see
[Reference #7](#7-how-do-i-run-automated-tests).

---

## About the data and the parser — read this before you start

A **package description** reads left to right, one level of packaging at a time,
levels separated by ` / `:

```
12 eggs in 1 carton / 3 cartons in 1 box
```

Twelve eggs go in a carton; three cartons go in a box. `packaging_parser.py` gives you
three functions, and they are the *only* parsing you will do:

| function | given | returns |
| --- | --- | --- |
| `parse_packaging(text)` | one description | a list of levels, `[{'eggs': 12}, {'cartons': 3}, {'box': 1}]` |
| `calc_total_units(package)` | that list | every quantity multiplied together: `36` |
| `get_unit(package)` | that list | the name of the smallest unit: `'eggs'` |

So the description above is **36 eggs** — that is the "total package size" the apps
display. The list is ordered smallest unit first, and the outermost container is
always `1` of something.

The files in `data/` hold one description per line:

| file | lines | a taste |
| --- | --- | --- |
| `packaging1.txt` | 3 | eggs, baseballs, playing cards |
| `packaging2.txt` | 4 | tennis balls, tires, tablets, vials |
| `packaging3.txt` | 8 | a longer mix, ending in millimetres |

Two things about text files that will bite you if you don't know them. A text file
normally **ends with a newline**, so if you split its contents on line breaks the last
"line" is empty. And `parse_packaging("")` raises a `ValueError`, because an empty
string is not a package. Skip blank lines. The tests upload a file with a blank line in
the *middle* as well, so skip them wherever they are.

---

## Walkthrough — Do the assignment step by step

Work in order. Each step tells you *what* to do; when you need the *mechanics*, follow
the link to the matching **Reference — How do I…?** entry below.

### The training wheels come off

The three apps do related jobs, so they are deliberately **not** supported equally.
Open each file and you'll find a different amount of help waiting:

| app | what the file gives you |
| --- | --- |
| `one_package.py` | the title and the text box written out, and a TODO per line naming the exact function to call |
| `process_file.py` | the steps described in words — which function and which widget does each job is yours to work out |
| `process_files.py` | the goal, the two traps, and nothing else |

By the third app you should be reaching for the two finished apps beside it rather than
for a list of instructions — which is exactly what you'll do on the job.

**IMPORTANT GRADING NOTE:**  Remove the TODO comments as you write the code. leaving them might impact the code style checker, as its good practivce to *remove TODO comments after you code the TODO itself*

### Build order at a glance

| order | write this | turns green |
| --- | --- | --- |
| 1 | *(run the empty `one_package.py` — see the page appear)* | — |
| 2 | *(read `packaging_parser.py`, run its demo)* | — |
| 3 | `one_package.py` | `test_one_package_*` — 3 in `test_streamlit.py`, 2 in `test_code.py` |
| 4 | `process_file.py` | `test_process_file_*` — 4 in `test_streamlit.py`, 2 in `test_code.py` |
| 5 | `process_files.py` | `test_process_files_*` — 4 in `test_streamlit.py`, 3 in `test_code.py` |
| 6 | `reflection.txt` | — |

Every app is tested two ways. `test_streamlit.py` **runs the page**: it types into your
text box, uploads a file, clicks your button, and reads what the page says. `test_code.py`
**reads your source**: it checks the app imports the parser and calls it, uses the
widgets the assignment asks for, and keeps its state where state has to be kept. A page
can say the right thing for the wrong reasons — that second file is what notices.

### Step 1 — Run an app before you write one

Open `code/one_package.py`. It is empty apart from a docstring, and it will still run:
launch it ([Reference #1](#1-how-do-i-run-a-streamlit-app)) and open it in the browser.
A blank page — good. That blank page *is* your script, executed top to bottom and
producing nothing. Everything you add will appear in the order you add it.

Leave it running. Streamlit notices when you save the file; click **Rerun** (or turn on
**Always rerun**) and your changes show up.

### Step 2 — Read what you've been given

Open `code/packaging_parser.py`. You don't write it, but you *do* have to know what it
takes and what it returns — that is what its docstrings are for, and reading a docstring
instead of the code is a skill in itself.

Run it directly (**Python Debugger: Current File**) and watch the demo at the bottom
print. That `if __name__ == '__main__':` block only runs when the file is run *as a
program*; when your app imports the module it is skipped. It's the right place to try
a description of your own, or to set a breakpoint and step through the parser.

### Step 3 — Part 1: `one_package.py`

The title and the text box are written for you. Notice that `st.text_input(...)`
**returns a value**, and that on the first run — before anyone has typed — that value is
an empty string. Now fill in the TODOs:

1. **Guard the work.** `if package_data:` — everything below happens only when there
   is something in the box. This is the line that stops the empty first run from
   crashing ([Reference #2](#2-how-does-a-streamlit-app-run)).
2. **Parse and total.** Call `parse_packaging`, then `calc_total_units` and `get_unit`.
3. **Show each level.** Loop over the list. Each level is a one-item dictionary, so
   `for name, quantity in level.items():` gives you the pair. Show it with `st.info`:

   ```
   eggs ➡️ 12
   ```

4. **Show the total** with `st.success`:

   ```
   Total 📦 Size: 36 eggs
   ```

That's the whole app. Type `12 eggs in 1 carton / 3 cartons in 1 box` and press Enter —
the page should look like this:

![Screenshot of one_package.py](one_package.png)

Run the tests ([Reference #7](#7-how-do-i-run-automated-tests)). The five `one_package`
tests should go green. The emoji are decoration: the tests look for the level names and
the number-and-unit (`36 eggs`), not the exact punctuation.

> Type something that isn't a package (`hello`) and the page fills with a red traceback —
> `parse_packaging` raised a `ValueError` and nothing caught it. Not required, but a nicer
> app wraps the parse in `try` / `except ValueError` and shows `st.error(...)` instead.

### Step 4 — Commit and get early feedback

Commit with the message `one package app` ([Reference #9](#9-how-do-i-commit-my-changes-in-vs-code)),
push ([Reference #10](#10-how-do-i-push-my-code-to-github)), and submit to GraderThan
([Reference #12](#12-how-do-i-submit-for-grading--and-review-my-feedback--with-graderthan)).

Part 1's tests should score; the rest won't, because the other two apps are still
empty. That's the point — see what partial credit looks like, and read the feedback on
your code style while there is time to act on it.

### Step 5 — Part 2: `process_file.py`

Same idea, one file at a time. The file has the steps described in words; which widget
and which function does each job is yours to work out, and `one_package.py` is your
worked example for the shape.

1. **Title**, then a **file uploader** ([Reference #3](#3-how-do-i-read-a-value-from-an-input-widget)).
   Give it `key="package_file"`. It returns `None` until a file is chosen — so the guard
   is the same shape as Part 1.
2. **Bytes to text.** The upload is *bytes*. Decode it to a string, then split it into
   lines ([Reference #4](#4-how-do-i-turn-an-uploaded-file-into-text)).
3. **Every line:** strip it, **skip it if it's blank**, parse it, keep the parsed
   package in a list, and show the line with its total:

   ```
   12 eggs in 1 carton / 3 cartons in 1 box ➡️ Total 📦 Size: 36 eggs
   ```

4. **Write the JSON.** The list of parsed packages goes to `data/<same name>.json` —
   `packaging1.txt` in, `data/packaging1.json` out — with `json.dump`
   ([Reference #5](#5-how-do-i-write-a-json-file)). The path is relative to the
   folder the app runs in, which is the repository root; the tests look there.
5. **Say what happened**, with `st.success`, exactly:

   ```
   3 packages written to data/packaging1.json
   ```

Upload `data/packaging1.txt` from the browser and check the page against the screenshot,
then open `data/packaging1.json` in VS Code and check it is a list of lists of
dictionaries. (Those `.json` files are ignored by git on purpose — they are output, not
your work.)

![Screenshot of process_file.py](process_file.png)

Make the `process_file` tests pass. One of them uploads a file you have never seen, with
a blank line in the middle — if that one fails and the others pass, you know exactly
what to fix.

### Step 6 — Commit

Commit `process file app`, push, submit. Two of three apps now score.

### Step 7 — Part 3: `process_files.py` *(on your own)*

The same processing as Part 2, but the app **remembers**. Across any number of uploads
it shows two `st.metric` cards, **Files processed** and **Packages processed**, and
under them one line per file it has handled:

```
3 packages written to data/packaging1.json
4 packages written to data/packaging2.json
```

The metrics are on the page from the very first run, both at `0`. Per-line output is
not needed this time — just the summary line for each file, kept in a list.

There is no walkthrough for this one. You have two finished apps to learn from and two
traps to avoid, and the file's docstring names both:

- **A rerun resets your variables.** `files_processed = 0` at the top of the script is
  `0` again on every rerun, so the count never gets past one. Anything that has to
  survive a rerun lives in `st.session_state`, and is initialised **once**
  ([Reference #6](#6-how-do-i-keep-a-value-between-reruns)).
- **The uploader keeps its file.** Once a file is chosen it is *still* chosen on every
  rerun, so an app that processes "whenever there is a file" counts the same file again
  every time anything on the page changes. Process on a **button** instead —
  `st.button("Process file", key="process")` is `True` only on the one rerun the click
  caused. Choosing a file and *not* clicking must change nothing.

Put the two metrics in `st.columns(2)` so they sit side by side, the way the screenshot
shows. A **Reset** button that zeroes everything is a nice touch and a good test of
whether you understand the state — optional.

![Screenshot of process_files.py](process_files.png)

Make the `process_files` tests pass. `test_process_files_does_not_double_count_on_rerun`
is the one that catches the second trap; `test_process_files_remembers_with_session_state`
in `test_code.py` catches the first.

### Step 8 — Commit

Commit `process files app`, push, submit.

### Step 9 — Write your reflection

Read `reflection.md`, then write yours in `code/reflection.txt`. Be **specific**, use the
**terminology** from this assignment (rerun, widget, return value, guard, bytes vs.
text, decode, session state, initialise once, button-triggered, metric), and make it
**actionable**.

### Step 10 — Final submit

Commit `assignment complete`, push, and submit again
([Reference #9–12](#9-how-do-i-commit-my-changes-in-vs-code)). Read your feedback and fix
anything flagged — you get multiple attempts before the due date.

---
## Reference — How do I…?

> **Using GitHub Codespaces?** Every entry works exactly the same — it's the same VS Code
> and the same course container, just in your browser.

### 1. How do I run a Streamlit app?

Streamlit turns a Python file into an interactive web app.

1. Open the app file, e.g. `code/one_package.py`.
2. Open **Run and Debug** (**View → Run**, the play-with-a-bug icon).
3. From the dropdown at the top, choose **Streamlit Run: Current File**, then press
   the green **▶** button. The terminal shows the app starting on port **28502**.
4. Open the app in your browser:
   - **On your computer (Option B):** go to **http://localhost:28502** — VS Code
     usually also pops up an **Open in Browser** button on a port notification.
   - 🌐 **In Codespaces (Option A):** `localhost` won't work. Open the **PORTS** tab
     (next to TERMINAL), find port **28502**, and click the 🌐 globe icon (or the
     **Open in Browser** popup) to open the forwarded URL.
5. Edit and save the file; the page offers **Rerun** (top right). **Always rerun** saves
   the click.
6. Stop it with **Run → Stop Debugging** (`Shift+F5`) when you're done, and before
   launching a different app — two apps cannot share the port.

From a terminal the equivalent is `streamlit run code/one_package.py`, **run from the
repository root** — the apps write to `data/` relative to where they were started.

### 2. How does a Streamlit app run?

Not like a program with a `main()`. Streamlit runs your script **from the top, all of it,
every time the user does anything** — types in a box, chooses a file, clicks a button.
Each run redraws the whole page from scratch in the order your code calls the widgets.

Three consequences you will meet in this assignment:

- **The first run happens before any input.** A text box returns `""`, an uploader
  returns `None`, a button returns `False`. Any work has to sit behind an `if`.
- **Variables do not survive.** `count = 0` at the top of the script is executed again
  on every rerun, so `count` is `0` again. See #6.
- **A button is only `True` once** — on the rerun its click caused. On the next rerun,
  whatever caused it, that same `st.button(...)` returns `False` again.

Compare `2-counter-wrong.py` and `2-counter-session.py` from class: identical apart from
where the count lives.

### 3. How do I read a value from an input widget?

Every input widget is a function call that **returns the widget's current value**:

```python
package_data = st.text_input("Enter package data:", key="package_data")   # str, "" until typed
uploaded_file = st.file_uploader("Upload package file:", key="package_file")  # None until chosen
clicked = st.button("Process file", key="process")                            # True only when just clicked
```

`key=` gives the widget a stable name. This assignment asks for the keys shown above so
the tests can find your widgets — and a key is also what you would use to reach the
widget's value through `st.session_state[key]`. Two widgets with the same label and no
key is an error; the key is how Streamlit tells them apart.

### 4. How do I turn an uploaded file into text?

What `st.file_uploader` hands you is a file-like object, and its contents are **bytes**
— the uploader cannot know whether you sent it a text file or a photo. Decode it:

```python
text = uploaded_file.getvalue().decode("utf-8")    # bytes -> str
for line in text.splitlines():                      # one str per line
    line = line.strip()
    if not line:                                    # the empty line after the final newline
        continue
    ...
```

`uploaded_file.name` is the file's name as uploaded — `packaging1.txt` — which is what
you need to build the name of the JSON file. This is the same pattern as `2-upload.py`
and `2-2-3.py` from class.

### 5. How do I write a JSON file?

`json.dump` writes any combination of lists, dictionaries, strings and numbers to an open
file, and `indent=4` makes it readable:

```python
import json

with open("data/packaging1.json", "w") as json_file:
    json.dump(packages, json_file, indent=4)
```

`packages` here is a list of parsed packages — a list of lists of dictionaries. To build
the output name from the input name: `uploaded_file.name.replace(".txt", ".json")`.

### 6. How do I keep a value between reruns?

Put it in `st.session_state`, and initialise it **once** — the first time the script
runs, when the key does not exist yet:

```python
if "files_processed" not in st.session_state:   # first run only
    st.session_state.files_processed = 0
    st.session_state.history = []

if clicked:                                      # the rerun the click caused
    st.session_state.files_processed += 1
    st.session_state.history.append(summary)

st.metric("Files processed", st.session_state.files_processed)   # every run
```

Three parts, in that order: initialise if missing, update on an interaction, display
from state. `2-counter-session.py` and `2-2-2.py` from class are exactly this shape.

### 7. How do I run automated tests?

Open **Testing** in the activity bar (View → Testing). Press ▶ next to a test to run it,
or ▶ at the top to run them all. Green check = pass, red X = fail. Click a failed test to
see the assertion, expected vs. actual, and the line number.

You can also run them in the terminal from the repository root:

```
pytest tests/test_streamlit.py -v
pytest tests/test_code.py -v
pytest tests/ -k one_package          # just one part's tests, from both files
```

**How can a test click a button?** `test_streamlit.py` uses `streamlit.testing.v1.AppTest`,
which runs your script in-process — no browser, no server — and hands back the elements
it drew. Setting the text box, choosing a file and clicking a button are method calls,
and "what does the page say" is a string. Have a look at `tests/helpers.py`; it is short.

If the Testing panel shows **no tests at all**, or `pytest` stops with
`ModuleNotFoundError: No module named 'streamlit.testing'` (or a similar import error),
your Streamlit is too old for the testing module. From a terminal at the repository root:

```
pip install -r requirements.txt
```

### 8. How do I debug a Streamlit app?

**Streamlit Run: Current File** is a real debug session: set a breakpoint in your app
(click in the gutter left of a line number), interact with the page in the browser, and
VS Code stops at the line. Use the **VARIABLES** panel to inspect `package_data`,
`uploaded_file`, `st.session_state`, and step with `F10`.

The quick-and-dirty alternative is `st.write(some_variable)` — it draws the value on the
page, whatever type it is. Delete it when you're done. Do **not** reach for `print()`:
that goes to the terminal, not the page, and the structure tests flag it.

To debug the parser itself, run `code/packaging_parser.py` directly with **Python
Debugger: Current File** and put your description in the `__main__` block.

### 9. How do I commit my changes in VS Code?

View → Source Control. Type a commit message in the box, then click **Commit**. Commit
after each working piece — not once at the end.

### 10. How do I push my code to GitHub?

In Source Control, click **Sync Changes** (or the ⋯ menu → Push). In Codespaces you're
already signed in.

### 11. How do I see my code on GitHub?

Open your fork in the browser: `https://github.com/YOUR-GITHUB-USERNAME/assignment_03`.
If your latest change isn't there, it isn't pushed — and GraderThan won't see it.

### 12. How do I submit for grading — and review my feedback — with GraderThan?

GraderThan runs the autograder (Streamlit + code structure tests) and an AI reviewer
(code style, reflection) against your fork, then gives you a score and detailed,
per-criterion feedback.

**Submit:**

1. Go to **https://graderthan.cent-su.org** and log in with your SU Microsoft account.
2. On **Your dashboard**, click this assignment.
3. **First time only:** if you see **"Link your GitHub account first,"** click
   **Profile** → **Connect GitHub** and authorize it. You only do this once.
4. Under **Request grading**, submit your **fork's GitHub URL**
   (e.g. `https://github.com/YOUR-GITHUB-USERNAME/assignment_03`). Click **Submit for
   Grading and Feedback.**

> Always **commit and push before you submit** — GraderThan only sees what's on GitHub.
> You get multiple attempts, so submit early and often.

**Review your feedback:** scroll to **"Your submissions"** and click one. `AUTOMATED`
criteria show the raw test output (e.g. `11/11 tests passed`); `AI-JUDGED` criteria show
a written paragraph, the specific lines flagged, and a **"How to improve"** tip. Fix
what's flagged, commit, push, and submit again.

---
## The Assignment — what to actually do

Three Streamlit apps in `code/`, each importing `packaging_parser`. No parsing by hand —
if you are splitting strings on `" in "`, the module already does that.

### 1. `one_package.py` — one description, typed in

| widget | key | shows |
| --- | --- | --- |
| `st.title` | | `Process One Package` |
| `st.text_input` | `package_data` | the description, e.g. `12 eggs in 1 carton / 3 cartons in 1 box` |
| `st.info`, one per level | | `eggs ➡️ 12` |
| `st.success` | | `Total 📦 Size: 36 eggs` |

Nothing below the text box appears until something has been typed.

### 2. `process_file.py` — one file, uploaded

| widget | key | shows |
| --- | --- | --- |
| `st.title` | | `Process File of Packages` |
| `st.file_uploader` | `package_file` | a `.txt` file, one description per line |
| `st.info`, one per line | | `12 eggs in 1 carton / 3 cartons in 1 box ➡️ Total 📦 Size: 36 eggs` |
| `st.success` | | `3 packages written to data/packaging1.json` |

Blank lines are skipped. The parsed packages — a list of lists of dictionaries — are
written with `json.dump` to `data/<name>.json`, where `<name>` is the uploaded file's name
with `.txt` replaced by `.json`. Nothing is processed or written until a file is chosen.

### 3. `process_files.py` — many files, with a running count

| widget | key | shows |
| --- | --- | --- |
| `st.title` | | `Process Package Files` |
| `st.file_uploader` | `package_file` | the next file to process |
| `st.button` | `process` | `Process file` — processing happens **only** when clicked |
| `st.metric` ×2, in `st.columns(2)` | | `Files processed` and `Packages processed`, always shown, starting at `0` |
| `st.info`, one per file so far | | `3 packages written to data/packaging1.json` |

Each click processes the chosen file exactly as Part 2 does (parse every non-blank
line, write the JSON), then adds to the counts and to the history — all kept in
`st.session_state` so they survive reruns. Choosing a file without clicking changes
nothing; a rerun with the same file still chosen changes nothing.

### 4. Reflection

Read `reflection.md`, then write your reflection in `code/reflection.txt`. A good
reflection is **specific**, **uses the terminology** from this assignment, and is
**actionable**.

---
## How You're Graded

GraderThan scores this assignment out of **10 points** (see `rubric.json`):

| What | Points | Judged by |
| --- | --- | --- |
| **Streamlit Tests** — `test_streamlit.py` (the three apps, driven like a user would) | 3 | automated tests |
| **Code Structure Tests** — `test_code.py` (imports, calls, widgets, session state) | 3 | automated tests |
| Code style & readability | 2 | AI reviewer |
| Reflection quality | 2 | AI reviewer |

**Only files in the `code/` folder are graded.** Commit, push, and submit
([Reference #9–12](#9-how-do-i-commit-my-changes-in-vs-code)) to get your score and
feedback.
