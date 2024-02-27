import grid_world
import q_learning

domain = grid_world.Grid_World(10, 10, 4, 1, [1, 1], [5, 7], [[1, 3], [1, 5], [8, 3], [8, 5]], [[2, 4], [3, 4], [4, 4], [5, 4], [6, 4], [7, 4]])
#domain.start_game()

# Create a Q-learning agent with appropriate parameters
q_agent = q_learning.QLearningAgent(2, 4, 0.1, 0.9, 0.1)


# Main loop
while True:
    # Agent chooses an action based on the current state
    action = q_agent.choose_action(tuple(domain.player_pos))
    current_state = tuple(domain.player_pos)

    # Agent performs the chosen action
    domain.move()

    new_state = tuple(domain.player_pos)

    # Agent receives a reward and updates Q-value based on the observed outcome
    # Reward function is defined within domain and is updated based
    reward = domain.calculate_reward(current_state, action, new_state)
    old_q_value = q_agent.get_q_value(tuple(domain.player_pos), action)
    new_q_value = old_q_value + q_agent.learning_rate * (reward + q_agent.discount_factor * max(q_agent.get_q_value(tuple(domain.player_pos), a) for a in range(q_agent.action_space_size)) - old_q_value)
    q_agent.update_q_value(tuple(domain.player_pos), action, new_q_value)

    #print(q_agent.get_q_value(new_q_value, action))

    # Update the environment and render
    domain.check_collisions()
    domain.screen.fill(domain.GROUND_COLOR)
    domain.render()
