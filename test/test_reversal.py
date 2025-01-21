# test_reversal.py


def reverse_text(text):
    return text[::-1]


def test_reverse_text():
    assert reverse_text("python") == "nohtyp"
