from shared import wordreplacer
import pytest


def test_butt_statement():
    # simulate discord message
    fakemessage = "They can just require the gm tier to require all points! It's not hard!"
    bs = wordreplacer.ButtStatement(fakemessage)
    print(bs)
    assert (len(bs.chunks) == 2)
    assert (bs.chunks[0].text == "the gm tier")


def test_get_good_chunks():
    fakemessage = "They can just require the gm tier to require all points! It's not hard!"
    bs = wordreplacer.ButtStatement(fakemessage)
    assert (len(bs.get_good_chunks()) == 2)


chunks = [
    ("They can just require the gm tier to require all points! It's not hard!", 2),
    ("because i aint gonna lie, blightfall tickles my pickle even if its jank as fuck multiplay", 3),
    ("I want to touch the skullcrusher", 1),
    ("those items you get for upgrading the defender D/A into zaros, undead, rumbling, etc", 2),
    ("Okay game, you have my interest. They're playing it straight with how in space no one can hear you dakka", 0),
    ("IT'S A BIT MUCH", 1),
    ("Never seen advanced rocketry for the most part I guess?", 2),
    ("did we check out wither stuff", 1),
    ("what I used your scepters for was doing my enchantments", 2),

]


@pytest.mark.parametrize("test_input,expected_possible_chunks", chunks)
def test_bad_chunks(test_input, expected_possible_chunks):
    print(f"starting test for {test_input}")
    print(f"expect {expected_possible_chunks} chunks")
    bs = wordreplacer.ButtStatement(test_input)
    print(bs)
    print("-----END RAW STATEMENT------")
    a = bs.get_good_chunks()
    for b in a:
        print(b)
    print(f"got {len(a)} chunks")
    assert (len(a) == expected_possible_chunks)
