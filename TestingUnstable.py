import pygame
import threading
import tkinter as tk
import time
import random
from sys import exit

pygame.init()

# Screen setup
info = pygame.display.Info()
SCREEN_WIDTH = info.current_w
SCREEN_HEIGHT = info.current_h

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption('Game')

# Player and ground Y positions remain unchanged
GROUND_Y = SCREEN_HEIGHT - 150  # Adjust based on ground height
PLAYER_START_X = GROUND_Y
PLAYER_START_Y = GROUND_Y

# Settings variables
slider_x = 300  # Initial slider position
settings_active = False

clock = pygame.time.Clock()
score_timer = pygame.USEREVENT + 2
pygame.time.set_timer(score_timer, 1000)  # Trigger event every 1000ms (1 second)

# Game variables
allow_difficulty_decrease = False
game_active = True
menu_open = False
paused = False
freeze_start_time = 0
frozen = False
frozen_enemies = False  # Separate enemy freezing from the player
base_difficulty = 1

# Load images
sky_surf = pygame.image.load('Sprites/sky.png').convert()
ground_surf = pygame.image.load('Sprites/ground.png').convert()

#Scale sky and ground to fullscreen
sky_surf = pygame.transform.scale(sky_surf, (SCREEN_WIDTH, SCREEN_HEIGHT))
ground_surf = pygame.transform.scale(ground_surf, (SCREEN_WIDTH, 100))

# Score UI
score_font = pygame.font.SysFont('Consolas',40,1)
score = 0

# Gameover / Intro UI
player_stand = pygame.image.load('Sprites/player/player_stand.png').convert_alpha()
player_stand = pygame.transform.rotozoom(player_stand,0,2)
player_stand_rect = player_stand.get_rect(center = (400,200))

game_message = score_font.render('Press space to run',True,(111,196,169))
game_message_rect = game_message.get_rect(center = (400,330))

# Enemy setup
snail_surf = pygame.image.load('Sprites/snail/snail1.png').convert_alpha()
snail_rect = snail_surf.get_rect(midbottom=(700,300))
snail_mask = pygame.mask.from_surface(snail_surf)

fly_surf = pygame.image.load('Sprites/fly/fly1.png')
fly_mask = pygame.mask.from_surface(fly_surf)

obstacle_rect_list = []


# Player setup
player_surf = pygame.image.load('Sprites/player/player_walk_1.png').convert_alpha()
player_rect = player_surf.get_rect(midbottom=(80,GROUND_Y))
player_mask = pygame.mask.from_surface(player_surf)
player_gravity = 0

# Health bar setup
# Health bar setup
heart_surf = pygame.image.load('Sprites/heart.png').convert_alpha()
heart_surf = pygame.transform.rotozoom(heart_surf, 0, 2)  # Scale by 2x

HEART_SIZE = int(SCREEN_WIDTH * 0.03 * 1.75)
HEART_SPACING = HEART_SIZE * 0.15  # Reduce spacing (15% of heart size)

start_x = SCREEN_WIDTH - (HEART_SIZE * 3 + HEART_SPACING * 2) - 50  # Position first heart

heart_positions = [
    (start_x + i * (HEART_SIZE + HEART_SPACING), SCREEN_HEIGHT * 0.02)
    for i in range(3)
]



# Gameover effect setup
gameover_screen_vfx = pygame.Surface((SCREEN_WIDTH,SCREEN_HEIGHT))
gameover_screen_vfx.fill((0,0,0))
gameover_screen_vfx.set_alpha(80)

# Hurt effect setup
hurt_screen_vfx = pygame.Surface((SCREEN_WIDTH,SCREEN_HEIGHT))
hurt_screen_vfx.fill((200,0,20))
hurt_screen_vfx.set_alpha(160)

# Hurt variables
hurt_start_time = 0
hurting = False

# Heart status variables
health = 3
flashing = False
flash_start_time = 0
visible = True
flashing_index = None

# Collision Variables
collision = False
collision_time = 0
collision_immune = False

obstacle_timer = pygame.USEREVENT + 1
spawn_rate = 1800
pygame.time.set_timer(obstacle_timer,spawn_rate)
difficulty_multiplier = 1

ground_surf = pygame.transform.scale(ground_surf, (SCREEN_WIDTH, 150))



def open_settings():
    global settings_active, paused
    settings_active = not settings_active  # Toggle state
    paused = settings_active  # Pause game when settings is open


