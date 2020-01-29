import random
import copy
import itertools
from hearthbreaker import engine

CHANCE = 'CHANCE'
A = 1


class GameStateBase:

    def __init__(self, parent, to_move,  game, n):
        self.parent = parent
        self.to_move = to_move
        self.game = game
        self.n = n

    def play(self, action):
        return self.children[action]

    def is_chance(self):
        return self.to_move == CHANCE

    def inf_set(self):
        raise NotImplementedError("Please implement information_set method")


class RootChanceGameState(GameStateBase):
    def __init__(self, game):
        super().__init__(parent=None, to_move=CHANCE, game=game, n=0)
        self.actions = self.get_starting_hands()
        self.game.current_player = self.game.players[1]

        game_curr = self.game.copy()
        print(self.actions)

        self.children = {
            hands: PlayerMoveGameState(
                self, A, self.pre_game(game_curr, hands), hands, [], self.n+1
            ) for hands in self.actions
        }
        # print(self.children)

        self._chance_prob = 1. / len(self.children)

    def pre_game(self, game, hands):
        game.__pre_game_run = True
        game.players[0].hand = hands[0]
        for card in game.players[0].hand:
            card.attach(card, game.players[0])
            card.drawn = True
            game.players[0].deck.left -= 1
            game.players[0].trigger("card_drawn", card)
            card.trigger("drawn")

        game.players[1].hand = hands[1]
        for card in game.players[1].hand:
            card.attach(card, game.players[1])
            card.drawn = True
            game.players[1].deck.left -= 1
            game.players[1].trigger("card_drawn", card)
            card.trigger("drawn")
        return game


    def get_starting_hands(self):
        starting_hands1 = tuple(itertools.combinations(self.game.players[0].deck.cards, 3))
        starting_hands2 = tuple(itertools.combinations(self.game.players[1].deck.cards, 3))

        startinghands1 = []
        startinghands2 = []
        for i in range(len(starting_hands1)):
            startinghands1.append(starting_hands1[i])
        for i in range(len(starting_hands2)):
            startinghands2.append(starting_hands2[i])

        for i in range(len(startinghands2)):
            coin = engine.card_lookup("The Coin")
            coin.player = self.game.players[1]
            t = list(startinghands2[i])
            t.append(coin)
            startinghands2[i] = tuple(t)

        starting_hands = []
        for i in range(len(startinghands1)):
            for j in range(len(startinghands2)):
                starting_hands.append((startinghands1[i], startinghands2[j]))
        return starting_hands

    def is_terminal(self):
        return False

    def inf_set(self):
        return "."

    def chance_prob(self):
        return self._chance_prob

    def sample_one(self):
        return random.choice(list(self.children.values()))


