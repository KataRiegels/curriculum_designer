import random

import pygame
import sys

class Grid_World:
    def __init__(self, grid_width, grid_height, player_position_x, player_position_y, key_position, chest_position, cactus_positions, hole_positions, max_steps):
        pygame.init()

        self.GRID_SIZE = 50
        self.GROUND_COLOR = (255, 255, 255)
        self.PLAYER_COLOR = (255, 0, 0)
        self.KEY_COLOR = (255, 255, 0)
        self.CHEST_COLOR = (0, 255, 255)
        self.CACTUS_COLOR = (0, 255, 0)
        self.HOLE_COLOR = (0, 0, 0)

        self.generation_counter = 1
        self.got_key = False

        self.player_pos = [player_position_x, player_position_y]
        #saving the initial position of the player, and making it global so we can access it from functions
        global initial_pos
        initial_pos = [player_position_x, player_position_y]

        self.key_pos = key_position
        self.chest_pos = chest_position
        self.cactus_pos = cactus_positions
        self.hole_pos = hole_positions

        self.GRID_WIDTH = grid_width
        self.GRID_HEIGHT = grid_height
        self.SCREEN_WIDTH = self.GRID_WIDTH * self.GRID_SIZE
        self.SCREEN_HEIGHT = self.GRID_HEIGHT * self.GRID_SIZE

        self.max_steps = max_steps
        self.current_steps = 0
        self.accumulated_reward = 0

        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        pygame.display.set_caption("Grid_world")

    def reset_player(self):
        self.player_pos = [initial_pos[0], initial_pos[1]]
        self.got_key = False
        #print(self.accumulated_reward)
        self.accumulated_reward = 0

        self.generation_counter += 1
        self.current_steps = 0
        if self.generation_counter % 100 == 0:
            print(self.generation_counter)

    def check_max_steps(self):
        if self.current_steps >= self.max_steps:
            #print("Max steps reached. Resetting player")
            self.reset_player()

    def check_collisions(self):
        if self.player_pos == self.key_pos:
            self.got_key = True

        if (self.player_pos == self.chest_pos) and (self.got_key == True):
            print("success")
            #exit()
            print(self.generation_counter)
            self.reset_player()

        for cacti in self.cactus_pos:
            if self.player_pos == cacti:
                self.reset_player()

        for hole in self.hole_pos:
            if self.player_pos == hole:
                self.reset_player()

    def move(self, action):

        #random movement based on the action space
        #action = random.randint(0, 3)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        if action == 0 and self.player_pos[0] > 0:
            self.player_pos[0] -= 1
        elif action == 1 and self.player_pos[0] < self.GRID_WIDTH - 1:
            self.player_pos[0] += 1
        elif action == 2 and self.player_pos[1] > 0:
            self.player_pos[1] -= 1
            #self.calculate_reward(tuple(initial_pos), action, tuple(self.player_pos))
        elif action == 3 and self.player_pos[1] < self.GRID_HEIGHT - 1:
            self.player_pos[1] += 1
        self.current_steps += 1

            #self.calculate_reward(tuple(initial_pos), action, tuple(self.player_pos))
        #print(self.accumulated_reward)

#Only next_state is used when calculating reward
    def calculate_reward(self, state, action, next_state):
         # Assuming state and next_state are tuples representing (x, y) coordinates

         # Check if the agent hits a hole or cactus
         if next_state in self.hole_pos or next_state in self.cactus_pos:
             reward = -10
         # Check if the agent hits the key
         elif next_state == self.key_pos and self.got_key == False:
             reward = 100
         # Check if the agent hits the chest after hitting the key
         elif self.got_key and next_state == self.chest_pos:
             reward = 100
         #
         # # Default reward for other cases
         else:
             reward = -0.1

         self.accumulated_reward += reward
         #print(self.accumulated_reward)

         return self.accumulated_reward

    def render(self):
        #Checks if the max number of steps have been reached
        self.check_max_steps()
        for row in range(self.GRID_HEIGHT):
            for col in range(self.GRID_WIDTH):
                pygame.draw.rect(self.screen, self.PLAYER_COLOR,
                                 (col * self.GRID_SIZE, row * self.GRID_SIZE, self.GRID_SIZE, self.GRID_SIZE), 1)

            if self.got_key == False:
                pygame.draw.rect(self.screen, self.KEY_COLOR,
                                 (self.key_pos[0] * self.GRID_SIZE, self.key_pos[1] * self.GRID_SIZE,
                                  self.GRID_SIZE, self.GRID_SIZE))
            elif self.got_key == True:
                pygame.draw.rect(self.screen, self.GROUND_COLOR,
                                 (self.key_pos[0] * self.GRID_SIZE, self.key_pos[1] * self.GRID_SIZE,
                                  self.GRID_SIZE, self.GRID_SIZE))

        pygame.draw.rect(self.screen, self.PLAYER_COLOR,
                         (self.player_pos[0] * self.GRID_SIZE, self.player_pos[1] * self.GRID_SIZE,
                          self.GRID_SIZE, self.GRID_SIZE))

        pygame.draw.rect(self.screen, self.CHEST_COLOR,
                         (self.chest_pos[0] * self.GRID_SIZE, self.chest_pos[1] * self.GRID_SIZE,
                          self.GRID_SIZE, self.GRID_SIZE))

        for cacti in self.cactus_pos:
            pygame.draw.rect(self.screen, self.CACTUS_COLOR,
                             (cacti[0] * self.GRID_SIZE, cacti[1] * self.GRID_SIZE, self.GRID_SIZE, self.GRID_SIZE))

        for hole in self.hole_pos:
            pygame.draw.rect(self.screen, self.HOLE_COLOR,
                             (hole[0] * self.GRID_SIZE, hole[1] * self.GRID_SIZE, self.GRID_SIZE, self.GRID_SIZE))

        pygame.display.flip()
        pygame.time.Clock().tick()

