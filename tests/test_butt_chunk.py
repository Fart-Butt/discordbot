from butt_chunk import ButtChunk
import spacy
from shared import db

nlp = spacy.load('en_core_web_lg')

nlp_sentence = nlp("They can just require the gm tier to require all points! It's not hard!")
chunks_to_investigate = []
for chunk in nlp_sentence.noun_chunks:
    chunks_to_investigate.append(chunk)
bc = ButtChunk(db["buttbot"], nlp, nlp_sentence, chunks_to_investigate[1])


def test_build_chunk_wordlist():
    assert (len(bc.tag) == 3)
    assert (bc.tag[0] == 'DT' or bc.tag[0] == 'DET')
    assert (bc.tag[1] == 'PROPN' or bc.tag[1] == 'NNP')
    assert (bc.tag[2] == 'NOUN' or bc.tag[2] == "NN")
    assert (bc.normalized_tags == "DET PROPN NOUN" or bc.normalized_tags == "DT NN NN")
    assert (bc.text == "the gm tier")


# def test__butt_vector_analyser():
#    test_word = nlp("car")
#    assert (bc._butt_vector_analyser(test_word) > 1000)


def test_normalize_tags():
    assert (
            bc.normalize_tags(["NNP", "NNS", "NNPS", "RBR", "RBS", "VBD", "VBG", "VBN", "VBP", "JJR", "JJS"]) ==
            "NN NN NN RB RB VB VB VB VB JJ JJ"
    )

# def test__time_vector_analyser():
# test_word = nlp("minutes")
# print(bc._butt_vector_analyser(test_word))
