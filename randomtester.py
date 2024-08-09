from random import *


def __pick_random_phrase_by_weight(summed_weights, word_list):
    total_sum_of_weights = summed_weights
    try:
        randomweight = randrange(1, total_sum_of_weights)
        for i in word_list:
            randomweight = randomweight - i[1]
            if randomweight <= 0:
                return i[0]
    except ValueError:
        # no words to pick
        return None


gorilla = 0
primal = 0
list_of_picks = {"gorilla": 0, "primal": 0, "otherword": 0, "thisword": 0}
word_list = (("gorilla", 1000), ("primal", 1000), ("otherword", 1000), ("thisword", 2000))
for i in range(5000):
    a = __pick_random_phrase_by_weight(5000, word_list)
    list_of_picks[a] += 1

for a, b in list_of_picks.items():
    print("%s: %d" % (a, b))
