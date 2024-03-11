from __future__ import annotations
import pygame
import sys
from mdp import *
# Initialize Pygame

class PygameInstance():


    # Constants
    GRID_SIZE = 50


    # Colors
    GROUND_COLOR = (255, 255, 255)
    PLAYER_COLOR = (255, 0, 255)
    KEY_COLOR = (255, 255, 0)
    CHEST_COLOR = (0, 255, 255)
    CACTUS_COLOR = (0, 255, 0)
    HOLE_COLOR = (0, 0, 0)


    generation_counter = 1

    def __init__(self):
    
        pygame.init()
        self.information_parser = {}


    def reset_map(self):
        pass

    def start_game_mdp(self, stop_event, reset_event, go_to_optimal_event):
        
        self.text_render_number = 0
        
        # sets everything to the initial values matching the mdp
        def reset():
            print(f'reset with mdp size: {self.mdp.grid.size}')
            self.got_key = self.mdp.agent.state.key_found
            self.player_pos = self.mdp.agent.state.coordinate
            self.grid = self.mdp.grid
            grid = self.grid
            
            self.key_pos = grid.key.coordinate
            self.chest_pos = grid.lock.coordinate
            
            self.hole_pos = grid.hole.coordinates
            self.beam_pos = grid.beams.coordinates
        
        reset()
        
        GRID_WIDTH = self.mdp.grid_size.width
        GRID_HEIGHT = self.mdp.grid_size.height
        
        
        SCREEN_WIDTH = GRID_WIDTH * self.GRID_SIZE + 200
        SCREEN_HEIGHT = GRID_HEIGHT * self.GRID_SIZE
        
        self.SCREEN_WIDTH = SCREEN_WIDTH
        self.SCREEN_HEIGHT = SCREEN_HEIGHT
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Grid_world")
        
        while not stop_event.is_set():
            player_pos = self.player_pos
            grid = self.grid
            key_pos = self.key_pos
            chest_pos = self.chest_pos
            hole_pos = self.hole_pos
            beam_pos = self.beam_pos
            
            
            
            player_pos = self.mdp.agent.state.coordinate
            for event in pygame.event.get():
                if event.type == pygame.QUIT  :
                    stop_event.set()
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        stop_event.set()
                        pygame.quit()
                        sys.exit()
                    if event.key == pygame.K_w:
                        # go_to_optimal_event.set()
                        go_to_optimal_event.set_value("next")
                        # reset_event.set()
                        reset_event.set_value("policy")
                        reset()  
                    if event.key == pygame.K_e:
                        # go_to_optimal_event.set()
                        go_to_optimal_event.set_value("optimal")
                        # reset_event.set()
                        reset_event.set_value("policy")
                        reset()  
                            

            # Happens when the run_mdp loop signals the mdp episode has ended
            if reset_event.is_set():
                reset()  
                reset_event.clear()
                
            # Draw the grid
            screen.fill(self.GROUND_COLOR)
            
                #Draw the key
            if not self.mdp.agent.state.key_found:
                pygame.draw.rect(screen, self.KEY_COLOR, (key_pos[0] * self.GRID_SIZE, key_pos[1] * self.GRID_SIZE, self.GRID_SIZE, self.GRID_SIZE))

            #Draw the chest
            pygame.draw.rect(screen, self.CHEST_COLOR, (chest_pos[0] * self.GRID_SIZE, chest_pos[1] * self.GRID_SIZE, self.GRID_SIZE, self.GRID_SIZE))

            #Draw the cacti
            for beam in beam_pos:
                pygame.draw.rect(screen, self.CACTUS_COLOR, (beam[0] * self.GRID_SIZE, beam[1] * self.GRID_SIZE, self.GRID_SIZE, self.GRID_SIZE))

            #Draw the hole
            for hole in hole_pos:
                pygame.draw.rect(screen, self.HOLE_COLOR, (hole[0] * self.GRID_SIZE, hole[1] * self.GRID_SIZE, self.GRID_SIZE, self.GRID_SIZE))

            
            
            # for row in range(GRID_HEIGHT):
            #     for col in range(GRID_WIDTH):
            for row in range(self.mdp.grid.height):
                for col in range(self.mdp.grid.width):
                    # pygame.draw.rect(screen, self.PLAYER_COLOR, (col * self.GRID_SIZE, row * self.GRID_SIZE, self.GRID_SIZE, self.GRID_SIZE), 1)
                    cell_rect = pygame.Rect(col * self.GRID_SIZE, row * self.GRID_SIZE, self.GRID_SIZE, self.GRID_SIZE)
                    # Draw the cell border
                    pygame.draw.rect(screen, self.PLAYER_COLOR, cell_rect, 1)
                    
                    

                    # Get the Q-values for the current cell
                    # cell_q_values = self.information_parser["q_values"][row][col]
                    cell_q_values = self.information_parser["q_values_grid"][col][row]
                    if not all(value == 0.0 for value in cell_q_values.values()):
                        # Handle the case where all values are 0.0 (no arrows needed)
                        max_value = max(cell_q_values.values())
                        max_actions = [action for action, value in cell_q_values.items() if value == max_value]

                        # Use a different color if more than one action has the same max Q-value
                        arrow_color = (200, 200, 200)  # Default color
                        if len(max_actions) > 1:
                            # arrow_color = (0, 0, 255)  # Blue for example
                            arrow_color = "#8f9eff"  # Blue for example

                        # Draw arrows based on the highest Q-value action
                        arrow_size = self.GRID_SIZE // 6
                        if max_actions[0] == 0:  # Up
                            pygame.draw.polygon(screen, arrow_color, [(cell_rect.centerx, cell_rect.centery - arrow_size),
                                                                    (cell_rect.centerx + arrow_size, cell_rect.centery + arrow_size),
                                                                    (cell_rect.centerx - arrow_size, cell_rect.centery + arrow_size)])
                        elif max_actions[0] == 1:  # Right
                            pygame.draw.polygon(screen, arrow_color, [(cell_rect.centerx + arrow_size, cell_rect.centery),
                                                                    (cell_rect.centerx - arrow_size, cell_rect.centery + arrow_size),
                                                                    (cell_rect.centerx - arrow_size, cell_rect.centery - arrow_size)])
                        elif max_actions[0] == 2:  # Down
                            pygame.draw.polygon(screen, arrow_color, [(cell_rect.centerx, cell_rect.centery + arrow_size),
                                                                    (cell_rect.centerx + arrow_size, cell_rect.centery - arrow_size),
                                                                    (cell_rect.centerx - arrow_size, cell_rect.centery - arrow_size)])
                        elif max_actions[0] == 3:  # Left
                            pygame.draw.polygon(screen, arrow_color, [(cell_rect.centerx - arrow_size, cell_rect.centery),
                                                                    (cell_rect.centerx + arrow_size, cell_rect.centery + arrow_size),
                                                                    (cell_rect.centerx + arrow_size, cell_rect.centery - arrow_size)])
                    """
                    """

                # Draw the key based on if the player have collided with it or not
                # if not grid.key.coordinate:
                #     pygame.draw.rect(screen, self.KEY_COLOR, (key_pos[0] * self.GRID_SIZE, key_pos[1] * self.GRID_SIZE, self.GRID_SIZE, self.GRID_SIZE))
                # elif grid.key.coordinate:
                #     pygame.draw.rect(screen, self.GROUND_COLOR,
                #                     (key_pos[0] * self.GRID_SIZE, key_pos[1] * self.GRID_SIZE, self.GRID_SIZE, self.GRID_SIZE))


        
            
            player_rect = pygame.Rect(player_pos[0] * self.GRID_SIZE, player_pos[1] * self.GRID_SIZE, self.GRID_SIZE, self.GRID_SIZE)
            # print(f'Player pos: {player_pos}')
            # pygame.draw.rect(screen, self.PLAYER_COLOR, player_rect)
            player_center = (player_rect.x + player_rect.width // 2, player_rect.y + player_rect.height // 2)
            pygame.draw.circle(screen, self.PLAYER_COLOR, player_center, self.GRID_SIZE // 4)
            
            
            # Writes information on the screen
            self.text_renderer( "fails", (255, 0, 0), screen, parsed = True)
            self.text_renderer( "successes", self.CHEST_COLOR, screen, parsed = True)
            self.text_renderer( "keys", (230, 230, 0), screen, parsed = True)
            if ((self.information_parser["fails"]+self.information_parser["successes"]) != 0):
                fail_success = self.information_parser["successes"]/(self.information_parser["fails"]+self.information_parser["successes"])
                self.text_renderer( f"success rate: {fail_success} ", (0, 255, 0) , screen, parsed = False)
            if ((self.information_parser["fails"]+self.information_parser["successes"]) != 0):
                fail_success = self.information_parser["keys"]/(self.information_parser["fails"]+self.information_parser["successes"])
                self.text_renderer( f"keys rate: {fail_success} ", (200, 200, 0) , screen, parsed = False)
            
            
            rd = 0
            q_values = self.information_parser["q_values"]
            self.text_renderer(f"up: {round(q_values[0],rd)}", (0,0,0), screen, parsed = False)
            self.text_renderer(f"right: {round(q_values[1],rd)}", (0,0,0), screen, parsed = False)
            self.text_renderer(f"down: {round(q_values[2],rd)}", (0,0,0), screen, parsed = False)
            self.text_renderer(f"left: {round(q_values[3],rd)}", (0,0,0), screen, parsed = False)
            
            self.text_render_number = 0
            
            
            
            
            
            # Update the display
            pygame.display.flip()

            # Control the game speed
            pygame.time.Clock().tick(10)

    def text_renderer(self, parser, color, screen, parsed = False):
        font = pygame.font.Font(None, 24)
        
        self.text_render_number += 1
        if parsed:
            text_to_render = f"{parser}: {str(round(self.information_parser[parser],4))}"
        else:
            text_to_render = parser
        number_text = font.render(text_to_render, True, color)
        
        screen.blit(number_text, (self.SCREEN_WIDTH - 190, 30*self.text_render_number - 25))
        
        return
        


