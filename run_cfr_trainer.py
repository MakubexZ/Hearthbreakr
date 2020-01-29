import json
import itertools
from hearthbreaker.agents.basic_agents import RandomAgent
from hearthbreaker.cards.heroes import hero_for_class
from hearthbreaker.constants import CHARACTER_CLASS
from hearthbreaker.engine import Game, Deck, card_lookup
from hearthbreaker.cards import *
from hearthbreaker.agents import build_tree
from hearthbreaker.agents.cfr_algorithms import ChanceSamplingCFR, VanillaCFR
import matplotlib.pyplot as plt
import sys
import pickle
sys.setrecursionlimit(1000000)


def load_deck(filename):
    cards = []
    character_class = CHARACTER_CLASS.MAGE

    with open(filename, "r") as deck_file:
        contents = deck_file.read()
        items = contents.splitlines()
        for line in items[0:]:
            parts = line.split(" ", 1)
            count = int(parts[0])
            for i in range(0, count):
                card = card_lookup(parts[1])
                if card.character_class != CHARACTER_CLASS.ALL:
                    character_class = card.character_class
                cards.append(card)

    if len(cards) > 30:
        pass
    print('character_class', character_class)
    print('character_hp', hero_for_class(character_class).health)
    return Deck(cards, hero_for_class(character_class))


def play_game(game):
    try:
        game.start()
    except Exception as e:
        print(json.dumps(game.__to_json__(), default=lambda o: o.__to_json__(), indent=1))
        print(game._all_cards_played)
        raise e


def bulid_starting_hands(deck_1, deck_2):
    starting_hands1 = list(itertools.combinations(deck_1.cards, 2))
    starting_hands2 = list(itertools.combinations(deck_2.cards, 2))

deck1 = load_deck("patron.hsdeck")
deck2 = load_deck("zoo.hsdeck")

'''
for i in range(len(deck1.cards)):
    print(type(deck1.cards[i].name))
    print(deck1.cards[i].name)
'''

game1 = Game([deck1, deck2], [RandomAgent(), RandomAgent()])

root = build_tree.RootChanceGameState(game1)

print('tree built')


X1 = []
Y1 = []
X2 = []
Y2 = []

chance_sampling_cfr = ChanceSamplingCFR(root)
for i in range(100):
    X1.append(i*10)
    chance_sampling_cfr.run(iterations = 10)
    chance_sampling_cfr.compute_nash_equilibrium()
    #if i == 99:
        #print(len(chance_sampling_cfr.nash_equilibrium))
        #for key, value in chance_sampling_cfr.nash_equilibrium.items():
            #print(value)
    # print('already compute nash')
    if i % 5 == 0:
        print("processing", i, "/100")
    value1 = chance_sampling_cfr.value_of_the_game()
    Y1.append(value1)
    
nash1 = chance_sampling_cfr.nash_equilibrium
file3 = open('pickle_nash1.pickle', 'wb')
pickle.dump(nash1, file3)
file3.close()


data1 = [X1,Y1]
file1 = open('pickle_chance.pickle', 'wb')
pickle.dump(data1, file1)
file1.close()



print('Vanilla')
game2 = Game([deck1, deck2], [RandomAgent(), RandomAgent()])
root = build_tree.RootChanceGameState(game2)
vanilla_cfr = VanillaCFR(root)
for j in range(100):
    if j % 5 == 0:
        print("processing", j, "/100")
    X2.append(j * 10)
    vanilla_cfr.run(iterations = 5)
    vanilla_cfr.compute_nash_equilibrium()
    value2 = vanilla_cfr.value_of_the_game()
    Y2.append(value2)
print('compute')

nash2 = vanilla_cfr.nash_equilibrium
file4 = open('pickle_nash2.pickle', 'wb')
pickle.dump(nash2, file4)
file4.close()

data2 = [X2,Y2]
file2 = open('pickle_vanilla.pickle', 'wb')
pickle.dump(data2, file2)
file2.close()

'''
plt.figure()
plt.plot(X1, Y1, label = 'Chance_sampling')
plt.plot(X2, Y2, color = 'red', label = 'Vanilla')
plt.xlabel('Iterations')
plt.ylabel('Value of Player1')
plt.legend(loc='upper right')
plt.show()
'''

