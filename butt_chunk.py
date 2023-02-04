import logging

log = logging.getLogger('bot.' + __name__)


class ButtChunk:
    def __init__(self, sentence, chunk):
        self._original_sentence = sentence
        self.text = []
        self.tag = []
        self.lemma = []
        self.shape = []
        self.original_spacy_object = []
        self.passes_noun_check = False
        self.passes_chunk_length_check = False
        self.passes_noun_length_check = False
        self.usable_chunk = False
        self.previous_word = ""
        self.previous_word_tag = ""
        self.noun = ""
        self.build_chunk_word_list(chunk)

    def build_chunk_word_list(self, chunk):
        if len(chunk.text.split(" ")) > 1:
            self.passes_chunk_length_check = True
            noun_tags = ["NN", "NNS", "NNP", "NNPS"]
            characters_to_strip = ["'", '"', '*', ".", "..."]
            for i in range(chunk.start, chunk.end):
                # if self._original_sentence[i].text in characters_to_strip:
                #    continue
                self.text.append(self._original_sentence[i].text)
                self.tag.append(self._original_sentence[i].tag_)
                if self._original_sentence[i].tag_ in noun_tags:
                    self.passes_noun_check = True
                    self.noun = self._original_sentence[i].text
                    try:
                        self.previous_word = self._original_sentence[i - 1].text
                    except IndexError:
                        self.previous_word = None
                    try:
                        self.previous_word_tag = self._original_sentence[i - 1].tag_
                    except IndexError:
                        self.previous_word_tag = None
                self.lemma.append(self._original_sentence[i].lemma_)
                self.shape.append(self._original_sentence[i].shape_)
                self.original_spacy_object.append(self._original_sentence[i])

    def __repr__(self):
        return """
        butt_chunk
        text: {}
        tag: {}
        lemma: {}
        shape: {} 
        original spacy object: {}
        Previous Word: {}
        Previous Word Tag: {}
        Noun: {}
        N: {} NL {} CL {} UC {}
        """.format(
            self.text,
            self.tag,
            self.lemma,
            self.shape,
            self.original_spacy_object,
            self.previous_word,
            self.previous_word_tag,
            self.noun,
            self.passes_noun_check,
            self.passes_noun_length_check,
            self.passes_chunk_length_check,
            self.usable_chunk
        )
