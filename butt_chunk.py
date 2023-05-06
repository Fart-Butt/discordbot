import logging
from rfc3987 import parse

log = logging.getLogger('bot.' + __name__)


class ButtChunk:

    def __init__(self, db, spacy, sentence, chunk, focusword=''):
        self.text = ""
        self.tag = []
        self.normalized_tags = ""
        self.lemma = []
        self.shape = []
        self.text_weight = 0
        self.tag_weight = 0
        self.lemma_weight = 0
        self.weight = 0
        self.usable_chunk = False
        self._spacy = spacy
        self.db = db
        # self.phraseweights = phraseweights
        self._original_sentence = sentence
        self.original_spacy_object = []
        self.passes_noun_check = False
        self.passes_chunk_length_check = False
        self.previous_word: str = ""
        self.previous_word_tag: str = ""
        self.noun = ""
        self.noun_shape = ""
        self._similarities = []
        self.text_list = []
        self.focusword = focusword
        self.noun_tag = ""
        self.corrected = False

        # Processing
        if self.focusword:
            self.build_chunk_word_list(chunk, fw=True)
        else:
            self.build_chunk_word_list(chunk)
        if self.usable_chunk:
            self.normalized_tags = self.normalize_tags(self.tag)
            self.get_weights(self.normalized_tags, self.lemma, self.text)
            self.weight = self._check_posessive_phrases(self.weight)

    def build_chunk_word_list(self, chunk, fw=False):
        if len(chunk.text.split(" ")) > 1:
            self.passes_chunk_length_check = True
            noun_tags = ["NN", "NNS", "NNP", "NNPS", "NOUN"]
            # characters_to_strip = ["'", '"', '*', ".", "..."]
            for i in range(chunk.start, chunk.end):
                # filter out shit chunks
                try:
                    w = parse(self._original_sentence[i].text, rule="IRI")
                    if w is dict:
                        continue
                except ValueError:
                    # not an IRI, continue processing:
                    pass
                self.text_list.append(self._original_sentence[i])
                self.tag.append(self._original_sentence[i].tag_)
                if self._original_sentence[i].tag_ in noun_tags:
                    self.passes_noun_check = True
                    if fw and self.focusword == self._original_sentence[i].text:
                        self.noun = self._original_sentence[i].text
                        self.noun_shape = self._original_sentence[i].shape_
                        self.noun_tag = self._original_sentence[i].tag_
                        try:
                            self.previous_word = self._original_sentence[i - 1].text
                        except IndexError:
                            self.previous_word = ""
                        try:
                            self.previous_word_tag = self._original_sentence[i - 1].tag_
                        except IndexError:
                            self.previous_word_tag = []
                    elif not fw:
                        self.noun = self._original_sentence[i].text
                        self.noun_shape = self._original_sentence[i].shape_
                        self.noun_tag = self._original_sentence[i].tag_
                        try:
                            self.previous_word = self._original_sentence[i - 1].text
                        except IndexError:
                            self.previous_word = ""
                        try:
                            self.previous_word_tag = self._original_sentence[i - 1].tag_
                        except IndexError:
                            self.previous_word_tag = []
                self.lemma.append(self._original_sentence[i].lemma_)
                self.shape.append(self._original_sentence[i].shape_)
                self.original_spacy_object.append(self._original_sentence[i])
            self.text = chunk.text
            if len(self.noun) > 3:
                if self.passes_noun_check and self.passes_chunk_length_check:
                    self.usable_chunk = True
            else:
                self.usable_chunk = False

    def _butt_vector_analyser(self, phrase) -> int:
        """check noun vector similarity to spatially funny objects/words/concepts."""
        # TODO: consider reducing weight value for not funny words/objects/concepts
        spatially_funny_objects = self._spacy("animal people structure machine car")
        phrase = self._spacy(phrase)
        # not_funny_objects = ["time", ]
        starting_weight = self.__get_text_weight(self.text)
        if starting_weight == 0:
            return 0
        else:
            working_weight = starting_weight
            for s in spatially_funny_objects:
                similarity = s.similarity(phrase)
                if similarity > .5:
                    self._similarities.append("%s: %f" % (s, similarity))
                    working_weight = int(working_weight + starting_weight * similarity)
            return working_weight

    @staticmethod
    def normalize_tags(tags: list) -> str:
        """intended for db storage/retrieval - collapses tags of similar type to a master type.
        example: collapses all noun POS tags (NNS,NNP,NNPS) to NN."""
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

    def _store_lemma(self, normalized_lemma: str, normalized_tag: str, weight: int):
        self.db.do_insert("""insert into lemma_weights(`tag`, `lemma`, `frequency`, `weight`)
                          values ((select tag from tag_weights where tag = %s), %s, 1, %s)
                          on duplicate key update 
                          frequency=(select frequency from lemma_weights lw where lw.lemma=%s)+1,
                          weight = %s""",
                          (normalized_tag, normalized_lemma, weight, normalized_lemma, weight))

    def _store_tag(self, tag: str, weight: int):
        self.db.do_insert(
            "INSERT into tag_weights (tag, weight) VALUES (%s, %s) ON DUPLICATE KEY UPDATE weight=%s",
            (tag, weight, weight))

    def _store_phrase(self, word: str, weight: int, pos: str):
        self.db.do_insert(
            "INSERT into phraseweights (phrase, weight, pos) "
            "VALUES (%s, %s, %s) "
            "ON DUPLICATE KEY UPDATE weight = weight + %s",
            (word, weight, pos, weight)
        )

    def get_weights(self, normalized_tag: str, lemma: list, text: str):
        self.text_weight = self._butt_vector_analyser(text)
        self.tag_weight = self.__get_tag_weight(normalized_tag)
        self.lemma_weight = self.__get_lemma_weight(" ".join(lemma))

        if self.text_weight == 0 or self.tag_weight == 0 or self.lemma_weight == 0:
            # block crap
            self.weight = 0
            self.usable_chunk = False
        else:
            self.weight = self.text_weight + self.tag_weight + self.lemma_weight

    def __get_lemma_weight(self, lemma: str) -> int:
        try:
            db_weight = self.db.do_query("select weight from lemma_weights where lemma=%s", (lemma,))[0]["weight"]
        except IndexError:
            db_weight = 1000
        if not db_weight:
            return 0
        elif db_weight < 0:
            return 1
        return db_weight

    def __get_tag_weight(self, tag: str) -> int:
        try:
            db_weight = self.db.do_query("select weight from tag_weights where tag=%s", (tag,))[0]["weight"]
        except IndexError:
            db_weight = 1000
        if not db_weight:
            return 0
        elif db_weight < 0:
            return 1
        return db_weight

    def __get_text_weight(self, text: str) -> int:
        try:
            db_weight = self.db.do_query("select weight from phraseweights where phrase=%s", (text,))[0]["weight"]
        except IndexError:
            # not in db
            db_weight = 1000
        if not db_weight:
            return 0
        elif db_weight < 0:
            return 1
        else:
            return db_weight

    @staticmethod
    def list_to_string(list_: list) -> str:
        return " ".join(list_)

    def adjust_weight(self, voted_weight: int):
        log.debug("PhraseWeights - updating phrase database")
        count_update = 0
        count_ignored = 0
        if voted_weight == 0:
            count_ignored += 1
            # no further processing.
            log.debug("word %s: not adjusting weight since voted weight is %d" %
                      (self.text, voted_weight)
                      )
            pass
        else:
            count_update += 1
            db_word_weight = self.text_weight
            calculated_weight = db_word_weight + voted_weight
            log.debug("word %s is getting weight %d adjusted to %d" % (self.text, db_word_weight, calculated_weight))
            self._store_phrase(self.text, calculated_weight, " ".join(self.tag))
            self._store_tag(self.normalized_tags, calculated_weight)
            self._store_lemma(" ".join(self.lemma), self.normalized_tags, calculated_weight)
        log.debug(
            "PhraseWeights - updating phrase database completed.  Updated: {} Ignored: {}"
            .format(count_update, count_ignored)
        )

    def _check_posessive_phrases(self, weight: int) -> int:
        if self.previous_word_tag == "PRP$":
            return self.weight * 10
        else:
            return weight

    def __repr__(self):
        return f"""
        butt_chunk
        text: {self.text}
        text weight: {self.text_weight}
        tag: {self.tag}
        tag weight: {self.tag_weight}
        normalized tags: {self.normalized_tags}
        lemma: {self.lemma}
        lemma weight: {self.lemma_weight}
        shape: {self.shape} 
        original spacy object: {self.original_spacy_object}
        Previous Word: {self.previous_word}
        Previous Word Tag: {self.previous_word_tag}
        Noun: {self.noun}
        Noun Tag: {self.noun_tag}
        N: {self.passes_noun_check} CL {self.passes_chunk_length_check} UC {self.usable_chunk}
        weight: {self.weight}
        similarities: {self._similarities}
        """
