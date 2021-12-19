from __future__ import absolute_import, division, print_function
from math import sqrt, log
from game import Game, WHITE, BLACK, EMPTY
import copy
import time
import random


class Node:
    # NOTE: modifying this block is not recommended
    def __init__(self, state, actions, parent=None):
        self.state = (state[0], copy.deepcopy(state[1]))
        self.num_wins = 0  # number of wins at the node
        self.num_visits = 0  # number of visits of the node
        self.parent = parent  # parent node of the current node
        self.children = []  # store actions and children nodes in the tree as (action, node) tuples
        self.untried_actions = copy.deepcopy(actions)  # store actions that have not been tried


# NOTE: deterministic_test() requires BUDGET = 1000
#   You can try higher or lower values to see how the AI's strength changes
BUDGET = 1000


class AI:
    # NOTE: modifying this block is not recommended
    def __init__(self, state):
        self.simulator = Game()
        self.simulator.reset(*state)  # using * to unpack the state tuple
        self.root = Node(state, self.simulator.get_actions())

    def mcts_search(self):
        # TODO: Main MCTS loop

        iters = 0
        action_win_rates = {}  # store the table of actions and their ucb values

        # TODO: Implement the MCTS Loop
        while iters < BUDGET:
            if (iters + 1) % 100 == 0:
                # NOTE: if your terminal driver doesn't support carriage returns
                #   you can use: print("{}/{}".format(iters + 1, BUDGET))
                print("\riters/budget: {}/{}".format(iters + 1, BUDGET), end="")

            # TODO: select a node, rollout, and backpropagate
            node = self.select(self.root)
            result = self.rollout(node)
            self.backpropagate(node, result)
            iters += 1
        print()

        # Note: Return the best action, and the table of actions and their win values 
        #   For that we simply need to use best_child and set c=0 as return values
        _, action, action_win_rates = self.best_child(self.root, 0)
        return action, action_win_rates

    def select(self, node):
        # TODO: select a child node

        # NOTE: deterministic_test() requires using c=1 for best_child()
        #
        self.simulator.reset(*node.state)
        while not self.simulator.game_over:
            if len(node.untried_actions) != 0:
                return self.expand(node)
            else:
                Cp = 1 / sqrt(2)  # from the paper
                Cp = 1  # for deterministic test()
                node = self.best_child(node, Cp)[0]
                self.simulator.reset(*node.state)
        return node

    def expand(self, node):
        # TODO: add a new child node from an untried action and return this new node
        # IMPORTANT: use the following method to fetch the next untried action
        #   so that the order of action expansion is consistent with the test cases
        action = node.untried_actions.pop(0)
        self.simulator.place(action[0], action[1])
        child_node = Node(self.simulator.state(), self.simulator.get_actions(), node)
        node.children.append((child_node, action))

        # NOTE: Make sure to add the new node to the node.children
        # NOTE: You may find the following methods useful:
        #   self.simulator.state()
        #   self.simulator.get_actions()

        return child_node

    def best_child(self, node, c):
        # TODO: determine the best child and action by applying the UCB formula

        best_child_node = None  # store the best child node with UCB
        best_action = None  # store the action that leads to the best child
        action_ucb_table = {}  # store the UCB values of each child node (for testing)

        for child_info in node.children:
            curr_child = child_info[0]
            curr_action = child_info[1]
            action_ucb_table[curr_action] = curr_child.num_wins / curr_child.num_visits + c * sqrt(
                    2 * log(node.num_visits) / curr_child.num_visits)
            if best_child_node is None or action_ucb_table[best_action] < action_ucb_table[curr_action]:
                best_child_node = curr_child
                best_action = curr_action

        return best_child_node, best_action, action_ucb_table

    def backpropagate(self, node, result):
        while node is not None:
            # TODO: backpropagate the information about winner
            # IMPORTANT: each node should store the number of wins for the player of its **parent** node
            node.num_visits += 1
            if node.parent:
                node.num_wins += result[node.parent.state[0]]
            node = node.parent

    def rollout(self, node):
        # TODO: rollout (called DefaultPolicy in the slides)

        # NOTE: you may find the following methods useful:
        #   self.simulator.reset(*node.state)
        #   self.simulator.game_over
        #   self.simulator.rand_move()
        #   self.simulator.place(r, c)

        self.simulator.reset(*node.state)
        while not self.simulator.game_over:
            action = self.simulator.rand_move()
            self.simulator.place(action[0], action[1])

        # Determine reward indicator from result of rollout
        reward = {}
        if self.simulator.winner == BLACK:
            reward[BLACK] = 1
            reward[WHITE] = 0
        elif self.simulator.winner == WHITE:
            reward[BLACK] = 0
            reward[WHITE] = 1
        return reward
