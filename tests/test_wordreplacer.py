from shared import shitpost
import pytest

ab = ""
wp = shitpost


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
    ("kitten update: we got a trail cam and are gonna try to trap mom",
     [
         "butt update: we got a trail cam and are gonna try to trap mom",
         "kitten update: we got a butt cam and are gonna try to trap mom",
     ]),
    ("what I used your scepters for was doing my enchantments",
     [
         "what I used your scepters for was doing my butts",
         "what I used your butts for was doing my enchantments",
     ]),
    ("so like a sludgeblock, if i can mix terms?",
     [
         "so like a buttblock, if i can mix terms?",
         "so like a sludgebutt, if i can mix terms?"
     ]),
    ("Hate hate hate hate hate",
     [
         "Butt butt butt butt butt",
     ]),
    ("*now* you're thinking with portals. Also, sound ||https://i.imgur.com/d4bmAPI.mp4||",
     ''
     )

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
    bs = ""
    bs = wp.perform_text_to_butt(sdo)
    print(f"original sentence: {wp.original_sentence}")
    print(f"butted message: {bs}")
    print(f"selected chunk: {wp.lets_butt_this_chunk}")
    print(f"buttstatement: {wp.buttstatementobject}")
    assert (bs in expected_possible_returns)


proper_case_sentences = [
    ("But not Pakkrat's World Ship?", "But not Pakkrat's World Butt?"),
    ("as an aide, kara", "as a butt, kara"),
    ("i want to touch an apple", "i want to touch a butt"),
]


@pytest.mark.parametrize("sentence, expected", proper_case_sentences)
def test_fully_integrated_wordreplacer(sentence, expected):
    sdo = SimulatedDiscordMessage(bot=False, message_content=sentence)
    a = wp.perform_text_to_butt(sdo)
    print(wp.lets_butt_this_chunk.shape)
    print(a)
    assert a == expected
