from domains.grid_world import grid_world
from algorithm import q_learning

domain = grid_world.Grid_World(10, 10, 4, 1, [1, 1], [5, 7], [[8, 3], [8, 5]], [[2, 4], [3, 4], [4, 4], [5, 4], [6, 4], [7, 4]], 40)
#domain.start_game()

# Create a Q-learning agent with appropriate parameters
q_agent = q_learning.QLearningAgent(10000, 5000000, (domain.GRID_HEIGHT * domain.GRID_WIDTH), 4, 0.1, 0.9, 0.4)


# Main loop
while True:
    # Agent chooses an action based on the current state
    action = q_agent.choose_action(tuple(domain.player_pos))
    #print("This is the action: ",action)
    current_state = [domain.player_pos[0], domain.player_pos[1]]
    #print("This is the current state: ", current_state)
    # Agent performs the chosen action
    domain.move(action)

    new_state = [domain.player_pos[0], domain.player_pos[1]]
    #print("This is the new state: ", new_state)
    # Agent receives a reward and updates Q-value based on the observed outcome
    # Reward function is defined within domain and is updated based
    reward = domain.calculate_reward(current_state, action, new_state)
    old_q_value = q_agent.get_q_value(tuple(new_state), action)
    new_q_value = old_q_value + q_agent.learning_rate * (reward + q_agent.discount_factor * max(q_agent.get_q_value(tuple(domain.player_pos), a) for a in range(q_agent.action_space_size)) - old_q_value)
    q_agent.update_q_value(tuple(new_state), action, new_q_value)

    #print(reward)
    #print("This is the old Q-value: ",old_q_value)
    #print("This is the new Q-value",new_q_value)

    # Update the environment and render
    domain.check_collisions()
    domain.screen.fill(domain.GROUND_COLOR)
    domain.render()
