import importlib.util
import pathlib

spec = importlib.util.spec_from_file_location(
    "text_utils", pathlib.Path(__file__).resolve().parents[1] / "utils" / "text_utils.py"
)
text_utils = importlib.util.module_from_spec(spec)
spec.loader.exec_module(text_utils)

sanitize_text_for_dash = text_utils.sanitize_text_for_dash
remove_invalid_unicode = text_utils.remove_invalid_unicode


def test_remove_invalid_unicode():
    bad_text = "hello\udcffworld"
    assert remove_invalid_unicode(bad_text) == "helloworld"


def test_sanitize_text_for_dash_removes_surrogates():
    text = "a\ud800b"
    assert sanitize_text_for_dash(text) == "ab"
