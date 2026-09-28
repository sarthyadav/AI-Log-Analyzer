# tests/test_main.py
# tests for main.py - focused on logic that doesn't require calling the
# actual LLM, since those calls are slow and would make tests flaky

import pytest
from main import read_log_file, classify_log


def test_read_log_file_returns_content(tmp_path):
    """
    A log file with real content should be read back exactly as written.
    """
    log_file = tmp_path / "sample.log"
    log_file.write_text("BUILD FAILURE: something went wrong")

    content = read_log_file(str(log_file))

    assert content == "BUILD FAILURE: something went wrong"


def test_read_log_file_raises_for_missing_file():
    """
    Reading a file that doesn't exist should raise FileNotFoundError
    with a clear message, not Python's default cryptic one.
    """
    with pytest.raises(FileNotFoundError):
        read_log_file("this_file_does_not_exist.log")


def test_read_log_file_raises_for_empty_file(tmp_path):
    """
    An empty log file should raise ValueError, not silently proceed.
    """
    log_file = tmp_path / "empty.log"
    log_file.write_text("")

    with pytest.raises(ValueError):
        read_log_file(str(log_file))

def test_classify_log_returns_valid_category(monkeypatch):
    """
    If the LLM returns a valid category, classify_log should return it as-is.
    """
    monkeypatch.setattr("main.get_llm_response", lambda prompt, temperature=0.2: "timeout")

    assert classify_log("some log text") == "timeout"


def test_classify_log_cleans_messy_response(monkeypatch):
    """
    LLMs sometimes add whitespace or capitalization - classify_log
    should normalize that before matching against valid categories.
    """
    monkeypatch.setattr("main.get_llm_response", lambda prompt, temperature=0.2: "  Compile Error \n")

    assert classify_log("some log text") == "compile error"


def test_classify_log_returns_unrelated(monkeypatch):
    """
    The 'unrelated' escape hatch should be passed through correctly.
    """
    monkeypatch.setattr("main.get_llm_response", lambda prompt, temperature=0.2: "unrelated")

    assert classify_log("some log text") == "unrelated"


def test_classify_log_returns_unknown_for_garbage(monkeypatch):
    """
    If the LLM responds with something outside the expected set,
    we fall back to 'unknown' instead of crashing or guessing.
    """
    monkeypatch.setattr("main.get_llm_response", lambda prompt, temperature=0.2: "I think this is a network problem")

    assert classify_log("some log text") == "unknown"