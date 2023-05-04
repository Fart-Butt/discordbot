import time
import logging
from butt_chunk import ButtChunk

log = logging.getLogger('bot.' + __name__)


class PhraseWeights:
    def __init__(self):
        # weighted phrases
        # butted messages we need to store
        self.messages = []

    def add_message(self, message, butt_chunk: ButtChunk):
        log.debug("got message id {} for noun {}".format(message, butt_chunk))
        self.messages.append([time.time(), message, butt_chunk])

    def get_messages(self):
        return self.messages

    def remove_message(self, _time, message, butt_chunk: ButtChunk):
        self.messages.remove([_time, message, butt_chunk])

    @staticmethod
    def process_reactions(reactions):
        negativeemojis = ['😕', '🙁', '☹', '😨', '😦', '😧', '👎', '😠', '😭', '😖', '👎', '💤', '🚫', '🔫', '❎', '😪']
        negative_emoji_guid = ['504537001845063680']
        downvotes = 0
        upvotes = 0
        log.debug("processing reactions")
        log.debug(reactions)
        for items in reactions:
            log.debug("new reaction")
            log.debug(items.emoji)
            try:
                if items.emoji in negativeemojis or items.emoji.id in negative_emoji_guid:
                    log.debug("downdoot")
                    downvotes = downvotes + items.count
                else:
                    log.debug("updoot")
                    upvotes = upvotes + items.count
            except AttributeError:
                # items.emoji.id not defined
                if items.emoji in negativeemojis:
                    log.debug("downdoot")
                    downvotes = downvotes + items.count
                else:
                    log.debug("updoot")
                    upvotes = upvotes + items.count
        return (upvotes - downvotes) * 20  # set weight change to 20 for each vote
