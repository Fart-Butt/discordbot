import json
from random import *
from FinalizedButtChunk import FinalizedButtChunk
from ButtStatement import ButtStatement

import butt_library as buttlib
from ButtClassifier import ButtClassifier
import shared
import logging

log = logging.getLogger('bot.' + __name__)


class WordReplacer:

    def __init__(self, stat_module, phrase_weights, nlp_):
        self.__stats = stat_module
        self.__wlist = self.__load_word_list()
        self.__command = {"nltk": 'wordreplacer'}
        self.__phraseweights = phrase_weights

        # state variables
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
        self._selected_noun_pair_to_butt = FinalizedButtChunk
        self.butted_sentence = ""
        self._spacy_nouns = []
        self._message_author = ""
        self._spacy_tagged_sentence = ""
        self.nlp = nlp_
        self.butt_classifier = ButtClassifier(self.__phraseweights, self.nlp)
        self._spacy_finalized_nouns = []
        self._spacy_finalized_weights = []
        self._message_channel = 0
        self._message_guild = 0
        self._spacy_processed_nouns = ""

    def __state_reset(self):
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
        self._selected_noun_pair_to_butt = FinalizedButtChunk
        self.butted_sentence = ""
        self._spacy_nouns = []
        self._message_author = ""
        self._spacy_tagged_sentence = ""
        self._spacy_finalized_nouns = []
        self._spacy_finalized_weights = []
        self._message_channel = 0
        self._message_guild = 0
        self._spacy_processed_nouns = ""

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

    def return_commands(self):
        return self.__command

    def get_noun(self):
        return self._selected_noun_pair_to_butt.text

    def __save(self):
        with open('wordlist.txt', 'w') as f:
            json.dump(self.__wlist, f, ensure_ascii=False)

    def rspeval(self, message):
        message = message.lower()
        for t in self.__wlist:  # replace everything aaaaaaa
            message = message.replace('butt', self.__wlist[randint(0, len(self.__wlist) - 1)], 1)
        return message

    def __get_phrase_weight(self, phrase):
        return self.__phraseweights.return_weight(phrase)

    def __is_user_an_allowed_bot(self, author):
        if author in shared.guild_configs[self._message_channel].get_all_allowed_bots():
            return True
        else:
            return False

    def print_debug_message(self):
        print("--------------------------------------------------------------------------------------------")
        print("Original message: %s" % self._original_sentence)
        print("Message contain stop phrase? %s" % str(self.__does_message_contain_stop_phrases()))
        print("Message meet length requirement? (server setting: %i) %s" % (
            shared.guild_configs[self._message_guild].max_sentence_length,
            self.__check_length_of_sentence_to_butt(self._message_channel)))
        print("Spacy noun chunk(s): %s" % self._spacy_nouns)
        try:
            print("Spacy processed sentence: %s " % self._spacy_tagged_sentence)
        except AttributeError:
            print("Spacy processed sentence: None")
        try:
            print("Spacy noun chunk(s): %s " % self._spacy_processed_nouns)
            print("weights: %s" % self._spacy_finalized_weights)
        except AttributeError:
            print("Spacy noun chunk(s): None")
        try:
            print("Selected noun pair: %s" % str(self._selected_noun_pair_to_butt.text))
        except AttributeError:
            print("Selected noun pair: None")
        print("Passes weight minimum? %s" % str(self.__check_if_picked_phrase_weight_passes_minimum()))
        print("Butted sentence: %s" % self.butted_sentence)
        print("--------------------------------------------------------------------------------------------")

    def log_disposition(self):
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

    def __does_message_contain_stop_phrases(self):
        if not any(
                v for v in shared.guild_configs[self._message_guild].stop_phrases if
                v in self._original_sentence) and not (
                self._original_sentence.startswith("*") and self._original_sentence.endswith("*")):
            return False
        else:
            return True

    def successful_butting(self):
        return self.__check_if_picked_phrase_weight_passes_minimum()

    def perform_text_to_butt(self, messageobject):
        """takes a messageobject from discord and sanity checks the butted phrase to determine if we should butt
        the sentence"""
        # we are going to manipulate this version of the message before sending it to the processing functions.
        # we remove stuff that we dont want to be processed (banned phrases, banned people, banned bots)
        self.__state_reset()
        self._message_guild = messageobject.guild.id
        self._original_sentence = messageobject.content
        self._message_author = str(messageobject.author)
        self._message_channel = messageobject.channel.id
        if not buttlib.detect_code_block(self._original_sentence):
            # passes code block test
            if not self.__does_message_contain_stop_phrases():
                # message contains no stop phrases, let's proceed
                if messageobject.author.bot:
                    pass
                    # self.__tag_sentence(True)
                else:
                    pass
                    #self.__tag_sentence()
                if self._tagged_sentence and self.__check_length_of_sentence_to_butt(messageobject.guild.id):
                    # TODO: modify the above two functions for spacy
                    # message is below length limit set on a per-guild basis
                    self.__get_word_pairs_from_all_sources()
                    self.__pick_word_pair_to_butt()
                    if self.__check_if_picked_phrase_weight_passes_minimum():
                        # let's butt
                        self.__make_butted_sentence()

    def do_butting_raw_sentence(self, message):
        """always makes butted sentence.  skip all sanity checks that perform_text_to_butt does."""
        self.__state_reset()
        self._original_sentence = str(message)
        print("yes")
        bs = ButtStatement(message, self.nlp, self.__phraseweights)
        print(bs)

    #        self.__get_word_pairs_from_all_sources()
    #        self.__pick_word_pair_to_butt()
    #        self.__make_butted_sentence()
    #        return self.butted_sentence

    def __tag_sentence(self, split_for_bot=False):
        """tags sentence properly based if user is a bot. we assume these bots are relaying chat message from
        games such as minecraft or factorio."""
        if split_for_bot:
            # message sender is allowed bot, we should separate the first word out of the message since that
            # is the user the bot is relaying for
            # support for DPT Omnibot
            if self._message_author == "Omnibot#0741" or self._message_author == "Spaigbot#7382":
                self._tagged_sentence = self.nlp(buttlib.strip_IRI(self._original_sentence.split(" ", 1)[1]))
            else:
                self._tagged_sentence = self.nlp(buttlib.strip_IRI(self._original_sentence.split(" ", 1)[1]))
        else:
            self._tagged_sentence = self.nlp(buttlib.strip_IRI(self._original_sentence))

    def __check_if_picked_phrase_weight_passes_minimum(self):
        try:
            if self._selected_noun_pair_to_butt.weight <= 501:
                # dont send anything, this word probably sucks
                return False
            else:
                if len(self._selected_noun_pair_to_butt.text) > 1:
                    return True
                else:
                    return False
        except AttributeError:
            # selected nouns to butt is empty
            return False

    def __get_word_pairs_from_all_sources(self):
        self.butt_classifier.classify_butts(self._tagged_sentence)
        self._spacy_tagged_sentence = self.butt_classifier.get_processed_sentence()
        self._spacy_finalized_nouns = self.butt_classifier.get_nouns()
        self._spacy_processed_nouns = self.butt_classifier.get_pretty_noun_format()
        for a in self._spacy_finalized_nouns:
            self._spacy_finalized_weights.append(
                "%s (%s, %s). Similarities: %s" % (a.text, a.tag, a.weight, a.similarities))

    def __pick_word_pair_to_butt(self):
        """randomly selects a word pair to be the target of replacement."""
        # remove all 1 length words
        self._selected_noun_pair_to_butt = self.__pick_random_phrase_by_weight(self._spacy_finalized_nouns)

    def __pick_random_phrase_by_weight(self, word_list):
        total_sum_of_weights = self.__sum_all_weights(word_list)
        try:
            randomweight = randrange(1, total_sum_of_weights)
            for i in word_list:
                randomweight = randomweight - i.weight
                if randomweight <= 0:
                    return i
        except ValueError:
            # no words to pick
            return None

    @staticmethod
    def __sum_all_weights(word_list):
        return sum(word.weight for word in word_list)

    @staticmethod
    def __butt_in_proper_case(wordtobutt, buttoreplace):
        # todo: check if needed for new system
        if wordtobutt.istitle():
            return buttoreplace.title()
        elif wordtobutt.isupper():
            return buttoreplace.upper()
        else:
            return buttoreplace

    @staticmethod
    def __word_passes_stop_word_check(word):
        """checks to see if selected word passes stopword check - eliminates common crappy words and internet slang
         that are tagged as nouns but either aren't funny to replace or aren't nouns."""
        stopwords = ['gon', 'dont', 'lol', 'yeah', 'tho', 'lmao', 'yes', 'way']
        if len(word) < 2 or word in stopwords:
            return False
        else:
            return True

    def __does_message_have_prioritized_parts_of_speech(self):
        """takes a tagged sentence and checks if it contains a personal posessive pronoun - we want to specially
        target that for funny replaces like "my butt" """
        wordtagstocheckprioritized = ['PRP$']  # posessive personal pronoun
        if any(t for t in self._tagged_sentence if t[1] in wordtagstocheckprioritized):
            return True
        else:
            return False

    def __check_length_of_sentence_to_butt(self, message_guid: int):
        """checks to see if the tagged message length is lower than the limit set in the guild configuration file.
        this feature was originally requested by DPT."""
        if len(self._original_sentence) > shared.guild_configs[message_guid].max_sentence_length:
            return False
        else:
            return True

    @staticmethod
    def __replace_an_to_a_in_sentence(message, butt_word):
        """replaces an to a in a sentence, such as in the case where we replace "an apple" with "a butt" """
        message = message.split(" ")
        indexes = buttlib.get_indexes(message, butt_word)
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

    def __make_butted_sentence(self):
        if self._selected_noun_pair_to_butt.tag == "NNS":
            self.butted_sentence = self.__replace_an_to_a_in_sentence(
                self._original_sentence.replace(self._selected_noun_pair_to_butt.text,
                                                self.__butt_in_proper_case(self._selected_noun_pair_to_butt.text,
                                                                           'butts')), "butts")
        else:
            self.butted_sentence = self.__replace_an_to_a_in_sentence(
                self._original_sentence.replace(self._selected_noun_pair_to_butt.text,
                                                self.__butt_in_proper_case(self._selected_noun_pair_to_butt.text,
                                                                           'butt')), "butt")
