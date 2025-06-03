import pygame
from Block import Block
from LevelLoader import load_level_from_json
from sys import exit

pygame.init()

BLOCK_TYPES = {
    0: (0, 255, 0),     # Green block (Grass block)
    1: (255, 0, 0),     # Red block (Damage block)
    2: (0, 0, 255),     # Blue block (Water block)
    3: (0, 0, 0),       # Black block (Void block)
    4: (255, 255, 0),   # Orange block
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

# Setting up Hearts
heart_image = pygame.image.load('Sprites/heart.png').convert_alpha()
heart_image = pygame.transform.scale(heart_image, (40, 40))  # Resize if needed

# Object Rects
player_rect = pygame.Rect(200, 600, 55, 64)
 
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

player_health = 3
max_health = 3

invincible = False
iframe_timer = 0
IFRAME_DURATION = 500  # milliseconds (1 second of invincibility)


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

blocks = pygame.sprite.Group()
load_level_from_json('my_level.json', Block, blocks, 20, 20, BLOCK_TYPES)

platforms = [
    (block.rect.copy(), block.block_id)  # .copy() avoids modifying the original rect
    for block in blocks
]

def handle_collision():
    global player_vel, left_collision, right_collision, landed, player_health, iframe_timer, invincible, current_time
    # Check for collisions after vertical movement
    for rect, block_id in platforms:
        if player_rect.colliderect(rect):
            if player_vel >= 0 and prev_bottom <= rect.top:
                # Landed on top
                player_rect.bottom = rect.top
                player_vel = 0
                landed = True
                current_time = pygame.time.get_ticks()
                if block_id == 1:
                    if not invincible:
                        if player_health > 0:
                            player_health -= 1
                            invincible = True
                            iframe_timer = current_time
            elif player_vel <= 0 and prev_top >= rect.bottom:
                # Hit from below
                player_rect.top = rect.bottom
                player_vel = 0
                current_time = pygame.time.get_ticks()
                if block_id == 1:
                    if not invincible:
                        if player_health > 0:
                            player_health -= 1
                            invincible = True
                            iframe_timer = current_time

    # Check for side collisions (left and right) to prevent scrolling
    left_collision = False
    right_collision = False
    for rect, block_id in platforms:
        if player_rect.colliderect(rect):
            if prev_right > rect.left and prev_left < rect.left:
                # Collided from the left
                left_collision = True
                current_time = pygame.time.get_ticks()
                if block_id == 1:
                    if not invincible:
                        if player_health > 0:
                            player_health -= 1
                            invincible = True
                            iframe_timer = current_time
                break
            if prev_left < rect.right and prev_right > rect.right:
                # Collided from the right
                right_collision = True
                current_time = pygame.time.get_ticks()
                if block_id == 1:
                    if not invincible:
                        if player_health > 0:
                            player_health -= 1
                            invincible = True
                            iframe_timer = current_time
                break

def draw_objects():
    global DEBUG
    screen.fill((0, 0, 0))
    screen.blit(sky_surf, (bg_scroll % SCREEN_WIDTH - SCREEN_WIDTH, 0))
    screen.blit(sky_surf, (bg_scroll % SCREEN_WIDTH, 0))

    for rect, block_id in platforms:
            color = BLOCK_TYPES.get(block_id, (255, 255, 255)) # Fallback color
            pygame.draw.rect(screen, color, rect)

    if DEBUG:
        pygame.draw.rect(screen, (0, 255, 0), player_rect)

def draw_hearts(screen, health, max_health, heart_image):
    for i in range(max_health):
        if i < health:
            x = 1200 + i * 50  # 50 px gap
            y = 50
            screen.blit(heart_image, (x, y))

def movement():
    global frame_index, frame_timer, animation_speed, prev_direction, bg_scroll, player_vel, landed
    keys = pygame.key.get_pressed()

    # Handle horizontal movement
    if keys[pygame.K_a] and not right_collision and not dead:
        bg_scroll += scroll_speed
        for rect, block_id in platforms:
            rect.x += scroll_speed
        prev_direction = 1
    if keys[pygame.K_d] and not left_collision and not dead:
        bg_scroll -= scroll_speed
        for rect, block_id in platforms:
            rect.x -= scroll_speed
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

def reset():
    global dead, death_jump, player_rect, bg_scroll
    player_rect.topleft = (200, 536) 
    dead = False
    death_jump = False
    for rect, block_id in platforms:
        rect.x -= bg_scroll
    player_vel = 0
    bg_scroll = 0


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

running = True
while running:
    # Draw all objects
    draw_objects()
    # Draw hearts
    draw_hearts(screen, player_health, max_health, heart_image)
    # Handle movement
    movement()
    # Handle collisions
    handle_collision()
    # Check if player is dead
    death()
    # Handle animations
    animations()

    keys = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    if keys[pygame.K_ESCAPE]:
        reset()

    if invincible and pygame.time.get_ticks() - iframe_timer >= IFRAME_DURATION:
        invincible = False

    # Save previous values before moving
    prev_bottom = player_rect.bottom
    prev_top = player_rect.top
    prev_left = player_rect.left
    prev_right = player_rect.right

    # Move player based on velocity
    player_rect.y += player_vel

    pygame.display.update()
    clock.tick(60)

pygame.quit()
exit()