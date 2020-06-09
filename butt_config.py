import shared
import logging

log = logging.getLogger('bot.' + __name__)


class ButtConfig:

    def __init__(self, guid: int):
        log.debug("Loading config for guid %d" % guid)
        shared.db["buttbot"].build()
        self.guid = guid
        self.allowed_channels_query = dict()
        self.stop_phrases_query = dict()
        self.conf = dict()
        self.allowed_bots_query = dict()
        self.banned_user_query = dict()
        self._load_config(self.guid)

    def _load_config(self, guid):
        self.allowed_channels_query = shared.db["buttbot"].do_query("select channel_guid "
                                                                    "from allowed_channels ac "
                                                                    "inner join config "
                                                                    "on config.guid = ac.guid "
                                                                    "where ac.guid = %s", (guid,))
        self.stop_phrases_query = shared.db["buttbot"].do_query("select phrase "
                                                                "from stop_processing_phrases spp "
                                                                "inner join config "
                                                                "on config.guid = spp.guid "
                                                                "where spp.guid = %s", (guid,))
        self.allowed_bots_query = shared.db["buttbot"].do_query("select bot_guid, minecraft_server "
                                                                "from whitelisted_bots wb "
                                                                "inner join config "
                                                                "on config.guid = wb.guid "
                                                                "where wb.guid = %s", (guid,))
        self.conf = shared.db["buttbot"].do_query("select config.* from config where guid = %s", (guid,))[0]
        self.banned_user_query = shared.db["buttbot"].do_query("select user_guid from banned_users where"
                                                               " guid = %s or globally_banned = TRUE", (guid,))
        log.debug("config loaded for guid %d" % guid)

    def reload(self):
        log.debug("RELOAD_CONFIG - reloading config for guid %d" % self.guid)
        self._load_config(self.guid)

    @staticmethod
    def do_query(query: str, args=()):
        shared.db["buttbot"].build()
        log.debug('running query: %s' % query)
        if args:
            shared.db["buttbot"].do_query(query, args)
        else:
            shared.db["buttbot"].do_query(query)

    def update_property(self, prop: str, value):
        query = "update config set {0} = %s where guid = %s".format(prop)
        shared.db["buttbot"].do_query(query, (value, self.guid))

    def insert_new_value(self, tab: str, row: str, val):
        query = "insert into {0} ({1}, guid) values(%s, %s)".format(tab, row)
        self.do_query(query, (val, self.guid))

    def delete_value(self, tab: str, row: str, val):
        query = "delete from {0} where {1} = %s and guid = %s".format(tab, row)
        self.do_query(query, (val, self.guid))

    @property
    def name(self) -> str:
        return self.conf["guild_name"]

    @property
    def exists(self) -> bool:
        return True

    @property
    def vacuum_url(self) -> str:
        return self.conf["vacuum_update_url"]

    @vacuum_url.setter
    def vacuum_url(self, setting):
        self.update_property("vacuum_update_url", setting)

    @property
    def command_freq(self) -> int:
        return self.conf["command_call_freq"]

    @property
    def shitpost_freq(self) -> int:
        return self.conf["shitpost_call_freq"]

    @name.setter
    def name(self, pla: str):
        self.update_property("guild_name", pla)

    @property
    def vacuum(self) -> bool:
        return bool(self.conf["vacuum"])

    @vacuum.setter
    def vacuum(self, setting: bool):
        self.update_property("vacuum", setting)

    @property
    def allowed_bots(self) -> list:
        return self.reformat_query_to_list(self.allowed_bots_query, "bot_guid")

    @property
    def allowed_channels(self) -> list:
        return self.reformat_query_to_list(self.allowed_channels_query, "channel_guid")

    @property
    def emojis(self) -> list:
        return self.conf["butt_response_emojis"]

    @property
    def banned_users(self) -> list:
        return self.reformat_query_to_list(self.banned_user_query, "user_guid")

    @property
    def stop_phrases(self) -> list:
        return self.reformat_query_to_list(self.stop_phrases_query, "phrase")

    def add_channel_to_allowed_channel_list(self, channel: int):
        self.insert_new_value("allowed_channels", "channel_guid", channel)

    def remove_channel_from_allowed_channel_list(self, channel: int):
        self.delete_value("allowed_channels", "channel_guid", channel)

    @property
    def rip(self) -> bool:
        return bool(self.conf["rip"])

    @rip.setter
    def rip(self, setting):
        self.update_property("rip", setting)

    @property
    def table_prefix(self) -> str:
        return self.conf["table_prefix"]

    @table_prefix.setter
    def table_prefix(self, setting):
        self.update_property("table_prefix", setting)

    @property
    def nsa_module(self) -> bool:
        return self.conf["NSA_module"]

    @nsa_module.setter
    def nsa_module(self, setting):
        self.update_property("NSA_module", setting)

    @property
    def f(self) -> bool:
        return self.conf["f"]

    @f.setter
    def f(self, setting: bool):
        self.update_property("f", setting)

    def add_always_ignore(self, user_guid: int):
        self.insert_new_value("banned_users", "user_guid", user_guid)
        pass

    def remove_always_ignore(self, user_guid: int):
        self.delete_value("banned_users", "user_guid", user_guid)
        pass

    def add_whitelisted_bots(self, user_guid: int):
        self.insert_new_value("whitelisted_bots", "bot_guid", user_guid)

    def remove_whitelisted_bots(self, user_guid: int):
        self.delete_value("whitelisted_bots", "bot_guid", user_guid)

    def is_bot_minecraft_relay(self, bot_guid: int) -> bool:
        try:
            return bool(
                next(item for item in self.allowed_bots_query if item["bot_guid"] == bot_guid)['minecraft_server']
            )
        except KeyError:
            return False

    @property
    def max_sentence_length(self):
        return self.conf["wordreplacer_max_sentence_length"]

    @property
    def wordreplacer(self):
        return self.conf["wordreplacer"]

    @staticmethod
    def reformat_query_to_list(data, field_name):
        items = []
        for i in data:
            items.append(i[field_name])
        return items


