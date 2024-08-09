from butt_chunk import ButtChunk
import shared
import logging
import butt_library as buttlib
import spacy
import decompound

log = logging.getLogger('bot.' + __name__)


class ButtStatement:

    def __init__(self, message: str):
        self.db = shared.db["buttbot"]
        self.message: str = message
        self.__nlp = spacy.load('en_core_web_lg')
        self.chunks: list[ButtChunk] = []
        self.good_chunks: list[ButtChunk] = []
        # process message
        self.processed_message = self.__nlp(buttlib.strip_IRI(buttlib.strip_discord_formatting(message)))
        # extract noun chunks
        self.__processed_message_noun_chunks = self.processed_message.noun_chunks
        # create message chunk objects
        self.chunks = self._create_buttchunks()

    def _create_buttchunks(self) -> list:
        """takes nlp processed message and creates ButtChunk objects for each identified spacy chunk that has more
        than one word."""
        chunks = []
        nouns = ["NN", "NNS", "NNP", "NNPS", "NOUN"]
        for chunk in self.__processed_message_noun_chunks:
            noun = []
            corrected_noun = ""
            if len(chunk.text.split(" ")) > 1:
                # detect chunks that have more than 1 noun.  If there are more than 1 noun, create multiple
                # butt_chunks per noun.
                for j in range(chunk.start, chunk.end):
                    if self.processed_message[j].pos_ in nouns:
                        noun.append(self.processed_message[j].text)
                if len(noun) > 1:
                    for n in noun:
                        if len(n) > 10:
                            # checking for compound closed word:
                            corrected_noun = self.compound_closed_noun(self.message, n)
                        chunks.append(
                            ButtChunk(self.db, self.__nlp, self.processed_message, chunk, focusword=n)
                        )
                        if corrected_noun:
                            chunks[-1].noun = corrected_noun

                else:
                    chunks.append(
                        ButtChunk(self.db, self.__nlp, self.processed_message, chunk)
                    )
                    if len(chunks[-1].noun) > 10:
                        # checking for compound closed word:
                        corrected_noun = self.compound_closed_noun(self.message, chunks[-1].noun)
                    if corrected_noun:
                        print(f"corrected noun {corrected_noun}")
                        chunks[-1].noun = corrected_noun
                        chunks[-1].corrected = True

        return chunks

    def compound_closed_noun(self, original_sentence: str, suspected_word: str):
        """hander for compound closed nouns. example: skullcrusher->buttcrusher"""
        decompounded_words = \
            list(decompound.sentence_to_words(str(suspected_word), use_common=True, top_limit=1).values())[0][0]
        print(f"decompounded words {decompounded_words}")
        processed_suspected_word = " ".join(decompounded_words)
        print(f"processed suspected words {processed_suspected_word}")
        processed_nouns = ""
        if len(min(decompounded_words, key=len)) > 3:
            print("yes")
            # all compound word components should be above len 3
            processed_sentence = self.__nlp(original_sentence.replace(str(suspected_word), processed_suspected_word))
            for i in processed_sentence:
                if i.text in decompounded_words and i.pos_ in ["NOUN", "NN", "NNS", "NNP", "NNPS"] and len(i.text) > 3:
                    processed_nouns = i.text
        return processed_nouns

    def get_good_chunks(self):
        for a in self.chunks:
            if a.usable_chunk:
                self.good_chunks.append(a)
        return self.good_chunks

    def _store(self, butted_sentence: str, channel_id: int, message_id: int):
        self.db.do_insert("""insert into statement_history
                          (original_sentence, 
                          butted_sentence, 
                          discord_channel_guid, 
                          discord_message_guid) 
                          values 
                          (%s, %s, %s, %s)""",
                          (self.message,
                           butted_sentence,
                           channel_id,
                           message_id)
                          )

    def store(self, butted_sentence: str, channel_id: int, message_id: int):
        logging.debug(f"storing sentence: {butted_sentence}")
        self._store(butted_sentence, channel_id, message_id)
        logging.debug(f"storing chunks")
        for c in self.chunks:
            logging.debug("storing chunk: {c}")
            c.store(message_id)

    def __repr__(self):
        return f"""
        ButtStatement
        original message: {self.message}
        chunks: 
            {self.chunks}
        """
