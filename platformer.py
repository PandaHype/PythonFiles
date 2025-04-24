import pygame
import time
import os
from sys import exit

pygame.init()

# Setup screen
SCREEN_WIDTH = 1500
SCREEN_HEIGHT = 900

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Setup clock for fps management
clock = pygame.time.Clock()

# Setting up Background
sky_surf = pygame.image.load('Game Developing/Sprites/sky.png').convert()
sky_surf = pygame.transform.scale(sky_surf, (SCREEN_WIDTH, 700))
ground_surf = pygame.image.load('Game Developing/Sprites/ground.png').convert()
ground_surf = pygame.transform.scale(ground_surf, (SCREEN_WIDTH, 200))
ground_rect = ground_surf.get_rect()
ground_rect = pygame.Rect(0, 700, SCREEN_WIDTH, 200)

# Object Rects
player_rect = pygame.Rect(200, 600, 50, 60)
platform1_rect = pygame.Rect(750, 680, 100, 20)
platform2_rect = pygame.Rect(1200, 600, 100, 20)
platform3_rect = pygame.Rect(1500, 400, 100, 20)

# Put player sprites in list for anims
player_sprite = [pygame.image.load('Game Developing/Sprites/player/sprite_1.png').convert_alpha(),
                                   pygame.image.load('Game Developing/Sprites/player/sprite_2.png').convert_alpha()]

# Anim variables
frame_index = 0
frame_timer = 0
animation_speed = 30

# General variables
landed = 0
player_vel = 0
bg_scroll = 0
scroll_speed = 5
left_collision = False
right_collision = False
collision_ground = False
death = False
death_jump = False

# Platform listing
platforms = [ground_rect, platform1_rect, platform2_rect, platform3_rect]
platforms_draw = [platform1_rect, platform2_rect, platform3_rect]



while True:
    
    screen.fill((0, 0, 0))
    screen.blit(sky_surf, (bg_scroll % SCREEN_WIDTH - SCREEN_WIDTH, 0))
    screen.blit(sky_surf, (bg_scroll % SCREEN_WIDTH, 0))

    screen.blit(ground_surf, (bg_scroll % SCREEN_WIDTH - SCREEN_WIDTH, 700))
    screen.blit(ground_surf, (bg_scroll % SCREEN_WIDTH, 700))

    # Draw all platforms other than ground
    for platform in platforms_draw:
        pygame.draw.rect(screen, (255, 255, 255), platform)

    pygame.draw.rect(screen, (0, 255, 0), player_rect)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

    keys = pygame.key.get_pressed()

    # Save previous values before moving
    prev_bottom = player_rect.bottom
    prev_top = player_rect.top
    prev_left = player_rect.left
    prev_right = player_rect.right

    # Handle horizontal movement
    if keys[pygame.K_a] and not right_collision and not death:
        bg_scroll += scroll_speed
        for platform in platforms:
            platform.x += scroll_speed
    if keys[pygame.K_d] and not left_collision and not death:
        bg_scroll -= scroll_speed
        for platform in platforms:
            platform.x -= scroll_speed
    if keys[pygame.K_SPACE] and landed == 1:
        player_vel -= 20

    # Move ground to prevent falling off. [DEBUG], DISABLE FOR ACTUAL GAME!
    ground_rect.x = player_rect.x

    # Handle walking anim
    if frame_timer >= animation_speed:
        frame_index = (frame_index + 1) % len(player_sprite)
        frame_timer = 0
    
    current_image = player_sprite[frame_index]
    if keys[pygame.K_d]:
        screen.blit(current_image,player_rect.topleft)
    else:
        screen.blit(player_sprite[0],player_rect.topleft)

    # Move player with current velocity
    player_rect.y += player_vel

    is_on_platform = False

    # Check for collisions after vertical movement
    for platform in platforms:
        if player_rect.colliderect(platform):
            if player_vel >= 0 and prev_bottom <= platform.top:
                # Landed on top
                player_rect.bottom = platform.top
                player_vel = 0
                is_on_platform = True
            elif player_vel < 0 and prev_top >= platform.bottom:
                # Hit from below
                player_rect.top = platform.bottom
                player_vel = 0
            if player_rect.colliderect(ground_rect):
                collision_ground = True
            
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
    
    # Handle death jump anim
    if player_rect.bottom >= 900:
        death = True
    
    if death == True and death_jump == False:
        player_vel = -30
        death_jump = True
        

    # Apply gravity if not on a platform
    if is_on_platform:
        landed = 1
    else:
        if player_vel < 20:
            player_vel += 0.75
        landed = 0

    # Increase timer to track anim stage
    frame_timer += 1


    pygame.display.update()
    clock.tick(60)