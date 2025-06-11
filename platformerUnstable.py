import pygame
import math
from Block import Block
from LevelLoader import load_level_from_json
from sys import exit

pygame.init()

class Player:
    def __init__(self):
        self.rect = pygame.Rect(250, 600, 55, 64)
        self.frame_index = 0
        self.frame_timer = 0
        self.animation_speed = 20
        self.health = 3
        self.max_health = 3
        self.invincible = False
        self.iframe_timer = 0
        self.IFRAME_DURATION = 750
        self.vel = 0
        self.dead = False
        self.death_jump = False
        self.prev_direction = 0
        self.left_collision = False
        self.right_collision = False
        self.landed = 0
        self.knockback_x = 0
        self.knockback_freeze_timer = 0
        self.freeze_duration = 400
    def is_frozen(self):
        if self.knockback_freeze_timer == 0:
            return False  # not frozen

        if pygame.time.get_ticks() - self.knockback_freeze_timer >= self.freeze_duration:
            self.knockback_freeze_timer = 0
            return False  # freeze expired

        return True  # still frozen

BLOCK_TYPES = {
    0: (0, 255, 0),     # Green block (Grass block)
    1: (255, 0, 0),     # Red block (Damage block)
    2: (0, 0, 255),     # Blue block (Water block)
    3: (0, 0, 0),       # Black block (Void block)
    4: (175, 75, 0),   # Orange block
    5: (255, 128, 0),
    6: (128, 0, 255),
    7: (0, 255, 255),
}

info = pygame.display.Info()
SCREEN_WIDTH = 1600
SCREEN_HEIGHT = 800
SCROLL_LEFT = 300
SCROLL_RIGHT = 300

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Setup Clock for FPS management
clock = pygame.time.Clock()

# Setting up Background
sky_surf = pygame.image.load('Sprites/sky.png').convert()
sky_surf = pygame.transform.scale(sky_surf, (SCREEN_WIDTH, 600))

# Setting up Hearts
heart_image = pygame.image.load('Sprites/heart.png').convert_alpha()
heart_image = pygame.transform.scale(heart_image, (40, 40))  # Resize if needed

 
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
GRID_SIZE = 20

prev_bottom = 0
prev_top = 0
prev_left = 0
prev_right = 0

# Store player facing directon [1 = Left, 0 = Right]
prev_direction = 0

player = Player()

blocks = pygame.sprite.Group()
load_level_from_json('my_level.json', Block, blocks, 20, 20, BLOCK_TYPES)

platforms = [
    (block.rect.copy(), block.block_id)  # .copy() avoids modifying the original rect
    for block in blocks
]

red_unions = []
handled = set()

def find_connected_blocks():
    for rect, block_id in platforms:
        if block_id == 1:
            collisions = [rect]
        
            for other, block_id in platforms:
                if rect != other and rect.colliderect(other):
                    collisions.append(other)

            if len(collisions) > 1:
                union_rect = pygame.Rect.unionall(collisions)
                red_unions.append(union_rect)
            else:
                red_unions.append(rect)         

find_connected_blocks()

def apply_damage_with_knockback(collision_rect):
    if player.health > 0:
        player.health -= 1
        player.invincible = True
        player.iframe_timer = pygame.time.get_ticks()
        player.knockback_freeze_timer = pygame.time.get_ticks()

        # Calculate vector from block center to player center
        player_center = player.rect.center
        block_center = collision_rect.center

        dx = player_center[0] - block_center[0]
        dy = player_center[1] - block_center[1]

        dist = math.hypot(dx, dy)
        if dist == 0:
            dist = 1  # avoid division by zero

        knockback_strength = 15

        # Normalize direction
        knockback_x = (dx / dist) * knockback_strength
        knockback_y = (dy / dist) * knockback_strength

        knockback_x = round(knockback_x, 0)
        knockback_y = round(knockback_y, 0)
        player.knockback_x = knockback_x
        player.vel = -abs(knockback_y)  # always knock upward or as you prefer

def handle_collision():
    global player_vel, landed, current_time
    # Check for collisions after vertical movement
    for rect, block_id in platforms:
        if player.rect.colliderect(rect):
            if player_vel >= 0 and prev_bottom <= rect.top:
                # Landed on top
                player.rect.bottom = rect.top
                player.vel = 0
                landed = True
                current_time = pygame.time.get_ticks()
                if block_id == 1:
                    if not player.invincible:
                        if player.health > 0:
                            player.invincible = True
                            player.iframe_timer = current_time
                            apply_damage_with_knockback(rect)
            elif player_vel <= 0 and prev_top >= rect.bottom:
                # Hit from below
                player.rect.top = rect.bottom
                player.vel = 0
                current_time = pygame.time.get_ticks()
                if block_id == 1:
                    if not player.invincible:
                        if player.health > 0:
                            player.invincible = True
                            player.iframe_timer = current_time
                            apply_damage_with_knockback(rect)

    # Check for side collisions (left and right) to prevent scrolling
    player.left_collision = False
    player.right_collision = False
    for rect, block_id in platforms:
        if player.rect.colliderect(rect):
            if prev_right > rect.left and prev_left < rect.left:
                # Collided from the left
                player.left_collision = True
                player.rect.right = rect.left
                current_time = pygame.time.get_ticks()
                if block_id == 1:
                    for damage_rect in red_unions:
                        if not player.invincible:
                            if player.health > 0:
                                player.invincible = True
                                player.iframe_timer = current_time
                                apply_damage_with_knockback(damage_rect)
                break
            if prev_left < rect.right and prev_right > rect.right:
                # Collided from the right
                player.right_collision = True
                player.rect.left = rect.right
                current_time = pygame.time.get_ticks()
                if block_id == 1:
                    if not player.invincible:
                        if player.health > 0:
                            player.invincible = True
                            player.iframe_timer = current_time
                            apply_damage_with_knockback(rect)
                break

