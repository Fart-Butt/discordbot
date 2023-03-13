class SimulatedDiscordAuthorObject():
    def __init__(self, bot=False):
        self.bot = bot


class SimulatedDiscordMessageObject():
    def __init__(self, bot=False):
        self.content = "They can just require the gm tier to require all points! It's not hard!"
        self.author = SimulatedDiscordAuthorObject(bot=bot)

# def test_word_replacer():
#    assert False
