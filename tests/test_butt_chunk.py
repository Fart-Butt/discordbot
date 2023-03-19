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
    """expected output:
    text: the gm tier
        text weight: 1500
        tag: ['DT', 'NNP', 'NN']
        tag weight: 1000
        normalized tags: DT NN NN
        lemma: ['the', 'gm', 'tier']
        lemma weight: 1000
        shape: ['xxx', 'xx', 'xxxx'] 
        original spacy object: [the, gm, tier]
        Previous Word: ['the', 'gm']
        Previous Word Tag: ['DT', 'NNP']
        Noun: [gm, tier]
        N: True CL True UC True
        weight: 3500
        similarities: ['structure: 0.500237']
        """
    assert (len(bc.tag) == 3)
    assert (bc.tag[0] == 'DT')
    assert (bc.tag[1] == 'NNP')
    assert (bc.tag[2] == 'NN')
    assert (bc.normalized_tags == "DT NN NN")
    assert (bc.text == "the gm tier")
    # assert False


def test__butt_vector_analyser():
    test_word = nlp("car")
    assert (bc._butt_vector_analyser(test_word) > 1000)


def test_normalize_tags():
    assert (
            bc.normalize_tags(["NNP", "NNS", "NNPS", "RBR", "RBS", "VBD", "VBG", "VBN", "VBP", "JJR", "JJS"]) ==
            "NN NN NN RB RB VB VB VB VB JJ JJ"
    )
