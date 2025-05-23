import pygame
import json
from sys import exit

pygame.init()

class Block(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h, block_id=0, color=(0, 255 ,0)):
        super().__init__()
        self.block_id = block_id  # store block type id
        self.image = pygame.Surface((w, h))
        self.image.fill(color)
        self.rect = self.image.get_rect(topleft=(x, y))

BLOCK_TYPES = {
    0: (0, 255, 0),     # Green block (Grass block)
    1: (255, 0, 0),     # Red block (Damage block)
    2: (0, 0, 255),     # Blue block (Water block)
    3: (0, 0, 0),       # Black block (Void block)
    4: (255, 255, 0),
    5: (255, 128, 0),
    6: (128, 0, 255),
    7: (0, 255, 255),
}


info = pygame.display.Info()
SCREEN_WIDTH = 1600
SCREEN_HEIGHT = 800

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Setup Clock for FPS management
clock = pygame.time.Clock()

# Setting up Background
sky_surf = pygame.image.load('Sprites/sky.png').convert()
sky_surf = pygame.transform.scale(sky_surf, (SCREEN_WIDTH, 600))

ground_rect = pygame.Rect(0, 600, SCREEN_WIDTH, 200)

# Object Rects
player_rect = pygame.Rect(200, 600, 55, 64)
platform1_rect = pygame.Rect(750, 400, 100, 20)
platform2_rect = pygame.Rect(1200, 500, 100, 20)
platform3_rect = pygame.Rect(1500, 400, 100, 20)

# List player sprites to animate
player_sprite_right = [pygame.image.load('Sprites/player/sprite_1right.png').convert_alpha(),
                                    pygame.image.load('Sprites/player/sprite_2right.png').convert_alpha()]
player_sprite_left = [pygame.image.load('Sprites/player/sprite_1left.png').convert_alpha(),
                                    pygame.image.load('Sprites/player/sprite_2left.png').convert_alpha()]


# DEBUG MODE TOGGLE
DEBUG = False

# Player variables
frame_index = 0
frame_timer = 0
animation_speed = 20

# General variables
player_vel = 0
bg_scroll = 0
scroll_speed = 5
landed = 0
left_collision = False
right_collision = False
dead = False
death_jump = False
GRID_SIZE = 20

prev_bottom = 0
prev_top = 0
prev_left = 0
prev_right = 0

# Store player facing directon [1 = Left, 0 = Right]
prev_direction = 0

platforms = [ground_rect, platform1_rect, platform2_rect, platform3_rect]
platforms_draw = [platform1_rect, platform2_rect, platform3_rect]


def handle_collision():
    global player_vel, left_collision, right_collision, landed
    # Check for collisions after vertical movement
    for platform in platforms:
        if player_rect.colliderect(platform):
            if player_vel >= 0 and prev_bottom <= platform.top:
                # Landed on top
                player_rect.bottom = platform.top
                player_vel = 0
                landed = True
            elif player_vel <= 0 and prev_top >= platform.bottom:
                # Hit from below
                player_rect.top = platform.bottom
                player_vel = 0

    # Check for side collisions (left and right) to prevent scrolling
    left_collision = False
    right_collision = False
    for platform in platforms:
        if player_rect.colliderect(platform):
            if prev_right > platform.left and prev_left < platform.left:
                # Collided from the left
                left_collision = True
                break
            if prev_left < platform.right and prev_right > platform.right:
                # Collided from the right
                right_collision = True
                break

def draw_objects():
    global DEBUG
    screen.fill((0, 0, 0))
    screen.blit(sky_surf, (bg_scroll % SCREEN_WIDTH - SCREEN_WIDTH, 0))
    screen.blit(sky_surf, (bg_scroll % SCREEN_WIDTH, 0))



    for platform in platforms_draw:
        pygame.draw.rect(screen, (255, 255, 255), platform)

    if DEBUG:
        pygame.draw.rect(screen, (0, 255, 0), player_rect)

def movement():
    global frame_index, frame_timer, animation_speed, prev_direction, bg_scroll, player_vel, landed
    keys = pygame.key.get_pressed()

    # Handle horizontal movement
    if keys[pygame.K_a] and not right_collision and not dead:
        bg_scroll += scroll_speed
        for platform in platforms:
            platform.x += scroll_speed
        prev_direction = 1
    if keys[pygame.K_d] and not left_collision and not dead:
        bg_scroll -= scroll_speed
        for platform in platforms:
            platform.x -= scroll_speed
        prev_direction = 0
    if keys[pygame.K_SPACE] and landed == 1:
        player_vel -= 20

    # Apply gravity if not on a platform
    if player_vel < 15:
        player_vel += 0.75
    landed = 0
    frame_timer += 1


def death():
    global dead, death_jump, player_vel
    if player_rect.bottom >= 900:
        dead = True
    if dead == True and not death_jump:
        player_vel = -25
        death_jump = True

def animations():
    global prev_direction, frame_index, frame_timer, current_image_left, current_image_right

    current_image_right = player_sprite_right[frame_index]
    current_image_left = player_sprite_left[frame_index]
    
    keys = pygame.key.get_pressed()
    if frame_timer >= animation_speed:
        frame_index = (frame_index + 1) % len(player_sprite_right)
        frame_timer = 0

    # Check what key is pressed and draw corrosponding sprite
    if keys[pygame.K_d] and not keys[pygame.K_a]:
        screen.blit(current_image_right,player_rect.topleft)
        prev_direction = 0
    if keys[pygame.K_a] and not keys[pygame.K_d]:
        screen.blit(current_image_left,player_rect.topleft)
        prev_direction = 1
    if prev_direction == 0 and not keys[pygame.K_d]:
        screen.blit(player_sprite_right[0],player_rect.topleft)
    elif prev_direction == 1 and not keys[pygame.K_a]:
        screen.blit(player_sprite_left[0],player_rect.topleft)
    elif prev_direction == 0 and keys[pygame.K_a] and keys[pygame.K_d]:
        screen.blit(player_sprite_right[0],player_rect.topleft)

def load_and_draw_map(filename, surface, block_group, block_width, block_height):
    try:
        with open(filename, 'r') as f:
            data = json.load(f)

        for item in data:
            block_id = item['block_id']
            x = item['x']
            y = item['y']
            color = BLOCK_TYPES.get(block_id, (100, 100, 100))
            block = Block(x, y, block_width, block_height, block_id, color)
            block_group.add(block)

        # Draw blocks to the surface
        block_group.draw(surface)
        print(f"Loaded and drew map from {filename}")
    except Exception as e:
        print(f"Failed to load or draw map: {e}")


while True:
    # Draw all objects
    draw_objects()
    # Draw map
    loaded_blocks = pygame.sprite.Group()
    load_and_draw_map("my_level.json", screen, loaded_blocks, GRID_SIZE, GRID_SIZE)
    # Handle movement
    movement()
    # Handle collisions
    handle_collision()
    # Check if player is dead
    death()
    # Handle animations
    animations()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()


    # Save previous values before moving
    prev_bottom = player_rect.bottom
    prev_top = player_rect.top
    prev_left = player_rect.left
    prev_right = player_rect.right

    # Move player based on velocity
    player_rect.y += player_vel

    pygame.display.update()
    clock.tick(60)