class Config(dict):
    def __init__(self):
        super().__init__()
        self.configs = {}
        self.load_config_for_startup()

    def __getitem__(self, attr: int):
        try:
            # will return valid config if it exists inside of the Config object.
            return self.configs[attr]
        except KeyError:
            # no key found, so we will load/make a configuration and then return it.
            self.create_config(attr)
            return self.configs[attr]

    def load_config(self, guid: int):
        # check to see if the config is in the database
        does_config_exist = shared.db["buttbot"].do_query("select count(%s) as count", (guid,))[0]
        if does_config_exist['count'] > 0:
            # we have it, going to make a new instance
            self.configs[guid] = ButtConfig(guid)
            if self.configs[guid].vacuum:
                log.info("subscribing to vaccum for %d" % guid)
                shared.vacuum_instance.subscribe(self.configs[guid])
            else:
                log.info("%d not configured for vacuum. skipping" % guid)
        else:
            # not in database, we need to generate a new
            self.create_config(guid)

    def all_configs(self):
        print(str(self.configs))

    def create_config(self, guid: int):
        log.info("creating configuration for guild %d" % guid)
        shared.db["buttbot"].do_insert_no_args("INSERT INTO config (wordreplacer,wordreplacer_max_sentence_length,"
                                               "vacuum,command_call_freq,shitpost_call_freq,butt_response_emojis,rip,"
                                               "f, guid) "
                                               "select wordreplacer,wordreplacer_max_sentence_length,vacuum,"
                                               "command_call_freq, shitpost_call_freq,butt_response_emojis,rip,f, {} "
                                               "as guid "
                                               "from config where guid = 101".format(guid))
        self.configs[guid] = ButtConfig(guid)

    def load_config_for_startup(self):
        # load all configs saved in the table
        guids = shared.db["buttbot"].do_query("select guid from config where 1")
        for g in guids:
            print("startup for %d" % g['guid'])
            log.debug("STARTUP - found config for %d, building config" % g['guid'])
            self.configs[g['guid']] = ButtConfig(g['guid'])
            if self.configs[g['guid']].vacuum:
                log.info("subscribing to vaccum for %d" % g['guid'])
                shared.vacuum_instance.subscribe(self.configs[g['guid']])
            else:
                log.info("%d not configured for vacuum. skipping" % g['guid'])