def draw_slider(screen, x, y, min_val, max_val, current_val):
    """ Draws a simple slider and allows interaction. """
    slider_width = 200
    slider_height = 10
    handle_radius = 10

    # Map value to slider position
    normalized_val = (current_val - min_val) / (max_val - min_val)
    handle_x = x + int(normalized_val * slider_width)

    # Draw slider bar
    pygame.draw.rect(screen, (100, 100, 100), (x, y, slider_width, slider_height))

    # Draw handle
    pygame.draw.circle(screen, (200, 50, 50), (handle_x, y + slider_height // 2), handle_radius)

    return x, y, slider_width, handle_x, min_val, max_val


def obstacle_movement(obstacle_list, difficulty_multiplier):
    global frozen_enemies, paused

    if paused:
        return obstacle_list  # Stop movement while paused

    if obstacle_list:
        for obstacle in obstacle_list:
            if not frozen_enemies:  # Stop movement if enemies are frozen
                obstacle['rect'].x -= int(4 * difficulty_multiplier)  # Move each obstacle left

            if obstacle['rect'].bottom == GROUND_Y:
                screen.blit(snail_surf, obstacle['rect'])
            else:
                screen.blit(fly_surf, obstacle['rect'])

        # Remove obstacles that move off-screen
        obstacle_list = [obstacle for obstacle in obstacle_list if obstacle['rect'].x > -100]

        return obstacle_list
    return []



def collisions(player_rect,player_mask,obstacles):
    for obstacle in obstacles:
        obstacle_rect = obstacle['rect']
        obstacle_mask = obstacle['mask']

        if player_rect.colliderect(obstacle_rect):
            offset_x = obstacle_rect.x - player_rect.x
            offset_y = obstacle_rect.y - player_rect.y

            if player_mask.overlap(obstacle_mask, (offset_x, offset_y)):
                return True
    return False
            

def display_score():
    score_surf = score_font.render(f'Score : {score}', True, (64, 64, 64))
    score_rect = score_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT * 0.05))  # 5% from top
    score_rect_outline = score_rect.inflate(20, 15)
    score_rect_background = score_rect.inflate(15, 10)
    pygame.draw.rect(screen, 'white', score_rect_background)
    pygame.draw.rect(screen, 'white', score_rect_outline, 5, 10)
    screen.blit(score_surf, score_rect)

def draw_hearts():
    """Draws hearts based on health and flashing state."""
    for i in range(3):
        if i < health:
            screen.blit(heart_surf, heart_positions[i])  # Normal hearts
        elif flashing and i == flashing_index and visible:
            screen.blit(heart_surf, heart_positions[i])  # Flashing heart

def handle_flashing(index=None):
    """Starts and updates flashing animation for the heart."""
    global flashing, flash_start_time, flashing_index, visible, health, last_toggle, score, difficulty_multiplier

    if index is not None and health > 0:  # Prevent health from going negative
        health -= 1
        if allow_difficulty_decrease:
            difficulty_multiplier = 1 + (score / 50)  # Adjust difficulty only if enabled
        
        flashing = True
        flash_start_time = pygame.time.get_ticks()
        last_toggle = flash_start_time  # Initialize toggle timer
        flashing_index = index
        visible = True
    
    if flashing:
        elapsed_time = pygame.time.get_ticks() - flash_start_time

        # Toggle visibility every 200ms
        if pygame.time.get_ticks() - last_toggle >= 100:
            visible = not visible
            last_toggle = pygame.time.get_ticks()

        # Stop flashing after set durations
        if health == 0 and elapsed_time >= 1500:
            flashing = False
            flashing_index = None
            visible = False  # Ensure heart disappears
        elif health > 0 and elapsed_time >= 1000:
            flashing = False
            flashing_index = None
            visible = True

def handle_hurt():
    """Handles taking damage, flashing, and freezing logic."""
    global collision, collision_time, collision_immune, hurt_start_time, hurting
    global frozen, freeze_start_time, frozen_enemies

    if collision and not collision_immune:
        if flashing_index is None and health > 0:
            handle_flashing(health - 1)  # Flash the heart being removed
        
        hurt_start_time = pygame.time.get_ticks()
        hurting = True
        collision_immune = True
        collision_time = pygame.time.get_ticks()

        # Freeze obstacles for 0.5 seconds
        frozen_enemies = True  # Freeze only enemies
        frozen = True  # Also freeze the player
        freeze_start_time = pygame.time.get_ticks()

        if health <= 1:  # If it's the last hit
            frozen_enemies = True  # Keep enemies frozen
            return  # Prevents the player from freezing
    
    # Update hurt effects
    if hurting:
        elapsed_hurt_time = pygame.time.get_ticks() - hurt_start_time
        if elapsed_hurt_time >= 250:
            hurting = False
        if hurting:
            screen.blit(hurt_screen_vfx, (0, 0))

last_spawn_rate = spawn_rate  
last_timer_update = pygame.time.get_ticks()
death_fall = False  # Tracks if the player is falling after death


