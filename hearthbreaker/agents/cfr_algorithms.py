from hearthbreaker.agents.cfr_utils import init_sigma, init_empty_node_maps
import pickle

A = 1

class CounterfactualRegretMinimizationBase:

    def __init__(self, root, chance_sampling = False):
        self.root = root
        self.sigma = init_sigma(root)
        self.cumulative_regrets = init_empty_node_maps(root)
        self.cumulative_sigma = init_empty_node_maps(root)
        self.nash_equilibrium = init_empty_node_maps(root)
        self.chance_sampling = chance_sampling
        print('finished initialization')

    def _update_sigma(self, i):
        rgrt_sum = sum(filter(lambda x : x > 0, self.cumulative_regrets[i].values()))
        # print('regret_sum', rgrt_sum)
        for a in self.cumulative_regrets[i]:
            # print('i', i)
            # print('a', a)
            self.sigma[i][a] = max(self.cumulative_regrets[i][a], 0.) / rgrt_sum if rgrt_sum > 0 else 1. / len(self.cumulative_regrets[i].keys())
            # print('sigma[i][a]', self.sigma[i][a])

    def compute_nash_equilibrium(self):
        self.__compute_ne_rec(self.root)
        # print('nash_equilibrium', self.nash_equilibrium)
        dat = self.nash_equilibrium
        file = open('pickle_nash.pickle', 'wb')
        pickle.dump(dat, file)
        file.close()

    def __compute_ne_rec(self, node):
        if node.is_terminal():
            return
        i = node.inf_set()
        # print(i)
        if node.is_chance():
            # print('is chance node', node.actions)
            self.nash_equilibrium[i] = {a: node.chance_prob() for a in list(node.actions)}
            # print(i, self.nash_equilibrium[i])
        else:
            sigma_sum = sum(self.cumulative_sigma[i].values())
            if sigma_sum != 0:
                self.nash_equilibrium[i] = {a: self.cumulative_sigma[i][a] / sigma_sum for a in node.actions}
            # print('2222222', self.nash_equilibrium[i])
        for k in node.children:
            self.__compute_ne_rec(node.children[k])

    def _cumulate_cfr_regret(self, information_set, action, regret):
        self.cumulative_regrets[information_set][action] += regret
        # print('cumulate_cfr_regret', self.cumulative_regrets[information_set][action])

    def _cumulate_sigma(self, information_set, action, prob):
        self.cumulative_sigma[information_set][action] += prob
        # print('inf_set', information_set)
        # print('cumulate_sigma', self.cumulative_sigma[information_set][action])

    def run(self, iterations):
        raise NotImplementedError("Please implement run method")

    def value_of_the_game(self):
        # print(self.__value_of_the_game_state_recursive(self.root))
        return self.__value_of_the_game_state_recursive(self.root)

    def _cfr_utility_recursive(self, state, reach_a, reach_b):
        '''
        if not state.is_chance():
            for m in range(state.n):
                print('----'*m, end="")
            print('action_his', state.actions_history)
        for m in range(state.n):
            print('----' * m, end="")
        print('level', state.n)
        for m in range(state.n):
            print('----' * m, end="")
        print('actions', state.actions)
        '''

        # print('inf_set', state._information_set)
        children_states_utilities = {}
        # if state.parent is not None:
        #    print(state.actions_history)
        if state.is_terminal():
            # print("oiuioiuioioiuioiuio")
            return state.evaluation()
        if state.parent is None:
            '''
            for m in range(state.n):
                print('-'*m, end="")
            print('is chance node')
            '''

            if self.chance_sampling:

                if len(list(state.children.values())) == 0:
                    # print('2323', state.battle_fields)
                    # print(state.actions_history)
                    return state.evaluation()

                # print('123')
                return self._cfr_utility_recursive(state.sample_one(), reach_a, reach_b)
            else:
                chance_outcomes = {state.play(action) for action in state.actions}
                # print('chance_node_action', chance_outcomes)
                return state.chance_prob() * sum([self._cfr_utility_recursive(outcome, reach_a, reach_b) for outcome in chance_outcomes])

        value = 0.
        for action in state.actions:
            '''

            for m in range(state.n):
                print('----'*m, end="")
            print('action', action)
            for m in range(state.n):
                print('----'*m, end="")
            print('state.to_move', state.to_move)
            '''

            # print(state.inf_set())
            child_reach_a = reach_a * (self.sigma[state.inf_set()][action] if state.to_move == A else 1)
            # print(child_reach_a)
            '''

            for m in range(state.n):
                print('----'*m, end="")
            print('child_reach_a', child_reach_a)
            '''


            child_reach_b = reach_b * (self.sigma[state.inf_set()][action] if state.to_move == -A else 1)
            '''

            for m in range(state.n):
                print('----'*m, end="")
            print('child_reach_b', child_reach_b)
            '''


            child_state_utility = self._cfr_utility_recursive(state.play(action), child_reach_a, child_reach_b)
            # print(child_state_utility)

            '''
            for m in range(state.n):
                print('----'*m, end="")
            print('child_state_utility', child_state_utility)
            
            for m in range(state.n):
                print('----'*m, end="")
            print('return to level', state.n)
            for m in range(state.n):
                print('----'*m, end="")
            print('action for now is', action)
            for m in range(state.n):
                print('----'*m, end="")
            print('child_reach_a', child_reach_a, 'child_reach_b', child_reach_b)

            for m in range(state.n):
                print('----'*m, end="")
            print('sigma for this action', self.sigma[state.inf_set()][action])

            print("inf", state.inf_set())
            '''

            if action == 'NULL':
                value += 0
            else:
                value += self.sigma[state.inf_set()][action] * child_state_utility
                # print(self.sigma[state.inf_set()][action])
                # print('value', value)
                '''

            for m in range(state.n):
                print('----'*m, end="")
            print('value of this node', value)
            '''



            children_states_utilities[action] = child_state_utility
            '''

            for m in range(state.n):
                print('----'*m, end="")
            print('children_states_utilities', children_states_utilities)
            '''


        (cfr_reach, reach) = (reach_b, reach_a) if state.to_move == A else (reach_a, reach_b)
        '''

        for m in range(state.n):
            print('----' * m, end="")
        print('level', state.n)
        '''

        for action in state.actions:
            '''

            for m in range(state.n):
                print('----'*m, end="")
            print('action', action)
            '''

            # print(state.to_move)
            # print(cfr_reach)
            # print(children_states_utilities[action])
            action_cfr_regret = state.to_move * cfr_reach * (children_states_utilities[action] - value)

            '''

            for m in range(state.n):
                print('----'*m, end="")
            print('action_cfr_regret', action_cfr_regret)
            '''

            self._cumulate_cfr_regret(state.inf_set(), action, action_cfr_regret)
            '''

            for m in range(state.n):
                print('----'*m, end="")
            print('sigma[state.inf_set()][action]', self.sigma[state.inf_set()][action])
            '''

            self._cumulate_sigma(state.inf_set(), action, reach * self.sigma[state.inf_set()][action])

        if self.chance_sampling:
            self._update_sigma(state.inf_set())
        # print(value)
        return value

    def __value_of_the_game_state_recursive(self, node):
        value = 0.
        # print('node nash are\n', self.nash_equilibrium[node.inf_set()])
        if node.is_terminal():
            return node.evaluation()
        # print('node actions', node.actions)
        # print(node.is_chance())

        for action in node.actions:
            # print(action)
            value += self.nash_equilibrium[node.inf_set()][action] * self.__value_of_the_game_state_recursive(
                    node.play(action))
        ''''
        if node.is_chance():
            print('value of player 1 for this chance node is ', value)
        '''
        return value


class VanillaCFR(CounterfactualRegretMinimizationBase):

    def __init__(self, root):
        super().__init__(root = root, chance_sampling = False)

    def run(self, iterations = 1):
        for _ in range(0, iterations):
            # print('iterations', _)
            self._cfr_utility_recursive(self.root, 1, 1)
            self.__update_sigma_recursively(self.root)

    def __update_sigma_recursively(self, node):
        if node.is_terminal():
            return
        if not node.is_chance():
            self._update_sigma(node.inf_set())
        for k in node.children:
            self.__update_sigma_recursively(node.children[k])


class ChanceSamplingCFR(CounterfactualRegretMinimizationBase):

    def __init__(self, root):
        super().__init__(root = root, chance_sampling = True)

    def run(self, iterations = 1):
        for _ in range(0, iterations):
            # print('now iteration is', _)
            self._cfr_utility_recursive(self.root, 1, 1)

