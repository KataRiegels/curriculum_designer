import pygame
import sys

# Initialize Pygame
pygame.init()


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
def reset_player():
    global player_pos, got_key

    player_pos = [x,y]
    got_key = False

    global generation_counter
    generation_counter += 1
    print(generation_counter)


def start_game(grid_height, grid_width, player_position, key_position, chest_position):
    global player_pos, x, y, got_key

    got_key = False
    player_pos = player_position
    x, y = player_pos[0], player_pos[1]
    key_pos = key_position
    chest_pos = chest_position
    GRID_WIDTH = grid_width
    GRID_HEIGHT = grid_height
    SCREEN_WIDTH = GRID_WIDTH * GRID_SIZE
    SCREEN_HEIGHT = GRID_HEIGHT * GRID_SIZE

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Grid_world")
    # Game loop
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                # Move the player based on arrow keys
                if event.key == pygame.K_LEFT and player_pos[0] > 0:
                    player_pos[0] -= 1
                elif event.key == pygame.K_RIGHT and player_pos[0] < GRID_WIDTH - 1:
                    player_pos[0] += 1
                elif event.key == pygame.K_UP and player_pos[1] > 0:
                    player_pos[1] -= 1
                elif event.key == pygame.K_DOWN and player_pos[1] < GRID_HEIGHT - 1:
                    player_pos[1] += 1

    #Checks collision of player and key
        if player_pos == key_pos:
            got_key = True

    #Checks collision of player and chest, and if the player have colided with the key or not
        if (player_pos == chest_pos) and (got_key == True):
            exit()

    #Checks collision with player and cacti
        for cacti in cactus_pos:
            if player_pos == cacti:
                reset_player()



    #Checks collision with player and hole
        for hole in hole_pos:
            if player_pos == hole:
                reset_player()


        # Draw the grid
        screen.fill(GROUND_COLOR)
        for row in range(GRID_HEIGHT):
            for col in range(GRID_WIDTH):
                pygame.draw.rect(screen, PLAYER_COLOR, (col * GRID_SIZE, row * GRID_SIZE, GRID_SIZE, GRID_SIZE), 1)

            # Draw the key based on if the player have collided with it or not
            if got_key == False:
                pygame.draw.rect(screen, KEY_COLOR, (key_pos[0] * GRID_SIZE, key_pos[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE))
            elif got_key == True:
                pygame.draw.rect(screen, GROUND_COLOR,
                                (key_pos[0] * GRID_SIZE, key_pos[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE))

        # Draw the player
        pygame.draw.rect(screen, PLAYER_COLOR, (player_pos[0] * GRID_SIZE, player_pos[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE))


        #Draw the chest
        pygame.draw.rect(screen, CHEST_COLOR, (chest_pos[0] * GRID_SIZE, chest_pos[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE))

        #Draw the cacti
        for cacti in cactus_pos:
            pygame.draw.rect(screen, CACTUS_COLOR, (cacti[0] * GRID_SIZE, cacti[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE))

        #Draw the hole
        for hole in hole_pos:
            pygame.draw.rect(screen, HOLE_COLOR, (hole[0] * GRID_SIZE, hole[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE))

        # Update the display
        pygame.display.flip()

        # Control the game speed
        pygame.time.Clock().tick(10)

