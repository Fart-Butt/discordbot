from butt_library import strip_IRI, strip_discord_formatting
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


discord_message_stripper_tests = [
    ("*now* you're thinking with portals. Also, sound ||https://i.imgur.com/d4bmAPI.mp4||",
     "now you're thinking with portals. Also, sound https://i.imgur.com/d4bmAPI.mp4"),
]


@pytest.mark.parametrize("message, expected_value", discord_message_stripper_tests)
def test_strip_discord_formatting(message, expected_value):
    stripped_message = strip_discord_formatting(message)
    print(f"stripped message: {stripped_message}")
    assert (stripped_message == expected_value)
