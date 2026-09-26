"""Shared helpers for the tests.

The Streamlit tests drive each app with `streamlit.testing.v1.AppTest`, which runs
a Streamlit script in-process, without a browser or a server, and hands back the
elements the script drew. Typing into a text box, choosing a file, and clicking a
button are all method calls — which is what lets an autograder exercise a web app.
"""

import json
import os

from streamlit.testing.v1 import AppTest

# tests/ lives directly under the repository root.
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Elements whose `.value` is the text a person would read on the page.
TEXT_ELEMENTS = (
    "title", "header", "subheader", "markdown", "text", "caption", "code",
    "info", "success", "warning", "error", "json",
)


def repo_path(*parts: str) -> str:
    """Build an absolute path from the repository root, whatever the working directory."""
    return os.path.join(REPO_ROOT, *parts)


def load_app(script: str) -> AppTest:
    """Load one of the apps in code/ and run it once, as a browser would on opening it."""
    app = AppTest.from_file(repo_path(script), default_timeout=30)
    app.run()
    return app


def page_text(app: AppTest) -> str:
    """Everything readable on the page, joined into one string.

    Which output widget an app uses — st.info, st.success, st.write, st.markdown —
    is a design choice, so the tests check *what the page says* rather than which
    widget said it. Metrics contribute their label and value.
    """
    parts = []
    for element_type in TEXT_ELEMENTS:
        parts.extend(str(element.value) for element in app.get(element_type))
    for metric in app.metric:
        parts.append(f"{metric.label}: {metric.value}")
    return "\n".join(parts)


def counts(app: AppTest) -> tuple[str, str]:
    """The values of the "Files processed" and "Packages processed" metric cards.

    st.metric shows its value as text, so these come back as strings: ("1", "3").
    """
    shown = {metric.label: str(metric.value) for metric in app.metric}
    for label in ("Files processed", "Packages processed"):
        assert label in shown, (
            f"expected an st.metric labelled {label!r}; the page has {sorted(shown) or 'no metrics'}"
        )
    return shown["Files processed"], shown["Packages processed"]


def widget(elements, key: str, kind: str):
    """Find the widget the tests interact with.

    Prefers the one whose `key=` matches; falls back to the widget when there is
    exactly one of that kind, so a forgotten key is not fatal. More than one and
    no matching key is ambiguous, and says so.
    """
    for element in elements:
        if getattr(element, "key", None) == key:
            return element
    if len(elements) == 1:
        return elements[0]
    raise AssertionError(
        f"expected one st.{kind} (or one with key={key!r}), found {len(elements)}"
    )


def upload(app: AppTest, filename: str, content: str) -> None:
    """Choose a file in the app's uploader, as if dragged into the browser.

    Streamlit hands an app the upload as *bytes*, and so does this: `content` is
    encoded exactly as a text file on disk would be.
    """
    uploader = widget(app.file_uploader, "package_file", "file_uploader")
    uploader.set_value((filename, content.encode("utf-8"), "text/plain"))


def data_file(name: str) -> str:
    """The text of a file in data/."""
    with open(repo_path("data", name), encoding="utf-8") as fh:
        return fh.read()


def read_json(name: str):
    """Load data/<name>, which an app should have written."""
    path = repo_path("data", name)
    assert os.path.exists(path), f"expected the app to write {os.path.join('data', name)}"
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def no_exception(app: AppTest, script: str) -> None:
    """Fail with the app's own traceback if it raised while running."""
    assert not app.exception, f"{script} raised: {app.exception[0].value}"
