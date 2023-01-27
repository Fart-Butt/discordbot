from butt_chunk import ButtChunk
from FinalizedButtChunk import FinalizedButtChunk
import shared
import logging

log = logging.getLogger('bot.' + __name__)


class ButtClassifier:
    def __init__(self, phraseweights, nlp):
        self.message = ""
        self.weights = phraseweights
        self._starting_chunks = []
        self._chunks_to_investigate = []
        self._nouns = []
        self._nouns_previous_word_tag = []
        self._vectorized_weight = []
        self.nouns = []
        self._spacy = nlp
        self._similarities = {}
        self._processed_sentence = []

    def classify_butts(self, message):
        self.message = message
        self._starting_chunks = message.noun_chunks
        self._chunks_to_investigate = []
        self._nouns = []
        self._nouns_previous_word_tag = []
        self._vectorized_weight = []
        self.nouns = []
        self._similarities = {}
        self._extract_nouns_from_chunker()

        if self._nouns:
            i = 0
            for x in self._nouns:
                weight = self._get_word_weight(self._nouns[i], self._nouns_previous_word_tag[i])
                self.nouns.append(FinalizedButtChunk(self._nouns[i], weight, self._nouns_previous_word_tag[i],
                                                     self._similarities[x]))
                i += 1

    def get_nouns(self):
        return self.nouns

    def get_processed_sentence(self):
        return self._processed_sentence

    def get_pretty_noun_format(self):
        tags = []
        nouns = []
        for a in self._chunks_to_investigate:
            tags.append(a.tag)
            nouns.append(a.text)
        return "%s (%s)" % (nouns, tags)

    def _extract_nouns_from_chunker(self):
        # retrieve the nouns from the chunker, and nuke the bad chunks found.
        # the chunker pulls the 'subjects' out of the sentence and returns the full word data for each subject chunk.
        # right now we are blocking single word chunks because most of them are "I, he, we, etc".
        noun_tags = ["NN", "NNS", "NNP", "NNPS"]
        chunks = []
        for chunk in self._starting_chunks:
            a = ButtChunk(self.message, chunk)
            chunks.append("{} ({})".format(a.text, a.tag))
            if len(chunk.text.split()) > 1:
                if any(x in noun_tags for x in a.tag):
                    self._chunks_to_investigate.append(a)
                    i = 0
                    for x in a.tag:
                        # fix:  for some reason i didnt originally check if the length of the noun was greater than 1.
                        if x in noun_tags and len(a.text) > 1:
                            self._nouns.append(a.original_spacy_object[i])
                            try:
                                self._nouns_previous_word_tag.append(a.tag[i - 1])
                            except IndexError:
                                self._nouns_previous_word_tag.append(None)
                        i += 1
                else:
                    log.debug("Did not find appropriate chunk: %s, chunks: %s" % (self.message, a))

            else:
                if a.tag in noun_tags:
                    # chunk word count is less than 1. we need to account for this for some phrases
                    log.debug("chunk word length is 1 and contains noun: %s" % chunk.text)
        self._processed_sentence = chunks

    def _butt_vector_analyser(self, word):
        """check noun vector similarity to spatially funny objects/words/concepts."""
        # TODO: consider reducing weight value for not funny words/objects/concepts
        spatially_funny_objects = self._spacy("animal people structure machine car")
        # not_funny_objects = ["time", ]
        starting_weight = shared.phrase_weights.return_weight(word.text)
        working_weight = starting_weight
        self._similarities[word] = []
        for s in spatially_funny_objects:
            similarity = s.similarity(word)
            if similarity > .43:
                self._similarities[word].append("%s: %f" % (s, similarity))
                working_weight = int(working_weight + starting_weight * similarity)
        return working_weight

    def _get_word_weight(self, word, previous_tag):
        """combine vector analysis with posessive part-of-speeh increase if the sentence has it"""
        weight = self._butt_vector_analyser(word)
        posessive_pos_tag = ["PRP$"]
        if previous_tag in posessive_pos_tag:
            weight = weight * 25
        return weight
