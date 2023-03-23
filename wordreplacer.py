import json
from random import *
from ButtStatement import ButtStatement
from butt_chunk import ButtChunk
from discord import Message
from typing import List, Union

import butt_library as buttlib
import shared
import logging

log = logging.getLogger('bot.' + __name__)


class WordReplacer:

    def __init__(self, stat_module):
        self.__stats = stat_module
        self.__wlist = self.__load_word_list()
        self.__command = {"nltk": 'wordreplacer'}

        # state variables
        self.message = ""
        self.original_sentence = ""
        self.buttstatementobject = ""
        self.usable_chunks = []
        self.butted_sentence = ""
        self.lets_butt_this_chunk = ''
        # self.should_we_butt = False  # this is the state variable that means butting should continue
        # self._priority_nouns = []
        # self._non_priority_nouns = []
        # self._word_is_plural = False
        # self._tagged_sentence = ""
        # self._original_sentence = ""
        # self._weight_of_picked_word = 0
        # self._word_passed_weight_check = False
        # self._final_sentence = ""
        # self._sentence_contains_stop_words = False
        # self.butted_sentence = ""
        # self._spacy_nouns = []
        # self._message_author = ""
        # self._spacy_tagged_sentence = ""
        # self._spacy_finalized_nouns = []
        # self._spacy_finalized_weights = []
        # self._message_channel = 0
        # self._message_guild = 0
        # self._spacy_processed_nouns = ""

    def __state_reset(self):
        self.message = ""
        self.original_sentence = ""
        self.buttstatementobject = ""
        self.usable_chunks = []
        self.butted_sentence = ""
        self.lets_butt_this_chunk = ''
        '''
        self.should_we_butt = False  # this is the state variable that means butting should continue
        self._priority_nouns = []
        self._non_priority_nouns = []
        self._word_is_plural = False
        self._tagged_sentence = ""
        self._original_sentence = ""
        self._weight_of_picked_word = 0
        self._word_passed_weight_check = False
        self._final_sentence = ""
        self._sentence_contains_stop_words = False
        self._selected_noun_pair_to_butt = ButtChunk
        self.butted_sentence = ""
        self._spacy_nouns = []
        self._message_author = ""
        self._spacy_tagged_sentence = ""
        self._spacy_finalized_nouns = []
        self._spacy_finalized_weights = []
        self._message_channel = 0
        self._message_guild = 0
        self._spacy_processed_nouns = ""
        '''

    def __set_max_sentence_length(self, length):
        # DPT requested feature
        # a length of 0 will default to any word length.
        if length > 0:
            self._sentence_max_length = length
        else:
            self._sentence_max_length = 9999

    @staticmethod
    def __load_word_list():
        try:
            with open('wordlist.txt') as f:
                return json.load(f)
        except Exception:
            pass

    def __save(self):
        with open('wordlist.txt', 'w') as f:
            json.dump(self.__wlist, f, ensure_ascii=False)

    def rspeval(self, message):
        message = message.lower()
        for _ in self.__wlist:  # replace everything aaaaaaa
            message = message.replace('butt', self.__wlist[randint(0, len(self.__wlist) - 1)], 1)
        return message

    # def __get_phrase_weight(self, phrase):
    # TODO: needed?
    #    return self.__phraseweights.return_weight(phrase)

    def __is_user_an_allowed_bot(self, mo: Message) -> bool:
        if mo.author.id in shared.guild_configs[mo.guild.id].allowed_bots():
            return True
        else:
            return False

    def print_debug_message(self):
        print("--------------------------------------------------------------------------------------------")
        print("Original message: %s" % self.original_sentence)
        print("buttstatement: %s" % self.buttstatementobject)
        print("--------------------------------------------------------------------------------------------")

    def log_disposition(self):
        pass
        '''
        log.debug("saving disposition")
        try:
            self.__stats.disposition_store(self._message_guild, self._message_channel, self._original_sentence,
                                           self.__does_message_contain_stop_phrases(),
                                           self.__check_length_of_sentence_to_butt(self._message_channel),
                                           str(self._spacy_nouns),
                                           str(self._spacy_processed_nouns),
                                           str(self._spacy_finalized_weights),
                                           str(self._selected_noun_pair_to_butt.text),
                                           self.__check_if_picked_phrase_weight_passes_minimum(),
                                           self.butted_sentence
                                           )
        except AttributeError:
            self.__stats.disposition_store(self._message_guild, self._message_channel, self._original_sentence,
                                           self.__does_message_contain_stop_phrases(),
                                           self.__check_length_of_sentence_to_butt(self._message_channel),
                                           str(self._spacy_nouns),
                                           str(self._spacy_processed_nouns),
                                           str(self._spacy_finalized_weights),
                                           "None",
                                           self.__check_if_picked_phrase_weight_passes_minimum(),
                                           self.butted_sentence
                                           )
        '''

    def __does_message_contain_stop_phrases(self, messageobject: Message) -> bool:
        if not any(v for v in shared.guild_configs[messageobject.guild.id].stop_phrases if
                   v in self.original_sentence) and not (
                self.original_sentence.startswith("*") and self.original_sentence.endswith("*")):
            return False
        else:
            return True

    def perform_text_to_butt(self, messageobject: Message) -> str:
        self.__state_reset()
        """takes a messageobject from discord and sanity checks the butted phrase to determine if we should butt
        the sentence"""
        # we are going to manipulate this version of the message before sending it to the processing functions.
        # we remove stuff that we don't want to be processed (banned phrases, banned people, banned bots)
        self.message = messageobject
        self.original_sentence = messageobject.content
        if not buttlib.detect_code_block(self.original_sentence):
            # passes code block test
            if not self.__does_message_contain_stop_phrases(messageobject):
                # message contains no stop phrases, let's proceed
                if self.message.author.bot:
                    if self.__is_user_an_allowed_bot(messageobject):
                        self.buttstatementobject = self.process_bot_message(messageobject.content)
                else:
                    self.buttstatementobject = ButtStatement(buttlib.strip_IRI(messageobject.content))
                if len(self.buttstatementobject.get_good_chunks()) > 1 and \
                        self.__check_length_of_sentence_to_butt(messageobject):
                    # message is below length limit set on a per-guild basis
                    self.lets_butt_this_chunk = self.__pick_word_pair_to_butt(self.buttstatementobject)
                    # let's butt
                    self.butted_sentence = self._make_butted_sentence(self.lets_butt_this_chunk,
                                                                      self.buttstatementobject.message)

        if self.butted_sentence:
            return self.butted_sentence
        else:
            return ""

    def process_bot_message(self, mo: Message) -> str:
        if str(mo.content.author) == "Omnibot#0741" or str(mo.message.author) == "Spaigbot#7382":
            return buttlib.strip_IRI(mo.content.split(" ", 1)[1])
        else:
            return buttlib.strip_IRI(mo.content.split(" ", 1)[1])

    def do_butting_raw_sentence(self, message: Message) -> str:
        """always makes butted sentence.  skip all sanity checks that perform_text_to_butt does."""
        self.original_sentence = str(message.content)
        self.buttstatementobject = ButtStatement(message.content)
        if len(self.buttstatementobject.get_good_chunks()) > 1:
            # message is below length limit set on a per-guild basis
            self.lets_butt_this_chunk = self.__pick_word_pair_to_butt(self.buttstatementobject)
            # let's butt
            self.butted_sentence = self._make_butted_sentence(self.lets_butt_this_chunk, str(message.content))
            if self.butted_sentence:
                return self.butted_sentence
            else:
                return ""

    def do_butting_text(self, message: str) -> str:
        """always makes butted sentence.  skip all sanity checks that perform_text_to_butt does."""
        self.original_sentence = message
        bs = ButtStatement(message)
        if len(bs.get_good_chunks()) > 1:
            # message is below length limit set on a per-guild basis
            self.lets_butt_this_chunk = self.__pick_word_pair_to_butt(bs)
            # let's butt
            self.butted_sentence = self._make_butted_sentence(self.lets_butt_this_chunk, str(message))
            if self.butted_sentence:
                return self.butted_sentence
            else:
                return message

    def __pick_word_pair_to_butt(self, statement: ButtStatement) -> ButtChunk:
        """randomly selects a word pair to be the target of replacement."""
        return self.__pick_random_phrase_by_weight(statement.get_good_chunks())

    def __pick_random_phrase_by_weight(self, chunks: List[ButtChunk]) -> Union[ButtChunk, None]:
        try:
            total_sum_of_weights = sum(c.weight for c in chunks)
            randomweight = randrange(1, total_sum_of_weights)
            for i in chunks:
                randomweight = randomweight - i.weight
                if randomweight <= 0:
                    return i
        except ValueError:
            # no words to pick
            return None

    def __check_length_of_sentence_to_butt(self, messageobject: Message) -> bool:
        """checks to see if the tagged message length is lower than the limit set in the guild configuration file.
        this feature was originally requested by DPT."""
        if len(messageobject.content.split(" ")) > shared.guild_configs[messageobject.guild.id].max_sentence_length:
            return False
        else:
            return True

    def _replace_an_to_a_in_sentence(self, message: str, word_to_butt: str) -> str:
        """replaces an to a in a sentence, such as in the case where we replace "an apple" with "a butt" """
        message = message.split(" ")
        indexes = buttlib.get_indexes(message, word_to_butt)
        if indexes:
            # we found one or more instances of butt, we need to check the list index i-1 of that butt word to see if we
            # need to replace an with a.
            for i in indexes:
                try:
                    if message[i - 1] == "an":
                        message[i - 1] = "a"
                except IndexError:
                    # could be possible but we don't care
                    pass
        return " ".join(message)

    def _make_butted_sentence(self, chunk: ButtChunk, sentence: str) -> str:
        if chunk.noun_tag == "NNS":
            return self._replace_an_to_a_in_sentence(
                sentence.replace(
                    chunk.noun.text,
                    self._butt_in_proper_case(chunk, 'butts')
                ),
                "butts")
        else:
            return self._replace_an_to_a_in_sentence(
                sentence.replace(
                    chunk.noun.text,
                    self._butt_in_proper_case(chunk, 'butt')
                ),
                "butt")

    def _butt_in_proper_case(self, selected_chunk: ButtChunk, word: str) -> str:
        returnword = []
        if selected_chunk.noun.text.isupper():
            return word.upper()
        elif selected_chunk.noun.text.islower():
            return word
        else:
            for i in range(0, len(word)):
                try:
                    if selected_chunk.noun.text[i].isupper():
                        returnword.append(word[i].upper())
                    else:
                        returnword.append(word[i].lower())
                except IndexError:
                    # chunk noun is shorter than word, we can ignore this
                    returnword.append(word[i])
            return "".join(returnword)
