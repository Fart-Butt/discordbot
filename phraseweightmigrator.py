import json
from butt_database import Db
from config import *

try:
    with open('phrase_weight_list.txt') as f:
        phrases = json.load(f)
except IOError:
    pass
db_ = "discordbot_test"
db = Db(db_, db_secrets[0], db_secrets[1])

db_data = []
for word, weight in phrases.items():
    if weight != 1000:
        db_data.append((word, "XX NN", weight))

print(db_data)
db.do_insertmany("INSERT INTO `phraseweights` (`phrase`, `POS`, `weight`) "
                 "VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE phrase=phrase;",
                 db_data)
