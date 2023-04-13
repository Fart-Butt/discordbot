from butt_library import strip_IRI
import pytest

iri_tests = [
    ("kitten update: we got a trail cam and are gonna try to trap mom", False),
    ("lets go to http://www.google.com", True),
    ("lets go to https://www.google.com", True),
]


@pytest.mark.parametrize("msg, msg_changes", iri_tests)
def test_strip_iri(msg, msg_changes):
    stripped_msg = strip_IRI(msg)
    print(f"original sentence: {msg}")
    print(f"processed: {stripped_msg}")
    if msg_changes:
        assert (msg != stripped_msg)
    else:
        assert (msg == stripped_msg)
