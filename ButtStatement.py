from butt_chunk import ButtChunk
from FinalizedButtChunk import FinalizedButtChunk
import shared
import logging
import butt_library as buttlib

log = logging.getLogger('bot.' + __name__)


class ButtStatement:

    def __init__(self, message, nlp, phraseweights):
        self.db = shared.db["buttbot"]
        self.message = message
        self.__nlp = nlp
        self.__phraseweights = phraseweights
        self.chunks = []
        # process message
        self.__processed_message = self.__nlp(buttlib.strip_IRI(self.message.content))
        # extract noun chunks
        self.__processed_message_noun_chunks = self.__processed_message.noun_chunks
        for x in self.__processed_message.noun_chunks:
            print("chunk: {}".format(x))
        # create message chunk objects
        self._create_buttchunks()

    def _create_buttchunks(self):
        for chunk in self.__processed_message_noun_chunks:
            if len(chunk.text.split(" ")) > 1:
                self.chunks.append(
                    ButtChunk(self.__phraseweights, self.db, self.__nlp, self.__processed_message, chunk))

    def __repr__(self):
        return """
        ButtStatement
        original message: {}
        chunks: 
            {}
        """.format(
            self.message.content,
            self.chunks
        )
