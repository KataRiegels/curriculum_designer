import random
import numpy as np
import copy

class Policy(dict):
    def __init__(self, q_values = None):
        self.q_values = q_values
        self.policy = {}
        self.action_space_size = 4
        if q_values:
            self.set_optimal_policy(q_values)
        # else:
        #     # Generate random Q-values and set random policy
        #     self.q_values = self.generate_random_q_values()
        #     self.set_random_policy()
    
    def init_policy_from_states(self, states):
        for state in states:
            self[state] = 0.0
        pass
        
    def set_optimal_policy(self, q_values):
        self.policy = self.get_optimal_policy(q_values)
    
    def get_optimal_policy(self, q_values):
        optimal_policy = {}
        # Iterate over all unique states
        for state in self.get_unique_states():
            # Get Q-values for the current state
            q_values_for_state = self.get_q_values_for_state(state)

            # Determine the optimal action based on Q-values
            optimal_action = max(q_values_for_state, key=q_values_for_state.get)

            # Store the optimal action for the current state
            self[state] = optimal_action

        return self
    
    def get_unique_states(self):
        unique_states = set()

        for (state, _), _ in self.q_values.items():
            unique_states.add(state)

        return list(unique_states)       
    
    def get_q_values_for_state(self, state):
        # Retrieve all Q-values for a specific state
        q_values_for_state = {action: self.get_q_value(state, action) for action in range(self.action_space_size)}
        return q_values_for_state
    
    
    def generate_random_q_values(self):
        q_values = {}
        for state in self.get_unique_states():
            q_values[state] = [random.random() for _ in range(self.action_space_size)]
        return q_values

    def set_random_policy(self):
        self.policy = self.get_policy_from_q_values(self.q_values)
    def get_q_value(self, state, action):
        # Retrieve Q-value from the Q-table
        key = (state, action)
        q_value = self.q_values.get(key, None)
        return q_value if q_value is not None else 0.0
    
    def get_q_value_from_values(self, state, action, q_values):
        # Retrieve Q-value from the Q-table
        key = (state, action)
        q_value = q_values.get(key, None)
        return q_value if q_value is not None else 0.0
    
    
    def get_policy_action(self, state):
        return self.choose_policy_action(state)




    @staticmethod
    def get_policy_from_q_values(self, q_values):
        return_policy = Policy()

        # Iterate over all unique states
        for state in self.get_unique_states():
            # Get Q-values for the current state
            q_values_for_state = {action: self.get_q_value_from_values(state, action, q_values) for action in range(self.action_space_size)}
            # q_values_for_state = self.get_q_values_for_state(state)
            

            # Determine the optimal action based on Q-values
            optimal_action = max(q_values_for_state, key=q_values_for_state.get)

            # Store the optimal action for the current state
            return_policy[state] = optimal_action

        return return_policy


    def set_q_values_from_policy(self, optimal_policy):
        self.q_values = {}
        for state, optimal_action in optimal_policy.items():
            if optimal_action is not None:  # Check if optimal_action is not None
                for action in range(self.action_space_size):
                    q_value = 1.0 if action == optimal_action else 0.0
                    self.q_values[(state, action)] = q_value



    def choose_policy_action(self, state):
        # Choose the action with the highest Q-value
        q_values = [self.q_values.get((state, a), 0.0) for a in range(len(self.q_values[state]))]
        max_q_value = max(q_values)
        max_q_indices = [i for i, q in enumerate(q_values) if q == max_q_value]

        # Randomly choose one of the actions with the maximum Q-value
        chosen_action = random.choice(max_q_indices)

        return chosen_action



    def copy(self):
        return copy.deepcopy(self)















