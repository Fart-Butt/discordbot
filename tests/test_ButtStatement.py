from shared import wordreplacer


def test_butt_statement():
    # simulate discord message
    fakemessage = "They can just require the gm tier to require all points! It's not hard!"
    bs = wordreplacer.ButtStatement(fakemessage)
    assert (len(bs.chunks) == 2)
    assert (bs.chunks[0].text == "the gm tier")


def test_get_good_chunks():
    fakemessage = "They can just require the gm tier to require all points! It's not hard!"
    bs = wordreplacer.ButtStatement(fakemessage)
    assert (len(bs.get_good_chunks()) == 2)
