from shared import wordreplacer
import pytest


def test_butt_statement():
    # simulate discord message
    fakemessage = "They can just require the gm tier to require all points! It's not hard!"
    bs = wordreplacer.ButtStatement(fakemessage)
    print(bs)
    assert (len(bs.chunks) == 3)
    assert (bs.chunks[0].text == "the gm tier")


def test_get_good_chunks():
    fakemessage = "They can just require the gm tier to require all points! It's not hard!"
    bs = wordreplacer.ButtStatement(fakemessage)
    assert (len(bs.get_good_chunks()) == 3)


chunks = [
    ("They can just require the gm tier to require all points! It's not hard!", 3),
    ("because i aint gonna lie, blightfall tickles my pickle even if its jank as fuck multiplay", 3),
    ("I want to touch the skullcrusher", 1),
    ("those items you get for upgrading the defender D/A into zaros, undead, rumbling, etc", 3)

]

@pytest.mark.parametrize("test_input,expected_possible_chunks", chunks)
def test_bad_chunks(test_input, expected_possible_chunks):
    bs = wordreplacer.ButtStatement(test_input)
    a = bs.get_good_chunks()
    for b in a:
        print(b)
    assert (len(a) == expected_possible_chunks)
