from wordreplacer import WordReplacer
import pytest

ab = ""
wp = WordReplacer(ab)


class SimulatedClass:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class SimulatedDiscordAuthorObject:
    def __init__(self, bot=False):
        self.bot = bot


class SimulatedDiscordMessage:
    def __init__(self, bot=False, message_content=""):
        if message_content:
            self.content = message_content
        else:
            self.content = "They can just require the gm tier to require all points! It's not hard!"
        self.author = SimulatedDiscordAuthorObject(bot=bot)
        self.guild = SimulatedClass(id=154337182717444096)


def test__butt_in_proper_case():
    # nlp_sentence = nlp("They can just require the GM TIER to require all points! It's not hard!")
    # chunks_to_investigate = []
    # for chunk in nlp_sentence.noun_chunks:
    #    chunks_to_investigate.append(chunk)
    # bc = ButtChunk(db["buttbot"], nlp, nlp_sentence, chunks_to_investigate[1])
    # build fake noun object
    sim_noun = SimulatedClass(text="TeStInG")
    bc = SimulatedClass(noun=sim_noun)
    print(wp._butt_in_proper_case(bc, "butts"))
    assert (wp._butt_in_proper_case(bc, "butts") == "BuTtS")


nlp_sentences = [
    ("They can just require the gm tier to require all points! It's not hard!",
     [
         "They can just require the gm butt to require all points! It's not hard!",
         "They can just require the butt tier to require all points! It's not hard!",
         "They can just require the gm tier to require all butts! It's not hard!"
     ]),
    ("They can just require an apple to require all points! It's not hard!",
     [
         "They can just require a butt to require all points! It's not hard!",
         "They can just require an apple to require all butts! It's not hard!"
     ]),
    ("I want to touch the skullcrusher",
     [
         "I want to touch the buttcrusher"
     ]),
    # (
    # "how do they force feed you, ive seen some japanese anime videos on the internet and depending on how they do affects how quickly im booking a trip to japan"
    # "because i aint gonna lie, blightfal tickles my pickle even if its jank as fuck multiplay"
    # [
    #    ""
    # ]),

]


@pytest.mark.parametrize("test_input,expected_possible_returns", nlp_sentences)
def test_word_replacer_comprehensive(test_input, expected_possible_returns):
    sdo = SimulatedDiscordMessage(bot=False, message_content=test_input)
    bs = wp.perform_text_to_butt(sdo)
    print(f"original sentence: {wp.original_sentence}")
    print(f"butted message: {bs}")
    assert (bs in expected_possible_returns)


def test__replace_an_to_a_in_sentence():
    sentence = "They can just require an apple to require all points! It's not hard!"
    word = "apple"
    print(wp._replace_an_to_a_in_sentence(sentence, word))


# def test__make_butted_sentence():
#    sentence = "They can just require an apple to require all points! It's not hard!"
#    print(wp._make_butted_sentence(sentence))
def test_word_replacer():
    assert False
