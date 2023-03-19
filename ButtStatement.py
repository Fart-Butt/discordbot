from butt_chunk import ButtChunk
import shared
import logging
import butt_library as buttlib
import spacy

log = logging.getLogger('bot.' + __name__)


class ButtStatement:

    def __init__(self, message: str):
        self.db = shared.db["buttbot"]
        self.message: str = message
        self.__nlp = spacy.load('en_core_web_lg')
        self.chunks = []
        # process message
        self.__processed_message = self.__nlp(buttlib.strip_IRI(message))
        # extract noun chunks
        self.__processed_message_noun_chunks = self.__processed_message.noun_chunks
        # create message chunk objects
        self.chunks = self._create_buttchunks()

    def _create_buttchunks(self) -> list:
        """takes nlp processed message and creates ButtChunk objects for each identified spacy chunk that has more
        than one word."""
        chunks = []
        nouns = ["NN", "NNS", "NNP", "NNPS"]
        for chunk in self.__processed_message_noun_chunks:
            noun = []
            if len(chunk.text.split(" ")) > 1:
                for j in range(chunk.start, chunk.end):
                    if self.__processed_message[j].tag_ in nouns:
                        noun.append(self.__processed_message[j].text)
                if len(noun) > 1:
                    for n in noun:
                        chunks.append(
                            ButtChunk(self.db, self.__nlp, self.__processed_message, chunk, focusword=n)
                        )
                else:
                    chunks.append(
                        ButtChunk(self.db, self.__nlp, self.__processed_message, chunk)
                    )
        return chunks

    def get_good_chunks(self):
        good_chunks = []
        for a in self.chunks:
            if a.usable_chunk:
                good_chunks.append(a)
        return good_chunks

    def __repr__(self):
        return f"""
        ButtStatement
        original message: {self.message}
        chunks: 
            {self.chunks}
        """
