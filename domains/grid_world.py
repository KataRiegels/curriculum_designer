from __future__ import annotations
import pygame
import sys
from mdp import *
# Initialize Pygame

class PygameInstance():
    def __init__(self):
    
        pygame.init()
        self.information_parser = {}


    # Constants
    GRID_SIZE = 50


    # Colors
    GROUND_COLOR = (255, 255, 255)
    PLAYER_COLOR = (255, 0, 0)
    KEY_COLOR = (255, 255, 0)
    CHEST_COLOR = (0, 255, 255)
    CACTUS_COLOR = (0, 255, 0)
    HOLE_COLOR = (0, 0, 0)


    generation_counter = 1
    #global player_position

    # Initialize the screen

    # Initialize positions
    #player_pos = [4,1]
    #key_pos = [1, 1]
    #chest_pos = [5, 7]
    cactus_pos = [1, 3], [1, 5], [8, 3], [8, 5]
    hole_pos = [2, 4], [3, 4], [4, 4], [5, 4], [6, 4], [7, 4]

    #global got_key


    #Reset function called on generation restart
    def reset_player(self):
        global player_pos, got_key

        player_pos = [x,y]
        got_key = False

        global generation_counter
        generation_counter += 1

    def reset_map(self):
        pass

    def start_game_mdp(self, stop_event, reset_event):
        font = pygame.font.Font(None, 36)
        generation_counter_fail = 0
        generation_counter_success = 0
        def reset():
            print(f"ran reset")
            self.got_key = self.mdp.agent.state.key_found
            self.player_pos = self.mdp.agent.state.coordinate
            self.grid = self.mdp.grid
            grid = self.grid
            
            self.key_pos = grid.key.coordinate
            self.chest_pos = grid.lock.coordinate
            
            self.hole_pos = grid.hole.coordinates
            self.beam_pos = grid.beams.coordinates
            
            
            pass
        
        reset()
        
        GRID_WIDTH = self.mdp.grid_size.width
        GRID_HEIGHT = self.mdp.grid_size.height
        
        
        SCREEN_WIDTH = GRID_WIDTH * self.GRID_SIZE
        SCREEN_HEIGHT = GRID_HEIGHT * self.GRID_SIZE

        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Grid_world")
        
        while not stop_event.is_set():
            got_key = self.got_key
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
                    

            #Checks collision of player and key
            if self.mdp.agent.state.key_found:
                got_key = True
            
            # if self.mdp.mdp_ended:
            if reset_event.is_set():
                print("MDP has ended")  
                # if self.mdp.term_cause == "hole":
                generation_counter_fail += 1  
                generation_counter_success += 1  
                reset()  
                reset_event.clear()
                
            
            """
            #Checks collision of player and chest, and if the player have colided with the key or not
                if (player_pos == chest_pos) and (got_key == True):
                    exit()

            #Checks collision with player and cacti
                for beam in cactus_pos:
                    if player_pos == beam:
                        reset_player()



            #Checks collision with player and hole
                for hole in hole_pos:
                    if player_pos == hole:
                        reset_player()

            """

            # Draw the grid
            screen.fill(self.GROUND_COLOR)
            for row in range(GRID_HEIGHT):
                for col in range(GRID_WIDTH):
                    pygame.draw.rect(screen, self.PLAYER_COLOR, (col * self.GRID_SIZE, row * self.GRID_SIZE, self.GRID_SIZE, self.GRID_SIZE), 1)

                # Draw the key based on if the player have collided with it or not
                if got_key == False:
                    pygame.draw.rect(screen, self.KEY_COLOR, (key_pos[0] * self.GRID_SIZE, key_pos[1] * self.GRID_SIZE, self.GRID_SIZE, self.GRID_SIZE))
                elif got_key == True:
                    pygame.draw.rect(screen, self.GROUND_COLOR,
                                    (key_pos[0] * self.GRID_SIZE, key_pos[1] * self.GRID_SIZE, self.GRID_SIZE, self.GRID_SIZE))



            #Draw the chest
            pygame.draw.rect(screen, self.CHEST_COLOR, (chest_pos[0] * self.GRID_SIZE, chest_pos[1] * self.GRID_SIZE, self.GRID_SIZE, self.GRID_SIZE))

            #Draw the cacti
            for beam in beam_pos:
                pygame.draw.rect(screen, self.CACTUS_COLOR, (beam[0] * self.GRID_SIZE, beam[1] * self.GRID_SIZE, self.GRID_SIZE, self.GRID_SIZE))

            #Draw the hole
            for hole in hole_pos:
                pygame.draw.rect(screen, self.HOLE_COLOR, (hole[0] * self.GRID_SIZE, hole[1] * self.GRID_SIZE, self.GRID_SIZE, self.GRID_SIZE))

            # Draw the player
            # pygame.draw.rect(screen, self.PLAYER_COLOR, (player_pos[0] * self.GRID_SIZE, player_pos[1] * self.GRID_SIZE, self.GRID_SIZE, self.GRID_SIZE))
            
            
            player_rect = pygame.Rect(player_pos[0] * self.GRID_SIZE, player_pos[1] * self.GRID_SIZE, self.GRID_SIZE, self.GRID_SIZE)
            # pygame.draw.rect(screen, self.PLAYER_COLOR, player_rect)
            player_center = (player_rect.x + player_rect.width // 2, player_rect.y + player_rect.height // 2)
            pygame.draw.circle(screen, self.PLAYER_COLOR, player_center, self.GRID_SIZE // 4)
            
            number_text = font.render(str(self.information_parser["fails"]), True, (255, 0, 0))
            screen.blit(number_text, (SCREEN_WIDTH - 50, 10))
            number_text = font.render(str(self.information_parser["successes"]), True, (0, 255, 0))
            screen.blit(number_text, (SCREEN_WIDTH - 100, 10))
            number_text = font.render(str(self.information_parser["keys"]), True, self.KEY_COLOR)
            screen.blit(number_text, (SCREEN_WIDTH - 150, 10))
            
            number_text = font.render("up" + str(self.information_parser["action log"]["up"]), True, (200, 0, 170))
            screen.blit(number_text, (SCREEN_WIDTH - 100, 110))
            number_text = font.render("down" + str(self.information_parser["action log"]["down"]), True, (200, 0, 170))
            screen.blit(number_text, (SCREEN_WIDTH - 100, 160))
            number_text = font.render("left" + str(self.information_parser["action log"]["left"]), True, (200, 0, 170))
            screen.blit(number_text, (SCREEN_WIDTH - 100, 210))
            number_text = font.render("right" + str(self.information_parser["action log"]["right"]), True, (200, 0, 170))
            screen.blit(number_text, (SCREEN_WIDTH - 100, 260))
            
            
            
            # Update the display
            pygame.display.flip()

            # Control the game speed
            pygame.time.Clock().tick(10)

        