class PlayerMoveGameState(GameStateBase):

    def __init__(self, parent, to_move, game, starting_hands, actions_history, n):
        super().__init__(parent=parent, to_move=to_move, game=game, n=n)

        if not game.game_ended and self.n != 6:
            self.starting_hands = starting_hands
            self.actions_history = actions_history
            self.acseq_state = {}

            self.start_turn()
            action_sequence = []
            self.get_action_sequence(self.game, action_sequence)
            self.actions = self.acseq_state
        else:
            self.actions = {}
            self.starting_hands = starting_hands
            self.actions_history = actions_history

        self.children = {
            key: PlayerMoveGameState(
                self,
                -to_move,
                value,
                self.starting_hands,
                self.actions_history + [key],
                self.n+1
            ) for key, value in self.actions.items()
        }

        private_card = ""
        for i in range(len(self.starting_hands[0])):
            private_card += self.starting_hands[0][i].name if self.to_move == A else self.starting_hands[1][i].name
        self._information_set = ".{0}.{1}".format(private_card, ".".join(self.actions_history))
        # print(self._information_set)

    def start_turn(self):
        if not self.game._has_turn_ended:
            self.game._end_turn()
        if self.game.current_player == self.game.players[0]:
            self.game.current_player = self.game.players[1]
            self.game.other_player = self.game.players[0]
        else:
            self.game.current_player = self.game.players[0]
            self.game.ther_player = self.game.players[1]
            self.game._turns_passed += 1
        if self.game._turns_passed >= 10:
            self.game.players[0].hero.dead = True
            self.game.players[1].hero.dead = True
            self.game.game_over()
        if self.game.current_player.max_mana < 10:
            self.game.current_player.max_mana += 1

        for secret in self.game.other_player.secrets:
            secret.activate(self.game.other_player)
        for minion in self.game.current_player.minions:
            minion.attacks_performed = 0
        self.game.current_player.mana = self.game.current_player.max_mana - self.game.current_player.upcoming_overload
        self.game.current_player.current_overload = self.game.current_player.upcoming_overload
        self.game.current_player.upcoming_overload = 0
        self.game.current_player.cards_played = 0
        self.game.current_player.dead_this_turn = []
        self.game.current_player.hero.power.used = False
        self.game.current_player.hero.attacks_performed = 0
        self.game.current_player.trigger("turn_started", self.game.current_player)
        self.game._has_turn_ended = False

    def get_action_sequence(self, game, action_sequence):
        game_temp = game.copy()
        action_sequence_temp = copy.deepcopy(action_sequence)

        attack_minions = [minion for minion in filter(lambda minion: minion.can_attack(), game_temp.current_player.minions)]
        # if len(attack_minions) > 0:
           # print('attack minions', attack_minions[0].card.name)
        if game_temp.current_player.hero.can_attack():
            attack_minions.append(game_temp.current_player.hero)
        playable_cards = [card for card in
                          filter(lambda card: card.can_use(game_temp.current_player, game_temp.current_player.game),
                                 game_temp.current_player.hand)]
        # print('current hand', game_temp.current_player.hand)
        # print('playable card', playable_cards)
        possible_actions = len(attack_minions) + len(playable_cards) + 1
        # print(attack_minions, playable_cards, possible_actions)

        for ac in range(possible_actions):

            # print('possible action ', possible_actions)
            # print('now action is ', ac)

            if ac == possible_actions - 1:
                game_curr = game_temp.copy()
                action_sequence_curr = copy.deepcopy(action_sequence_temp)
                game_curr._end_turn()
                if game_curr.players[0].hero.health == 0 or game_curr.players[1].hero.health == 0:
                    game_curr.game_over()
                action = ".PASS"
                if len(action_sequence_curr) == 0:
                    action_sequence_curr.append(action)
                else:
                    action_sequence_curr[0] += action

                self.acseq_state[action_sequence_curr[0]] = game_curr
                # print('reach a final node', self.acseq_state)
                # input()

            elif ac < len(attack_minions):
                game_curr = game_temp.copy()
                action_sequence_curr = copy.deepcopy(action_sequence_temp)
                attack_minions1 = [minion for minion in
                                  filter(lambda minion: minion.can_attack(), game_curr.current_player.minions)]
                attack_minions1[ac].attack()
                action = "MINION_ATTACK" + str(ac)
                if len(action_sequence_curr) == 0:
                    action_sequence_curr.append(action)
                else:
                    action_sequence_curr[0] += action
                self.get_action_sequence(game_curr, action_sequence_curr)
                del game_curr
            else:
                # print('playable', playable_cards)
                cardindex = str(game_temp.current_player.hand.index(playable_cards[ac - len(attack_minions)]))
                game_curr = game_temp.copy()
                action_sequence_curr = copy.deepcopy(action_sequence_temp)
                game_curr.current_player.game.play_card(game_curr.current_player.hand[int(cardindex)])
                action = ".PLAY_CARD_" + playable_cards[ac - len(attack_minions)].name + cardindex
                if len(action_sequence_curr) == 0:
                    action_sequence_curr.append(action)
                else:
                    action_sequence_curr[0] += action
                self.get_action_sequence(game_curr, action_sequence_curr)
                del game_curr

    def inf_set(self):
        return self._information_set

    def is_terminal(self):
        if self.game.players[0].hero.health == 0 or self.game.players[1].hero.health == 0:
            return True
        return  False

    def evaluation(self):
        if self.is_terminal() is False:
            return -1
            # raise RuntimeError("trying to evaluate non-terminal node")
        # print("wowowowowwowowowowwo")
        if self.to_move == A:
            return 2
        else:
            return -2
