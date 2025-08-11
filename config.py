import os

# discord api key
secretkey = os.environ['buttbot_discordapikey']

# test env flag. changes certain processing commands to always run.
# default: False
test_environment = os.environ['buttbot_test_environment']

# discord chat command prefix.
# default: &
command_prefix = os.environ['buttbot_command_prefix']

# mysql username & password
db_secrets = [os.environ['buttbot_db_username'], os.environ['buttbot_db_password']]

# mysql server URI
db_server = os.environ['buttbot_db_server']

# databases for buttbot and minecraft add-on.  The minecraft addon has been spun off to another bot but I havent verified
# that this variable is no longer needed here.
discordbot_db = os.environ['buttbot_discordbot_db']
minecraft_db = os.environ['buttbot_minecraft_db']
stat_db = os.environ['buttbot_stat_db']

# default timer for buttbot's buttings.  can be set per guild.
# suggested: 300 (seconds)
timer = os.environ['buttbot_timer']

# global ignore list for bots that also replay text
global_ignore_list = os.environ['buttbot_global_ignore_list']
