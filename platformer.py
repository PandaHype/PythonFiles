import pygame
import json
from sys import exit

pygame.init()

# Setting up Clock for FPS management
clock = pygame.time.Clock()

# Screen dimensions
SCREEN_WIDTH = 1600
SCREEN_HEIGHT = 800

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Setting up background
sky_surf = pygame.image.load('Sprites/sky.png').convert()
sky_surf = pygame.transform.scale(sky_surf, (SCREEN_WIDTH, 600))

# List player sprites to animate
player_sprite_right = [pygame.image.load('Sprites/player/sprite_1right.png').convert_alpha(),
                       pygame.image.load('Sprites/player/sprite_2right.png').convert_alpha()]
player_sprite_left = [pygame.image.load('Sprites/player/sprite_1left.png').convert_alpha(),
                      pygame.image.load('Sprites/player/sprite_2left.png').convert_alpha()]

# Player variables
frame_index = 0
frame_timer = 0
animation_speed = 20
player_vel = 0
landed = 0
prev_bottom = 0
prev_top = 0
prev_left = 0
prev_right = 0
left_collision = False
right_collision = False

# Store player facing directon [1 = Left, 0 = Right]
prev_direction = 0

# Background variables
BG_SCROLL = 0
SCROLL_SPEED = 5
SCROLL_THRESH = 400  # Pixels from the left edge
LEFT_SCROLL_THRESH = 200  # Pixels from the left edge before scrolling left starts

# Define block types
BLOCK_TYPES = {
    0: {'color': (0, 255, 0), 'collidable': True},    # Green block (collidable)
    1: {'color': (255, 0, 0), 'collidable': True},    # Red block (collidable)
    2: {'color': (0, 0, 255), 'collidable': False},   # Blue block (non-collidable)
    3: {'color': (0, 0, 0), 'collidable': False},     # Black block (non-collidable)
}

class Block:
    WIDTH = 20
    HEIGHT = 20

    def __init__(self, x, y, block_id):
        self.rect = pygame.Rect(x, y, Block.WIDTH, Block.HEIGHT)
        self.block_id = block_id
        block_info = BLOCK_TYPES.get(block_id, {'color': (100, 100, 100), 'collidable': False})
        self.color = block_info['color']
        self.collidable = block_info['collidable']

    def draw(self, surface, scroll_x=0, scroll_y=0):
        # Adjust for scrolling if needed
        draw_rect = self.rect.move(-scroll_x, -scroll_y)
        pygame.draw.rect(surface, self.color, draw_rect)

    def check_collision(self, other_rect):
        if not self.collidable:
            return False
        return self.rect.colliderect(other_rect)

class Player:
    def __init__(self, x, y, sprites_right, sprites_left):
        self.rect = pygame.Rect(x, y, 55, 64)  # adjust size as needed
        self.vel = pygame.Vector2(0, 0)
        self.speed = 5
        self.jump_strength = -12
        self.on_ground = False

        self.gravity = 0.5
        self.max_fall_speed = 10

        self.sprites_right = sprites_right
        self.sprites_left = sprites_left
        self.frame_index = 0
        self.frame_timer = 0
        self.animation_speed = 15
        self.prev_direction = 0

    def handle_input(self):
        keys = pygame.key.get_pressed()
        self.vel.x = 0

        if keys[pygame.K_a]:
            self.vel.x = -self.speed
            self.prev_direction = 1  # left
        if keys[pygame.K_d]:
            self.vel.x = self.speed
            self.prev_direction = 0  # right
        if keys[pygame.K_w] and self.on_ground:
            self.vel.y = self.jump_strength
            self.on_ground = False

    def apply_gravity(self):
        self.vel.y += self.gravity
        if self.vel.y > self.max_fall_speed:
            self.vel.y = self.max_fall_speed

    def move(self, blocks):
        # Horizontal
        self.rect.x += self.vel.x
        for block in blocks:
            if block.collidable and self.rect.colliderect(block.rect):
                if self.vel.x > 0:  # Moving right
                    self.rect.right = block.rect.left
                elif self.vel.x < 0:  # Moving left
                    self.rect.left = block.rect.right

        # Prevent player from walking off screen to the left (using rect.left and BG_SCROLL)
        if self.rect.left < BG_SCROLL:
            self.rect.left = BG_SCROLL

        # Vertical
        self.rect.y += self.vel.y
        self.on_ground = False
        for block in blocks:
            if block.collidable and self.rect.colliderect(block.rect):
                if self.vel.y > 0:  # Falling
                    self.rect.bottom = block.rect.top
                    self.vel.y = 0
                    self.on_ground = True
                elif self.vel.y < 0:  # Jumping
                    self.rect.top = block.rect.bottom
                    self.vel.y = 0

    def update_animation(self):
        self.frame_timer += 1
        if self.frame_timer >= self.animation_speed:
            self.frame_index = (self.frame_index + 1) % len(self.sprites_right)
            self.frame_timer = 0

    def update(self, blocks):
        self.handle_input()
        self.apply_gravity()
        self.move(blocks)
        self.update_animation()

    def draw(self, surface, scroll_x):
        if self.vel.x < 0:
            image = self.sprites_left[self.frame_index]
        elif self.vel.x > 0:
            image = self.sprites_right[self.frame_index]
        else:
            image = self.sprites_left[0] if self.prev_direction else self.sprites_right[0]

        surface.blit(image, (self.rect.x - scroll_x, self.rect.y))

def load_blocks_from_json(filename):
    blocks = []
    with open(filename, 'r') as f:
        data = json.load(f)
        for item in data:
            block = Block(item['x'], item['y'], item['block_id'])
            blocks.append(block)
    return blocks

def draw_scene():
    screen.fill((0, 0, 0))

    # Draw scrolling background, if needed
    screen.blit(sky_surf, (-(BG_SCROLL % SCREEN_WIDTH), 0))
    screen.blit(sky_surf, (SCREEN_WIDTH - (BG_SCROLL % SCREEN_WIDTH), 0))

    # Draw blocks/platforms
    for block in blocks:
        block.draw(screen, BG_SCROLL)

    # Draw player
    player.draw(screen, BG_SCROLL)

# Setting up Player
player = Player(100, 300, player_sprite_right, player_sprite_left)

blocks = load_blocks_from_json('my_level.json')

running = True
frame_timer = 0
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Update player input and physics
    player.handle_input()
    player.apply_gravity()
    player.move(blocks)

    # Scroll right
    if player.rect.x - BG_SCROLL > SCROLL_THRESH:
        BG_SCROLL = player.rect.x - SCROLL_THRESH
    # Scroll left
    elif player.rect.x - BG_SCROLL < LEFT_SCROLL_THRESH:
        BG_SCROLL = player.rect.x - LEFT_SCROLL_THRESH

    # Prevent negative scroll
    BG_SCROLL = max(0, BG_SCROLL)

    # Prevent player from moving past left edge of visible screen
    if player.rect.left < BG_SCROLL:
        player.rect.left = BG_SCROLL

    # Update animation
    player.update_animation()

    # Draw everything
    draw_scene()
    pygame.display.flip()

    frame_timer += 1
    clock.tick(60)

pygame.quit()
exit()
