import random
import numpy as np
import copy
from policy import Policy
from samples import *

class QAgent:
    def __init__(self, max_training_episodes, max_steps, state_space_size, action_space_size, learning_rate,
                 discount_factor, exploration_rate, previous_q_values=None):
        if previous_q_values == None:
            self.q_values = {}
        else:
            self.q_values = previous_q_values
        self.max_training_episodes = max_training_episodes; self.max_steps = max_steps; self.state_space_size = state_space_size
        self.action_space_size = action_space_size; self.learning_rate = learning_rate; self.discount_factor = discount_factor
        self.exploration_rate = exploration_rate
        self.use_optimal = False
        self.optimal_policy = {}
        self.x = X()


    def get_q_value(self, state, action):
        # Retrieve Q-value from the Q-table
        key = (state, action)
        q_value = self.q_values.get(key, None)
        return q_value if q_value is not None else 0.0


    def calculate_and_update_q_value(self, state, action, next_state, next_action, reward):
        """Calculates q_value based on SARSA rule, and updates q_value accordingly"""
        pass

    def get_v_value(self, state):
        """Calculates and returns the value of a state (V(s)) based on the maximum Q-value."""
        q_values = [self.get_q_value(state, a) for a in range(self.action_space_size)]
        max_q_value = max(q_values)
        return max_q_value
    
    def choose_action(self, state, action_space = None):
        def get_keys_with_max_value(dictionary):
            if not dictionary:
                return []
            max_value = max(dictionary.values())
            return [key for key, value in dictionary.items() if value == max_value]
                # Epsilon-greedy policy for action selection
        
        if self.use_optimal: return self.choose_policy_action(state)
        
        if random.uniform(0, 1) < self.exploration_rate:
            # action = random.choice(range(self.action_space_size))
            action = random.choice(action_space)
            return action

        else:
            # Choose the action with the highest Q-value
            q_values = {a: self.get_q_value(state, a) for a in action_space}
            max_actions = get_keys_with_max_value(q_values)
            
            # q_values = [self.get_q_value(state, a) for a in range(self.action_space_size)]
            # max_q_value = max(q_values.values())
            # # q_values = {a: self.get_q_value(state, a) for a in action_space}
            
            
            
            # max_q_indices = [i for i, q in enumerate(q_values) if q == max_q_value]

            # Randomly choose one of the actions with the maximum Q-value
            chosen_action = random.choice(max_actions)

            self.exploration_rate -= 0.0000001
            return chosen_action
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
                    
    def choose_policy_action(self, state, action_space):
        def get_keys_with_max_value(dictionary):
            if not dictionary:
                return []
            max_value = max(dictionary.values())
            return [key for key, value in dictionary.items() if value == max_value]
                # Epsilon-greedy policy for action selection
        
        

            # Choose the action with the highest Q-value
        q_values = {a: self.get_q_value(state, a) for a in action_space}
        max_actions = get_keys_with_max_value(q_values)
        
        # q_values = [self.get_q_value(state, a) for a in range(self.action_space_size)]
        # max_q_value = max(q_values.values())
        # # q_values = {a: self.get_q_value(state, a) for a in action_space}
        
        
        
        # max_q_indices = [i for i, q in enumerate(q_values) if q == max_q_value]

        # Randomly choose one of the actions with the maximum Q-value
        chosen_action = random.choice(max_actions)

        self.exploration_rate -= 0.0000001
        return chosen_action
    
    @property
    def learned_values(self):
        return self.get_all_states_with_highest_q()
    
    def get_all_states_with_highest_q(self):
        """
        Get all states with their highest Q-values from the agent's Q-table.
        
        Returns:
        - states_with_highest_q: A dictionary where keys are states and values are the highest Q-value for each state.
        """

        # Initialize a dictionary to store the highest Q-values for each state
        states_with_highest_q = {}

        # Get all unique states
        states = self.get_unique_states()

        # Iterate through each state
        for state in states:
            # Retrieve all Q-values for the current state
            q_values_for_state = self.get_q_values_for_state(state)
            
            # Find the highest Q-value
            max_q_value = max(q_values_for_state.values())

            # Store the highest Q-value for the state
            states_with_highest_q[state] = max_q_value

        return states_with_highest_q
    
    def copy(self):
        return copy.deepcopy(self)


class SarsaAgent(QAgent):
    
    def calculate_and_update_q_value(self, state, action, next_state, next_action, reward, action_space = None):
        """Calculates q_value based on SARSA rule, and updates q_value accordingly"""
        old_q_value = self.get_q_value(state, action)
        target_q_value = reward + self.discount_factor * (self.get_q_value(next_state, next_action))
        new_q_value = old_q_value + self.learning_rate * (target_q_value - old_q_value)
        
        self.q_values[(state, action)] = new_q_value
        
class QLearningAgent(QAgent):
    
    
    def calculate_and_update_q_value(self, state, action, next_state, next_action, reward, action_space = None):
        # Update Q-value in the Q-table
        old_q_value = self.get_q_value(state, action)
        # target_q_value = reward + self.discount_factor * max(self.get_q_value(next_state, action) for a in range(self.action_space_size))
        target_q_value = reward + self.discount_factor * max(self.get_q_value(next_state, a) for a in action_space)
        new_q_value = old_q_value + self.learning_rate * (target_q_value - old_q_value)

        self.q_values[(state, action)] = new_q_value