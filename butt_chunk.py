import logging
from rfc3987 import parse

log = logging.getLogger('bot.' + __name__)


class ButtChunk:
    def __init__(self, phraseweights, db, spacy, sentence, chunk):
        self._spacy = spacy
        self.db = db
        self.phraseweights = phraseweights
        self._original_sentence = sentence
        self.text = []
        self.tag = []
        self.lemma = []
        self.shape = []
        self.original_spacy_object = []
        self.passes_noun_check = False
        self.passes_chunk_length_check = False
        self.usable_chunk = False
        self.previous_word = []
        self.previous_word_tag = []
        self.noun = []
        self._similarities = []
        self.weight = []
        self.tag_weight = 0
        self.lemma_weight = 0

        # Processing
        self.build_chunk_word_list(chunk)
        if self.usable_chunk:
            for n in self.noun:
                self.weight.append(self._butt_vector_analyser(n))
            self.normalized_tags = self.normalize_tags(self.tag)
            self.get_weights(self.normalized_tags, " ".join(self.lemma))
            self.store_tag(self.normalized_tags, self.tag_weight)
            self.store_lemma(" ".join(self.lemma), self.normalized_tags, self.lemma_weight)

    def build_chunk_word_list(self, chunk):
        if len(chunk.text.split(" ")) > 1:
            self.passes_chunk_length_check = True
            noun_tags = ["NN", "NNS", "NNP", "NNPS"]
            characters_to_strip = ["'", '"', '*', ".", "..."]
            for i in range(chunk.start, chunk.end):
                # filter out shit chunks
                try:
                    w = parse(self._original_sentence[i].text, rule="IRI")
                    if w is dict:
                        continue
                except ValueError:
                    # not an IRI, continue processing:
                    pass
                # if self._original_sentence[i].text in characters_to_strip:
                #    continue
                self.text.append(self._original_sentence[i].text)
                self.tag.append(self._original_sentence[i].tag_)
                if self._original_sentence[i].tag_ in noun_tags:
                    self.passes_noun_check = True
                    self.noun.append(self._original_sentence[i])
                    try:
                        self.previous_word.append(self._original_sentence[i - 1].text)
                    except IndexError:
                        self.previous_word = []
                    try:
                        self.previous_word_tag.append(self._original_sentence[i - 1].tag_)
                    except IndexError:
                        self.previous_word_tag = []
                self.lemma.append(self._original_sentence[i].lemma_)
                self.shape.append(self._original_sentence[i].shape_)
                self.original_spacy_object.append(self._original_sentence[i])
                if self.passes_noun_check and self.passes_chunk_length_check:
                    self.usable_chunk = True

    def _butt_vector_analyser(self, word):
        """check noun vector similarity to spatially funny objects/words/concepts."""
        # TODO: consider reducing weight value for not funny words/objects/concepts
        spatially_funny_objects = self._spacy("animal people structure machine car")
        # not_funny_objects = ["time", ]
        starting_weight = self.phraseweights.return_weight(word)
        working_weight = starting_weight
        for s in spatially_funny_objects:
            similarity = s.similarity(word)
            if similarity > .43:
                self._similarities.append("%s: %f" % (s, similarity))
                working_weight = int(working_weight + starting_weight * similarity)
        return working_weight

    @staticmethod
    def normalize_tags(tags):
        # tag map lists the tag and then the tag that we are normalizing it to.
        normalized_tags = []
        tag_map = [
            ["NNS", "NN"],
            ["NNP", "NN"],
            ["NNPS", "NN"],
            ["RBR", "RB"],
            ["RBS", "RB"],
            ["VBD", "VB"],
            ["VBG", "VB"],
            ["VBN", "VB"],
            ["VBP", "VB"],
            ["VBZ", "VB"],
            ["JJR", "JJ"],
            ["JJS", "JJ"]
        ]
        for t in tags:
            found = False
            for tm in tag_map:
                if tm[0] == t:
                    normalized_tags.append(tm[1])
                    found = True
                    continue
            if not found:
                normalized_tags.append(t)
        return " ".join(normalized_tags)

    def store_lemma(self, normalized_lemma, normalized_tag, weight):
        self.db.do_insert("""insert into lemma_weights(`tag`, `lemma`, `frequency`, `weight`)
                          values ((select tag from tag_weights where tag = %s), %s, 1, %s)
                          on duplicate key update 
                          frequency=(select frequency from lemma_weights lw where lw.lemma=%s)+1,
                          weight = %s""",
                          (normalized_tag, normalized_lemma, weight, normalized_lemma, weight))

    def store_tag(self, tag, weight):
        self.db.do_insert(
            "INSERT into tag_weights (tag, weight) VALUES (%s, %s) ON DUPLICATE KEY UPDATE weight=%s",
            (tag, weight, weight))

    def get_weights(self, tag, lemma):
        self.tag_weight = self.__get_tag_weight(tag)
        self.lemma_weight = self.__get_lemma_weight(lemma)

    def __get_lemma_weight(self, lemma):
        try:
            db_weight = self.db.do_query("select weight from lemma_weights where lemma=%s", (lemma,))[0]["weight"]
        except IndexError:
            db_weight = 1000
        return db_weight

    def __get_tag_weight(self, tag):
        try:
            db_weight = self.db.do_query("select weight from tag_weights where tag=%s", (tag,))[0]["weight"]
        except IndexError:
            db_weight = 1000
        return db_weight

    @staticmethod
    def list_to_string(list_):
        return " ".join(list_)

    def __repr__(self):
        return """
        butt_chunk
        text: {}
        tag: {}
        tag weight: {}
        normalized tags: {}
        lemma: {}
        lemma weight: {}
        shape: {} 
        original spacy object: {}
        Previous Word: {}
        Previous Word Tag: {}
        Noun: {}
        N: {} CL {} UC {}
        weight: {}
        similarities: {}
        """.format(
            self.text,
            self.tag,
            self.tag_weight,
            self.normalized_tags,
            self.lemma,
            self.lemma_weight,
            self.shape,
            self.original_spacy_object,
            self.previous_word,
            self.previous_word_tag,
            self.noun,
            self.passes_noun_check,
            self.passes_chunk_length_check,
            self.usable_chunk,
            self.weight,
            self._similarities
        )
