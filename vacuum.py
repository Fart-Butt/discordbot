import datetime
import http.client
import json
import urllib.error
import urllib.request
import random

from dateutil.parser import parse


class Vacuum:
    def __init__(self, db):
        self.players = []
        self.playtime_load()
        self.db = db
        self.command = {'lastseen': 'vacuum', 'playtime': 'vacuum', 'howchies': 'vacuum', 'ouchies': 'vacuum',
                        'deathsperhour': 'vacuum', 'alias': 'vacuum'}
        self.updateurl = ""
        self.config = ""
        self.scraper_timer = datetime.datetime.utcnow()

        try:
            if self.players:
                pass
        except TypeError:
            # variable is empty instead of being an empty list
            self.players = []

    def return_commands(self):
        return self.command

    def update_url(self, url):
        self.updateurl = url

    ################################################################################
    #                               commands                                       #
    ################################################################################
    def do_lastseen(self, player):
        try:
            if player:
                returnz = self.lastseen(player)
                if returnz:
                    return returnz
        except IndexError:
            return "who am i looking for?"

    def do_playtime(self, player):
        try:
            if player:
                returnz = self.playtime_insult(player)
                if returnz:
                    return returnz
            else:
                return self.playtime_global()
        except IndexError:
            return self.playtime_global()

    def do_howchies(self, message):
        if message:
            return "People who died to " + message + ": " + self.howchies_profile(message)
        else:
            return 'Heres whats killing you: ' + self.top_10_death_reasons()

    def do_ouchies(self, message):
        if message:
            return "Deaths for %s: %s" % (message, self.ouchies_profile(message))
        else:
            return 'Top 10 ouchies: %s' % self.top_10_deaths()

    def do_deathsperhour(self, message):
        return self.deathsperhour(message)

    def do_alias(self, player):
        names = self.player_alias(player)

        if len(names) == 0:
            return "I dont think i've ever seen that butt"
        elif len(names) == 1:
            return "I've only seen this jerk as %s" % names[0]
        else:
            return "I've seen this jerk play as %s" % ", ".join(names)

    ################################################################################
    #                               end commands                                   #
    ################################################################################
    def player_alias(self, player):
        self.db.build()
        r = self.db.do_query("select player_name from minecraft_players where player_guid ="
                             " (select player_guid as guid from minecraft_players where player_name = %s)", (player,))
        names = []
        for re in r:
            names.append(re['player_name'])

        return names

    def config(self, url, mode):
        self.updateurl = url
        self.master_config = mode

    def playtime_global(self):
        players = self.db.do_query(
            "select abs(sum(timedelta)) as seconds, count(timedelta)"
            " as sessions, player from progress_playertracker_v2 group by player")
        self.db.close()
        total_seconds = 0
        total_sessions = 0
        for p in players:
            total_seconds = total_seconds + int(p['seconds'])
            total_sessions = total_sessions + p['sessions']
        days, remainder = divmod(total_seconds, 86400)
        hours, remainder = divmod(remainder, 3600)
        return ("These fucking nerds have played %s days, %s hours worth of meincraft over %s sessions" % (
            days, hours, total_sessions))

    def playtime_single(self, player):
        time = self.db.do_query(
            "select sum(progress_playertracker_v2.timedelta) as seconds, "
            "count(progress_playertracker_v2.timedelta) as sessions "
            "from progress.progress_playertracker_v2 where player in "
            "(select player_name from progress.minecraft_players "
            "where player_guid = (select player_guid as guid from progress.minecraft_players where player_name = %s))",
            (player,))
        self.db.close()
        return [time[0]['seconds'], time[0]['sessions']]

    def playtime_insult(self, player):
        a = self.playtime_single(player)
        totaltime = a[0]
        sessions = a[1]
        if not totaltime == 0:
            m, s = divmod(totaltime, 60)
            h, m = divmod(m, 60)
            insult = ""
            if h > 1000:
                insult = ". i found kurr lol"
            elif h > 150:
                insult = ". why are you still so bad at this game"
            elif h > 80:
                insult = ". is this shit your full time job or something"
            elif h > 50:
                insult = ". go outside you fuckin nerd"
            elif h > 30:
                insult = ". don't you have something better to do with your time?"
            elif h < 25:
                insult = ". weak"

            return "Estimated playtime for %s: %d hours %d minutes in %s sessions%s" % (player, h, m, sessions, insult)
        else:
            return "bitch dont play"

    def playtime_player_started_current_session(self, player):
        if self.playtime_player_active(player):
            for p in self.players:
                if p[0] == player:
                    return p[1]
        else:
            return 0

    def playtime_current_session_timedelta(self, player):
        if self.playtime_player_active(player):
            return self.playtime_player_deltaseconds(self.playtime_player_started_current_session(player))
        else:
            return 0

    def deaths_per_hour_current_session(self, player):
        session_start = self.playtime_player_started_current_session(player)
        played_this_session_hours = self.playtime_current_session_timedelta(player) / 60 / 60
        deaths_this_session = self.db.do_query("SELECT count(player) as deaths FROM `progress_deaths` WHERE"
                                               " player = %s and datetime > %s", (player, session_start))[0]['deaths']
        return deaths_this_session / played_this_session_hours

    def playtime_scraper(self):
        print("running scraper")
        d = self.scraper_timer - datetime.datetime.utcnow()
        if abs(int(d.total_seconds())) < 10:
            # this dumb thing ran less than 10 second ago
            print("last run: %d" % self.scraper_timer)
            print("differential: %s" % str(d))
            print("WHY IS THIS SHIT RUNNING")
        else:
            try:
                with urllib.request.urlopen(self.updateurl) as url:
                    data = json.loads(url.read().decode())
                    pl = data['players']
                    query_data = list()
                    players = []
                    for p in pl:
                        print("found player %s" % p['name'])
                        query_data.append((
                            datetime.datetime.utcnow(),
                            p['name'],
                            p['world'],
                            p['x'],
                            p['y'],
                            p['z']
                        ))
                        if not p['name'] in players:
                            players.append(p['name'])
                        # we start by checking to see if the player is currently active
                        if self.playtime_player_active(p['name']):
                            print("%s already in, not adding to list." % p['name'])
                            pass
                            # player was logged in, and is still logged in
                            # we do not need to do anything for this player at this time.
                        else:
                            print("adding player %s since they have logged in" % p['name'])
                            # player was not logged in, but is logged in now.
                            self.playtime_player_addplayer(p['name'])
                    # now we are going to find players that have logged out since the last check
                    print("players list:")
                    print(self.players)
                    print("end players list")
                    self.db.do_insertmany("INSERT INTO `progress_NSA_module`"
                                          "(`datetime`, `player`, `dimension`, `x`, `y`, `z`) "
                                          "VALUES (%s, %s, %s, %s, %s, %s)", query_data)
                    self.playtime_player_checkplayers(players)
                    self.scraper_timer = datetime.datetime.utcnow()
                    print("------------scraper completed--------------")

            except urllib.error.URLError:
                # minecraft server is offline and buttbot is still online
                self.playtime_player_saveall()
                print("urllib.error.urlerror")

            except http.client.RemoteDisconnected:
                # we are going to save all data here too
                self.playtime_player_saveall()
                print("http.client.remotedisconnected")

            finally:
                pass

    def playtime_player_checkplayers(self, players):
        print("starting checkplayers")
        try:
            for e in self.players:
                print("on player %s" % e[0])
                if e[0] in players:
                    print("still in game")
                    pass
                    # person is still logged in. we do not need to do anything at this time.
                else:
                    # log that they logged out
                    print("logged out")
                    self.playtime_player_record(e[0], self.playtime_player_deltaseconds(e[1]))
                    self.playtime_player_removeplayer(e)
        except TypeError:
            # something went wrong with variable initialization.
            self.players = []
            self.playtime_player_checkplayers(players)
        finally:
            print("end checkplayer")

    @staticmethod
    def playtime_player_deltaseconds(starttime):
        d = starttime - datetime.datetime.utcnow()
        d = abs(int(d.total_seconds()))
        if d > 20:
            d = d - 10
        return d

    def playtime_player_saveall(self):
        for e in self.players:
            self.playtime_player_record(e[0], self.playtime_player_deltaseconds(e[1]))
            # remove player.
            self.playtime_player_removeplayer(e)

    def playtime_player_record(self, player, deltatime):
        print("going to do query: user is %s and timedetla is %s" % (player, deltatime))
        self.db.do_insert("INSERT into `progress_playertracker_v2` (`player`,`timedelta`,`datetime`) values (%s,%s,%s)",
                          (player, deltatime, datetime.datetime.utcnow()))
        self.db.close()

    def playtime_player_addplayer(self, player):
        self.players.append([player, datetime.datetime.utcnow()])
        self.playtime_serialize()

    def playtime_player_removeplayer(self, player):
        print("removing player %s" % player)
        self.players.remove(player)
        self.playtime_serialize()

    def playtime_player_active(self, player):
        try:
            if any(e[0] == player for e in self.players):
                return True
            else:
                return False
        except AttributeError:
            # the self.players variable is empty.  This can happen when the bot first turns on or when a player joins
            # and no one else is logged in.
            return False

    def playtime_serialize(self):
        with open('players.txt', 'w') as f:
            json.dump(self.players, f, ensure_ascii=False, default=str)

    def playtime_load(self):
        try:
            with open('players.txt') as f:
                self.players = json.load(f)
        except FileNotFoundError:
            # nothing special needs to happen here
            pass
        for i in self.players:
            i[1] = parse(i[1])

    def lastseen(self, player):
        lastseen = self.db.do_query(
            "select datetime from progress_playertracker_v2 where player=%s order by datetime desc limit 1", (player,))
        self.db.close()
        try:
            lastseen = lastseen[0]['datetime']
            now = datetime.datetime.utcnow()

            timedelta = now - lastseen
            seconds = abs(timedelta.total_seconds())
            if seconds > 15:
                days, remainder = divmod(seconds, 86400)
                hours, remainder = divmod(remainder, 3600)
                return 'last saw %s %s days %s hours ago' % (player, int(days), int(hours))
            else:
                return "Did you remember to wear your helmet today, honey?"
        except IndexError:
            return "Havent seen em"

    def deathsperhour_list(self):
        dph = self.db.do_query(
            "select T.player, COALESCE(D.deaths, 0) / (sum(T.timedelta) / 60 / 60) as deaths_per_hour"
            "FROM progress.progress_playertracker_v2 as T left join(SELECT count(D.player) as deaths, "
            "D.player from progress.progress_deaths D GROUP BY D.player) D ON T.player = D.player group by"
            "T.player ORDER BY deaths_per_hour DESC LIMIT 10"
        )
        if dph:
            return self.sort(dph, 'player', 'deaths_per_hour')

    def deathsperhour(self, player):
        dph = self.db.do_query(
            "select T.player, COALESCE(D.deaths, 0) / (sum(T.timedelta)/60/60) as deaths_per_hour FROM "
            "progress.progress_playertracker_v2 as T left join (SELECT count(D.player) as deaths, D.player"
            " from progress.progress_deaths D where player=%s GROUP BY D.player) D"
            " ON T.player = D.player where T.player=%s group by T.player", (player, player))
        self.db.close()

        try:
            if dph[0]['deaths_per_hour'] > 0:
                # good return
                if dph[0]['deaths_per_hour'] > 1:
                    insults = [
                        "my hero",
                        "a true gaming legend"
                    ]
                    insult = insults[random.randrange(0, len(insults) - 1)]

                else:
                    insult = "you should try harder"
                try:
                    dph_session = int(self.deaths_per_hour_current_session(player))
                except ZeroDivisionError:
                    # no deaths on current session
                    dph_session = 0
                if dph_session > 0:
                    dph_ses = " (% s deaths per hour this session)" % str(dph_session)
                else:
                    dph_ses = ""
                return "deaths per hour for %s is %s%s. %s" % \
                       (player,
                        str(dph[0]['deaths_per_hour']),
                        dph_ses,
                        insult)
            else:
                comments = [
                    "%s is the most boring person on the server",
                    "actually, %s is just a gaming god",
                    "persistence is key for %s",
                    "%s is a god among mortals"
                ]
                return comments[random.randrange(0, len(comments)) - 1] % player
        except IndexError:
            return "%s doesnt play" % player

        # noinspection PyBroadException

    def get_player_coords(self, player):
        try:
            with urllib.request.urlopen(self.updateurl) as url:
                data = json.loads(url.read().decode())
                pl = data['players']
                for p in pl:
                    if p['name'] == player:
                        return {'x': p['x'], 'y': p['y'], 'z': p['z'], 'world': p['world']}
        except Exception:
            # we dont actually really care what the error is here, theres too many inside of url for me to care.
            # i'm just going to return the error handling coords:
            return {'x': 0, 'y': 0, 'z': 0, 'world': 'Exception Handling'}

    def add_death_message(self, message):
        m = message.split()
        m[1] = m[1].lower()  # case insensitivity support for player name
        coords = self.get_player_coords(m[1])
        # now i need to combine the death reason into a string, which will be words in positions 2-n of the death
        # message 'm'
        dmsg = ''
        if m[2] == 'was':
            for i in m[3:]:
                dmsg = dmsg + " " + i
        else:
            for i in m[2:]:
                dmsg = dmsg + " " + i
        dmsg = dmsg.strip()
        try:
            self.db.do_insert(
                "INSERT INTO `progress_deaths` (`player`,`message`,`world`,`x`,`y`,`z`,`datetime`)"
                "VALUES(%s, %s, %s, %s, %s, %s, %s);",
                (m[1], dmsg, coords['world'], coords['x'], coords['y'], coords['z'], datetime.datetime.utcnow()))
        except TypeError:
            # catch this error, something that i dont believe should be possible with how this is set up but?????
            self.db.do_insert(
                "INSERT INTO `progress_deaths` (`player`,`message`,`world`,`x`,`y`,`z`,`datetime`)"
                "VALUES(%s, %s, %s, %s, %s, %s, %s);",
                (m[1], dmsg, "Exception Handling", 0, 0, 0, datetime.datetime.utcnow()))
        self.db.close()

    def top_10_deaths(self):
        result = self.db.do_query(
            "SELECT player, count(*) as `count` FROM `progress_deaths` GROUP BY player ORDER BY count DESC LIMIT 10",
            '')
        self.db.close()
        if result:
            return self.sort(result, 'player', 'count')
        else:
            pass

    def howchies_profile(self, message):
        result = self.db.do_query(
            "SELECT player, count(*) as `count` FROM `progress_deaths` where match(message) against (%s)"
            "GROUP BY player ORDER by count DESC",
            message)
        self.db.close()
        if result:
            return self.sort(result, 'player', 'count')
        else:
            return 'No deaths recorded'

    def ouchies_profile(self, player):
        result = self.db.do_query(
            "SELECT message,count(*) as `count` FROM `progress_deaths` WHERE player=%s"
            " GROUP BY message ORDER BY count DESC",
            (player,))
        self.db.close()
        if result:
            return self.sort(result, 'message', 'count')
        else:
            return 'No deaths recorded'

    def top_10_death_reasons(self):
        result = self.db.do_query(
            "SELECT message, count(*) as `count` FROM `progress_deaths` "
            "GROUP BY message ORDER BY count DESC LIMIT 10",
            '')
        self.db.close()
        if result:
            return self.sort(result, 'message', 'count')
        else:
            pass

    def have_we_seen_player(self, player):
        current_server_result = self.db.do_query(
            "select count(datetime) from progress_playertracker_v2 where player=%s", (player,))
        previous_server_result = self.db.do_query(
            "select count(datetime) from progress_playertracker_v2_old where player=%s", (player,))
        self.db.close()
        if current_server_result[0]['count(datetime)'] == 0:
            # new player
            if previous_server_result[0]['count(datetime)'] > 0:
                comments = [
                    "welcome back to progress, %s",
                    "fuck, %s is back",
                    "who let %s back in?",
                    "who gave %s the new IP address?",
                    "%s is back to top ouchies!"
                ]
                message = comments[random.randrange(0, len(comments) - 1)]
                return message % player
            else:
                return "welcome to progress %s" % player

    @staticmethod
    def sort(target, t1, t2):
        cmsg = ''
        i = 1
        for d in target:
            if i != 1:
                cmsg = cmsg + ', '
            cmsg = cmsg + d[t1] + '(' + str(d[t2]) + ')'
            i = i + 1
        return cmsg
