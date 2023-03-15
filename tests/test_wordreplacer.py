from wordreplacer import WordReplacer
from butt_chunk import ButtChunk
import spacy
from shared import db

# nlp = spacy.load('en_core_web_lg')

ab = ""
wp = WordReplacer(ab)


class SimulatedDiscordAuthorObject:
    def __init__(self, bot=False):
        self.bot = bot


class SimulatedDiscordMessageObject:
    def __init__(self, bot=False):
        self.content = "They can just require the gm tier to require all points! It's not hard!"
        self.author = SimulatedDiscordAuthorObject(bot=bot)


class SimulatedClass:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


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


def test__make_butted_sentence():
    assert False