# Game loop
while True:
    screen.blit(sky_surf, (0, 0))
    screen.blit(ground_surf, (0, GROUND_Y))


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                open_settings()  # Toggle settings menu
                
            if game_active and not paused:
                if event.key == pygame.K_SPACE and player_rect.bottom == GROUND_Y:
                    player_gravity = -18.5


        if event.type == score_timer and game_active and not paused:
            score += 1  # Increase score once per second

        if event.type == obstacle_timer and game_active and not paused:
            # Increase difficulty effect exponentially for a faster spawn rate increase
            adjusted_spawn_rate = max(300, spawn_rate / (difficulty_multiplier ** 1.3))  # Exponentially scale difficulty

            last_spawn_time = pygame.time.get_ticks()
            if last_spawn_time - last_timer_update >= adjusted_spawn_rate:
                last_timer_update = last_spawn_time  # Update last spawn time

                # Spawn the obstacle
            if random.randint(0, 1) == 0:  # 50% chance for snail
                obstacle_surf = snail_surf
                print("Spawning Snail")
                obstacle_rect = obstacle_surf.get_rect(midbottom=(random.randint(900, 1200), GROUND_Y))
            else:  # 50% chance for fly
                obstacle_surf = fly_surf
                print("Spawning Fly")
                obstacle_rect = obstacle_surf.get_rect(midbottom=(random.randint(900, 1200), GROUND_Y - 90))



            obstacle_mask = pygame.mask.from_surface(obstacle_surf)
            obstacle_rect_list.append({'rect': obstacle_rect, 'mask': obstacle_mask, 'surf': obstacle_surf})





        if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            game_active = True
            health = 3
            flashing = False
            flashing_index = None
            collision_immune = False
            collision_time = 0
            player_rect.midbottom = (80, 300)  # Reset player position
            score = 0
            death_fall = False
            difficulty_multiplier = 1
            frozen_enemies = False
            frozen = False
            player_gravity = 0.8  # Reset gravity
            hurting = False  # Stop any hurt effects
            obstacle_rect_list.clear()  # Clear all obstacles

            print("Game restarted!")


        if settings_active:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            mouse_pressed = pygame.mouse.get_pressed()[0]  # Left mouse button

            x, y, slider_width, handle_x, min_val, max_val = draw_slider(screen, 300, 200, 0.5, 2.0, base_difficulty)

            if mouse_pressed and (y - 10 <= mouse_y <= y + 20) and (300 <= mouse_x <= 500):
                normalized_val = (mouse_x - x) / slider_width
                base_difficulty = min_val + normalized_val * (max_val - min_val)




    if paused:
        screen.fill((50, 50, 50))  # Dark background for menu

        # Draw slider for difficulty
        draw_slider(screen, 280, 200, 0.5, 2.0, base_difficulty)

        # Display difficulty value
        difficulty_text = score_font.render(f"Base Difficulty: {base_difficulty:.2f}", True, (255, 255, 255))
        screen.blit(difficulty_text, (200, 250))

        pygame.display.flip()
        clock.tick(60)
        continue

    if frozen and (pygame.time.get_ticks() - freeze_start_time > 500 or health <= 0):
        frozen = False  # Unfreeze player
        frozen_enemies = False
        player_gravity = 0.8  # Restore gravity so they can move again


    if game_active == True:
        # Score management
        display_score()

        # Increase difficulty based on score
        difficulty_multiplier = base_difficulty * (1 + (score / (200 / base_difficulty)))

        obstacle_rect_list = obstacle_movement(obstacle_rect_list, difficulty_multiplier)

        # Update player physics
        if not frozen:
            if not game_active:
                player_gravity = min(player_gravity + 0.2, 3)  # Slower gravity, cap max fall speed
            else:
                player_gravity += 0.8  # Normal gravity when alive

            player_rect.y += player_gravity

        if player_rect.bottom >= GROUND_Y and not death_fall:  
            player_rect.bottom = GROUND_Y  # Only prevent falling when alive


        screen.blit(player_surf, player_rect)

        # Collision detection 
        collision = False
        collision = collisions(player_rect, player_mask, obstacle_rect_list)
        if collision and not collision_immune:
            handle_hurt
            print("Collision detected!")

        handle_flashing
        draw_hearts()

        # Reset collision immunity after 3 seconds
        if collision_immune and pygame.time.get_ticks() - collision_time > 2500:
            print("Resetting collision immunity!")
            collision_immune = False

        if health <= 0 and not death_fall:
            player_gravity = -13  # Give an initial jump impulse
            death_fall = True
            death_start_time = pygame.time.get_ticks()
            frozen = False  # Ensure the player is NOT frozen

        if death_fall:
            if pygame.time.get_ticks() - death_start_time > 250:  # Wait 250ms before applying gravity
                frozen = False  # Unfreeze player after initial jump
                player_gravity = min(player_gravity + 0.08, 10)  # Increase gravity
            player_rect.y += player_gravity  # Apply movement

            if player_rect.top > SCREEN_HEIGHT:  # If the player falls off-screen
                game_active = False  # End the game

    else:
        screen.blit(player_surf,player_rect)
        for obstacle in obstacle_rect_list:
            if obstacle['rect'].bottom == 300:
                screen.blit(snail_surf,obstacle['rect'])
            else:
                screen.blit(fly_surf, obstacle['rect'])
        update_hurt()
        update_flashing()
        draw_hearts()
        display_score()
        pygame.display.update()
    

    pygame.display.update()
    clock.tick(60)
