import random
import numpy as np
import copy

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

    # def get_q_value(self, state, action):
    #     # Retrieve Q-value from the Q-table
    #     #print(self.q_values)
    #     return self.q_values.get((state, action), 0.0)

    def get_q_value(self, state, action):
        # Retrieve Q-value from the Q-table
        key = (state, action)
        q_value = self.q_values.get(key, None)

        # if q_value is None:
        #     pass
        #     print(f"Q-value not found for key: {key}. Using default value: 0.0")
        # else:
        #     print(f"Q-value found for key: {key} with value {q_value}")

        return q_value if q_value is not None else 0.0


    def calculate_and_update_q_value(self, state, action, next_state, next_action, reward):
        """Calculates q_value based on SARSA rule, and updates q_value accordingly"""
        old_q_value = self.get_q_value(state, action)
        target_q_value = reward + self.discount_factor * (self.get_q_value(next_state, next_action))
        new_q_value = old_q_value + self.learning_rate * (target_q_value - old_q_value)
        self.q_values[(state, action)] = new_q_value

    # def update_q_value(self, state, action, new_value):
    #     # Update Q-value in the Q-table
    #     self.q_values[(state, action)] = new_value

    def choose_action(self, state):
        # Epsilon-greedy policy for action selection
        
        if self.use_optimal: return self.choose_policy_action(state)
        
        if random.uniform(0, 1) < self.exploration_rate:
            action = random.choice(range(self.action_space_size))
            return action

        else:
            # state_tuple = tuple(state)
            # Choose the action with the highest Q-value
            q_values = [self.get_q_value(state, a) for a in range(self.action_space_size)]
            max_q_value = max(q_values)
            max_q_indices = [i for i, q in enumerate(q_values) if q == max_q_value]
            # if q_values != [0.0, 0.0, 0.0, 0.0]:
            #     print(f'Q values: {q_values}')
            #     print(f'max Q values: {max_q_value}')
            #     print(f'max Q action: {max_q_indices}')

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

    def get_optimal_policy(self):
        optimal_policy = {}

        # Iterate over all unique states
        for state in self.get_unique_states():
            # Get Q-values for the current state
            q_values_for_state = self.get_q_values_for_state(state)

            # Determine the optimal action based on Q-values
            optimal_action = max(q_values_for_state, key=q_values_for_state.get)

            # Store the optimal action for the current state
            optimal_policy[state] = optimal_action
        self.optimal_policy = optimal_policy
        return optimal_policy

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
        # if self.use_optimal:
        #     for state, optimal_action in optimal_policy.items():
        #         for action in range(self.action_space_size):
        #             q_value = 1.0 if action == optimal_action else 0.0  # Set Q-value to 1 for optimal action, 0 otherwise
        #             # return q_value
        #             self.q_values[(state, action)] = q_value
        # print(f'q values: {self.q_values}')
                    
    def choose_policy_action(self, state):
        # Epsilon-greedy policy for action selection
            # state_tuple = tuple(state)
        # Choose the action with the highest Q-value
        # print(state)
        q_values = [self.get_q_value(state, a) for a in range(self.action_space_size)]
        max_q_value = max(q_values)
        max_q_indices = [i for i, q in enumerate(q_values) if q == max_q_value]
        # if q_values != [0.0, 0.0, 0.0, 0.0]:
        #     print(f'Q values: {q_values}')

            # Randomly choose one of the actions with the maximum Q-value
        chosen_action = random.choice(max_q_indices)

        return chosen_action
    
    
    def copy(self):
        # Create a deep copy of the agent
        
        return copy.deepcopy(self)
