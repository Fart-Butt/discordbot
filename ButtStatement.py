from butt_chunk import ButtChunk
import shared
import logging
import butt_library as buttlib
import spacy

log = logging.getLogger('bot.' + __name__)


class ButtStatement:

    def __init__(self, message):
        self.db = shared.db["buttbot"]
        self.message = message
        self.__nlp = spacy.load('en_core_web_lg')
        self.chunks = []
        # process message
        if self.message.author.bot:
            self.__processed_message = self.process_bot_message(self.message)
        else:
            self.__processed_message = self.__nlp(buttlib.strip_IRI(self.message.content))
        # extract noun chunks
        self.__processed_message_noun_chunks = self.__processed_message.noun_chunks
        for x in self.__processed_message.noun_chunks:
            print("chunk: {}".format(x))
        # create message chunk objects
        self.chunks = self._create_buttchunks()

    def _create_buttchunks(self) -> list:
        """takes nlp processed message and creates ButtChunk objects for each identified spacy chunk that has more
        than one word."""
        chunks = []
        for chunk in self.__processed_message_noun_chunks:
            if len(chunk.text.split(" ")) > 1:
                chunks.append(
                    ButtChunk(self.db, self.__nlp, self.__processed_message, chunk)
                )
        return chunks

    def process_bot_message(self, message):
        """tags sentence properly based if user is a bot. we assume these bots are relaying chat message from
        games such as minecraft or factorio."""
        if str(message.author) == "Omnibot#0741" or str(message.author) == "Spaigbot#7382":
            return self.__nlp(buttlib.strip_IRI(message.content.split(" ", 1)[1]))
        else:
            return self.__nlp(buttlib.strip_IRI(message.content))

    def __repr__(self):
        return f"""
        ButtStatement
        original message: {self.message.content}
        chunks: 
            {self.chunks}
        """
