import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.services.text_cleaner import clean_text


def test_empty_input():
    assert clean_text("") == ""
    assert clean_text(None) == ""


def test_newlines_and_extra_spaces_collapse():
    assert clean_text("hello\n\n\nworld   again") == "hello world again"


def test_strips_ends():
    assert clean_text("   padded text   ") == "padded text"