def draw_objects():
    global DEBUG
    screen.fill((0, 0, 0))
    parallax_scroll = bg_scroll * 0.5  # slower background scroll for parallax
    screen.blit(sky_surf, (parallax_scroll % SCREEN_WIDTH - SCREEN_WIDTH, 0))
    screen.blit(sky_surf, (parallax_scroll % SCREEN_WIDTH, 0))


    for rect, block_id in platforms:
            color = BLOCK_TYPES.get(block_id, (255, 255, 255)) # Fallback color
            pygame.draw.rect(screen, color, rect)

    if DEBUG:
        pygame.draw.rect(screen, (0, 255, 0), player.rect)

def draw_hearts(screen, health, heart_image):
    for i in range(player.max_health):
        if i < health:
            x = 1200 + i * 50  # 50 px gap
            y = 50
            screen.blit(heart_image, (x, y))

def movement():
    global frame_index, frame_timer, animation_speed, prev_direction, bg_scroll, player_vel, landed
    keys = pygame.key.get_pressed()

    world_movement = 0

    if keys[pygame.K_a] and not player.right_collision and not player.dead and not player.is_frozen():
        player.rect.x -= scroll_speed
        prev_direction = 1

    if keys[pygame.K_d] and not player.left_collision and not player.dead and not player.is_frozen():
        player.rect.x += scroll_speed
        prev_direction = 0

    # Camera follows only when player goes past scroll zone
    if player.rect.x < SCROLL_LEFT:
        world_movement = SCROLL_LEFT - player.rect.x
        player.rect.x = SCROLL_LEFT
    elif player.rect.x > SCROLL_RIGHT:
        world_movement = SCROLL_RIGHT - player.rect.x
        player.rect.x = SCROLL_RIGHT

    # Apply world scroll to platforms and background
    bg_scroll += world_movement
    for rect, block_id in platforms:
        rect.x += world_movement

    if keys[pygame.K_SPACE] and landed == 1 and not player.is_frozen():
        player.vel -= 20

    # Apply gravity if not on a platform
    if player.vel < 15:
        player.vel += 0.75
    landed = 0
    frame_timer += 1

def death():
    global player_vel
    if player.rect.bottom >= 900 or player.health == 0:
        player.dead = True
    if player.dead == True and not player.death_jump:
        player.vel = -20
        player.death_jump = True

def reset():
    global bg_scroll
    player.rect.topleft = (200, 536) 
    player.dead = False
    player.death_jump = False
    for rect, block_id in platforms:
        rect.x -= bg_scroll
    player.health = 3
    player.vel = 0
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
        screen.blit(current_image_right,player.rect.topleft)
        prev_direction = 0
    if keys[pygame.K_a] and not keys[pygame.K_d]:
        screen.blit(current_image_left,player.rect.topleft)
        prev_direction = 1
    if prev_direction == 0 and not keys[pygame.K_d]:
        screen.blit(player_sprite_right[0],player.rect.topleft)
    elif prev_direction == 1 and not keys[pygame.K_a]:
        screen.blit(player_sprite_left[0],player.rect.topleft)
    elif prev_direction == 0 and keys[pygame.K_a] and keys[pygame.K_d]:
        screen.blit(player_sprite_right[0],player.rect.topleft)

running = True
while running:
    # Draw all objects
    draw_objects()
    # Draw hearts
    draw_hearts(screen, player.health, heart_image)
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

    if player.invincible and pygame.time.get_ticks() - player.iframe_timer >= player.IFRAME_DURATION:
        player.invincible = False

    # Save previous values before moving
    prev_bottom = player.rect.bottom
    prev_top = player.rect.top
    prev_left = player.rect.left
    prev_right = player.rect.right

    # Move player based on velocity
    player.rect.x += player.knockback_x
    player.rect.y += player.vel

    if player.knockback_x > 0:
        player.knockback_x -= 1
    if player.knockback_x < 0:
        player.knockback_x += 1
    

    pygame.display.update()
    clock.tick(60)

pygame.quit()
exit()