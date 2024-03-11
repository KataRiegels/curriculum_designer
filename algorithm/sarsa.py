import random
import numpy as np
import copy
from policy import Policy

class SarsaAgent:
    def __init__(self, max_training_episodes, max_steps, state_space_size, action_space_size, learning_rate,
                 discount_factor, exploration_rate, previous_q_values=None):
        if previous_q_values == None:
            self.q_values = {}
        else:
            self.q_values = previous_q_values
        self.max_training_episodes = max_training_episodes
        self.max_steps = max_steps
        self.state_space_size = state_space_size
        self.action_space_size = action_space_size
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.exploration_rate = exploration_rate
        self.use_optimal = False
        self.optimal_policy = {}
        # self.policy = {}


    def get_q_value(self, state, action):
        # Retrieve Q-value from the Q-table
        key = (state, action)
        q_value = self.q_values.get(key, None)
        return q_value if q_value is not None else 0.0


    def calculate_and_update_q_value(self, state, action, next_state, next_action, reward):
        """Calculates q_value based on SARSA rule, and updates q_value accordingly"""
        old_q_value = self.get_q_value(state, action)
        target_q_value = reward + self.discount_factor * (self.get_q_value(next_state, next_action))
        new_q_value = old_q_value + self.learning_rate * (target_q_value - old_q_value)
        self.q_values[(state, action)] = new_q_value

    def get_v_value(self, state):
        """Calculates and returns the value of a state (V(s)) based on the maximum Q-value."""
        q_values = [self.get_q_value(state, a) for a in range(self.action_space_size)]
        max_q_value = max(q_values)
        return max_q_value
    
    def choose_action(self, state):
        # Epsilon-greedy policy for action selection
        
        if self.use_optimal: return self.choose_policy_action(state)
        
        if random.uniform(0, 1) < self.exploration_rate:
            action = random.choice(range(self.action_space_size))
            return action

        else:
            # Choose the action with the highest Q-value
            q_values = [self.get_q_value(state, a) for a in range(self.action_space_size)]
            max_q_value = max(q_values)
            max_q_indices = [i for i, q in enumerate(q_values) if q == max_q_value]

            # Randomly choose one of the actions with the maximum Q-value
            chosen_action = random.choice(max_q_indices)

            self.exploration_rate -= 0.0000001
            return chosen_action
        # print(self.exploration_rate)
    def get_unique_states(self):
        unique_states = set()

        for (state, _), _ in self.q_values.items():
            unique_states.add(state)

        return list(unique_states)       
        
    def get_q_values_for_state(self, state):
        # Retrieve all Q-values for a specific state
        q_values_for_state = {action: self.get_q_value(state, action) for action in range(self.action_space_size)}
        return q_values_for_state

    @property
    def policy(self):
        return self.get_optimal_policy()

    def get_optimal_policy(self):
        policy = Policy(self.q_values)
        return policy

    def q_values_from_policy(self, policy):
        q_values = {}
        if self.use_optimal:
            for state, optimal_action in policy.items():
                for action in range(self.action_space_size):
                    q_value = 1.0 if action == optimal_action else 0.0  # Set Q-value to 1 for optimal action, 0 otherwise
                    # return q_value
                    q_values[(state, action)] = q_value
        return q_values

    def set_q_values_from_policy(self, optimal_policy):
        self.q_values = {}
        self.q_values = self.q_values_from_policy(optimal_policy)
                    
    def choose_policy_action(self, state):
        q_values = [self.get_q_value(state, a) for a in range(self.action_space_size)]
        max_q_value = max(q_values)
        max_q_indices = [i for i, q in enumerate(q_values) if q == max_q_value]
        chosen_action = random.choice(max_q_indices)

        return chosen_action
    
    
    def copy(self):
        return copy.deepcopy(self)
