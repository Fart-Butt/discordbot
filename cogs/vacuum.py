import logging
from discord.ext.commands import Bot, Cog, Context, command, BucketType
from discord.ext import commands
from shared import db, shitpost
import datetime
import random
import asyncio

log = logging.getLogger('bot.' + __name__)


class VacuumCog(Cog):

    def __init__(self, bot: Bot):
        self.bot = bot

    @command()
    @commands.cooldown(1, 10, BucketType.guild)
    async def gaminggods(self, ctx: Context):
        """lets you know who is boss"""
        result = db["minecraft"].do_query(
            "select T.player, format(sum(T.timedelta)/60/60, 1) as time "
            "FROM progress_playertracker_v2 as T "
            "left join(SELECT count(D.player) as deaths, D.player from progress_deaths D GROUP BY D.player) D "
            "ON T.player = D.player "
            "where coalesce(deaths,0) = 0 "
            "group by player DESC "
            "having sum(T.timedelta) > 3600")
        if len(result) > 1:
            # normal return
            async with ctx.typing():
                await asyncio.sleep(4)
            await ctx.send("here are your gaming gods: %s" % self.sort(result, 'player', 'time', " hours"))
        elif len(result) == 1:
            async with ctx.typing():
                await asyncio.sleep(4)
                comments = ["https://www.youtube.com/watch?v=wubnFmYYfHs",
                            "https://www.youtube.com/watch?v=iLBBRuVDOo4",
                            "https://media.giphy.com/media/JoV2BiMWVZ96taSewG/giphy.gif"
                            ]
                r = comments[random.randrange(0, len(comments)) - 1]
            await ctx.send("only %s is left. %s" % (result['player'], r))
        else:
            async with ctx.typing():
                await asyncio.sleep(4)
            await ctx.send(shitpost.do_butting_raw_sentence("this world is without any gaming gods"))
            # no one left

    @command()
    @commands.cooldown(1, 10, BucketType.guild)
    async def lastseen(self, ctx: Context, *args):
        """i wonder where they went?"""
        log.debug("LASTSEEN - arguments are %s" % args)
        try:
            player = args[0]
            if player:
                lastseen = db["minecraft"].do_query(
                    "select datetime from progress_playertracker_v2 "
                    "where player=%s order by datetime desc limit 1".format(),
                    (player,)
                )
                db["minecraft"].close()
                try:
                    lastseen = lastseen[0]['datetime']
                    now = datetime.datetime.utcnow()

                    timedelta = now - lastseen
                    seconds = abs(timedelta.total_seconds())
                    if seconds > 15:
                        days, remainder = divmod(seconds, 86400)
                        hours, remainder = divmod(remainder, 3600)
                        async with ctx.typing():
                            await asyncio.sleep(3)
                        await ctx.send('last saw %s %s days %s hours ago' % (player, int(days), int(hours)))
                    else:
                        async with ctx.typing():
                            await asyncio.sleep(3)
                        await ctx.send("Did you remember to wear your helmet today, honey?")
                except IndexError:
                    async with ctx.typing():
                        await asyncio.sleep(3)
                    await ctx.send("Havent seen em")
        except IndexError:
            async with ctx.typing():
                await asyncio.sleep(3)
            await ctx.send("who am i looking for?")

    @command()
    @commands.cooldown(1, 10, BucketType.guild)
    async def playtime(self, ctx: Context, *args):
        """watch the muscle atrophy in real time"""
        try:
            player = args[0]
            if player:
                returnz = self.playtime_insult(player)
                if returnz:
                    async with ctx.typing():
                        await asyncio.sleep(3)
                    await ctx.send(returnz)
            else:
                async with ctx.typing():
                    await asyncio.sleep(3)
                await ctx.send(self.playtime_global())
        except IndexError:
            async with ctx.typing():
                await asyncio.sleep(3)
            await ctx.send(self.playtime_global())

    @staticmethod
    def playtime_global():
        players = db["minecraft"].do_query(
            "select abs(sum(timedelta)) as seconds, count(timedelta)"
            " as sessions, player from progress_playertracker_v2 group by player")
        db["minecraft"].close()
        total_seconds = 0
        total_sessions = 0
        for p in players:
            total_seconds = total_seconds + int(p['seconds'])
            total_sessions = total_sessions + p['sessions']
        days, remainder = divmod(total_seconds, 86400)
        hours, remainder = divmod(remainder, 3600)
        return ("These fucking nerds have played %s days, %s hours worth of meincraft over %s sessions" % (
            days, hours, total_sessions))

    @staticmethod
    def playtime_single(player):
        time = db["minecraft"].do_query(
            "select sum(progress_playertracker_v2.timedelta) as seconds, "
            "count(progress_playertracker_v2.timedelta) as sessions "
            "from progress.progress_playertracker_v2 where player in "
            "(select player_name from progress.minecraft_players "
            "where player_guid = (select player_guid as guid from progress.minecraft_players where player_name = %s))",
            (player,))
        db["minecraft"].close()
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

    def howchies_profile(self, message):
        result = db["minecraft"].do_query(
            "SELECT player, count(*) as `count` FROM `progress_deaths` where match(message) against (%s)"
            "GROUP BY player ORDER by count DESC",
            (message,))
        db["minecraft"].close()
        if result:
            return self.sort(result, 'player', 'count')
        else:
            return 'No deaths recorded'

    def ouchies_profile(self, player):
        result = db["minecraft"].do_query(
            "SELECT message,count(*) as `count` FROM `progress_deaths` WHERE player=%s"
            " GROUP BY message ORDER BY count DESC",
            (player,))
        db["minecraft"].close()
        if result:
            return self.sort(result, 'message', 'count')
        else:
            return 'No deaths recorded'

    @command()
    @commands.cooldown(1, 10, BucketType.guild)
    async def howchies(self, ctx: Context, *args):
        """here's whats killing you"""
        log.debug("HOWCHIES - triggered")
        if args:
            r = self.howchies_profile(args)
            log.debug("HOWCHIES - search mode - returned: 'people who died to %s: %s" % (args, r))
            async with ctx.typing():
                await asyncio.sleep(3)
            await ctx.send("People who died to %s: %s" % (args, r))
        else:
            r = self.top_10_death_reasons()
            log.debug("HOWCHIES - top 10 - returned: %s" % r)
            async with ctx.typing():
                await asyncio.sleep(3)
            await ctx.send("Heres whats killing you: %s" % r)

    def top_10_death_reasons(self):
        result = db["minecraft"].do_query(
            "SELECT message, count(*) as `count` FROM `progress_deaths` "
            "GROUP BY message ORDER BY count DESC LIMIT 10",
            '')
        db["minecraft"].close()
        if result:
            return self.sort(result, 'message', 'count')
        else:
            pass

    @command()
    @commands.cooldown(1, 10, BucketType.guild)
    async def ouchies(self, ctx: Context, *args):
        """reflect upon the dead"""
        log.debug("ouchies ")
        try:
            if args[0]:
                r = self.ouchies_profile(args[0])
                log.debug("OUCHIES - player search - searched %s, returned: %s" % (args[0], r))
                async with ctx.typing():
                    await asyncio.sleep(3)
                await ctx.send("Deaths for %s: %s" % (args[0], r))
                return
        except IndexError:
            # no args, lets do top 10
            r = self.top_10_deaths()
            log.debug("OUCHIES - top 10 - returned: %s" % r)
            async with ctx.typing():
                await asyncio.sleep(3)
            await ctx.send('Top 10 ouchies: %s' % r)

    @command()
    @commands.cooldown(1, 10, BucketType.guild)
    async def alias(self, ctx: Context, *args):
        """sneaky playerses"""
        names = self.player_alias(args[0])
        log.debug("ALIAS - searching player")
        if len(names) == 0:
            async with ctx.typing():
                await asyncio.sleep(3)
            await ctx.send("I dont think i've ever seen that butt")
        elif len(names) == 1:
            async with ctx.typing():
                await asyncio.sleep(3)
            await ctx.send("I've only seen this jerk as %s" % names[0])
        else:
            async with ctx.typing():
                await asyncio.sleep(3)
            await ctx.send("I've seen this jerk play as %s" % ", ".join(names))

    def top_10_deaths(self):
        result = db["minecraft"].do_query(
            "SELECT player, count(*) as `count` FROM `progress_deaths` GROUP BY player ORDER BY count DESC LIMIT 10",
            '')
        db["minecraft"].close()
        if result:
            return self.sort(result, 'player', 'count')
        else:
            pass

    def deathsperhour_list(self):
        dph = db["minecraft"].do_query(
            "select T.player, COALESCE(D.deaths, 0) / (sum(T.timedelta) / 60 / 60) as deaths_per_hour"
            "FROM progress.progress_playertracker_v2 as T left join(SELECT count(D.player) as deaths, "
            "D.player from progress.progress_deaths D GROUP BY D.player) D ON T.player = D.player group by"
            "T.player ORDER BY deaths_per_hour DESC LIMIT 10"
        )
        if dph:
            return self.sort(dph, 'player', 'deaths_per_hour')

    @command()
    @commands.cooldown(1, 10, BucketType.guild)
    async def deathsperhour(self, ctx: Context, *args):
        dph = db["minecraft"].do_query(
            "select T.player, COALESCE(D.deaths, 0) / format((sum(T.timedelta)/60/60),1) as deaths_per_hour FROM "
            "progress.progress_playertracker_v2 as T left join (SELECT count(D.player) as deaths, D.player"
            " from progress.progress_deaths D where player=%s GROUP BY D.player) D"
            " ON T.player = D.player where T.player=%s group by T.player", (args[0], args[0]))
        db["minecraft"].close()
        try:
            if dph[0]['deaths_per_hour'] > 0:
                # good return
                if dph[0]['deaths_per_hour'] > 5:
                    insults = [
                        "my hero",
                        "a true gaming legend"
                    ]
                    insult = insults[random.randrange(0, len(insults) - 1)]

                else:
                    insult = "you should try harder"
                log.debug("DEATHSPERHOUR - deaths per hour for %s is %s. %s" %
                          (args[0],
                           str(dph[0]['deaths_per_hour']),
                           insult))
                async with ctx.typing():
                    await asyncio.sleep(3)
                await ctx.send("deaths per hour for %s is %s. %s" %
                               (args[0],
                                str(dph[0]['deaths_per_hour']),
                                insult))
            else:
                comments = [
                    "%s is the most boring person on the server",
                    "actually, %s is just a gaming god",
                    "persistence is key for %s",
                    "%s is a god among mortals"
                ]
                r = comments[random.randrange(0, len(comments)) - 1] % args[0]
                log.debug("DEATHSPERHOUR - %s" % r)
                async with ctx.typing():
                    await asyncio.sleep(3)
                await ctx.send(r)
        except IndexError:
            async with ctx.typing():
                await asyncio.sleep(3)
            await ctx.send("%s doesnt play" % args[0])

    @staticmethod
    def player_alias(player):
        db["minecraft"].build()
        r = db["minecraft"].do_query("select player_name from minecraft_players where player_guid ="
                                     " (select player_guid as guid from minecraft_players where player_name = %s)",
                                     (player,))
        names = []
        for re in r:
            names.append(re['player_name'])
        return names

    @staticmethod
    def sort(target, t1, t2, t3=""):
        cmsg = ''
        i = 1
        for d in target:
            if i != 1:
                cmsg = cmsg + ', '
            cmsg = cmsg + d[t1] + "(%s%s)" % (str(d[t2]), t3)
            i = i + 1
        return cmsg
