import pygame
import time
from sys import exit

pygame.init()

info = pygame.display.Info()
SCREEN_WIDTH = 1500
SCREEN_HEIGHT = 900

screen = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))

clock = pygame.time.Clock()

# Setting up Background
sky_surf = pygame.image.load('Sprites/sky.png').convert()
sky_surf = pygame.transform.scale(sky_surf,(SCREEN_WIDTH,700))
ground_surf = pygame.image.load('Sprites/ground.png').convert()
ground_surf = pygame.transform.scale(ground_surf,(SCREEN_WIDTH,200))
ground_rect = ground_surf.get_rect()
ground_rect = pygame.Rect(0,700, SCREEN_WIDTH,200)

# Object Rects
player_rect = pygame.Rect(200,600,25,60)
platform1_rect = pygame.Rect(750,500,100,20)
platform2_rect = pygame.Rect(1200,600,100,20)

player_vel = 0
bg_scroll = 0
scroll_speed = 5

platforms = [ground_rect,platform1_rect,platform2_rect]
platforms_draw = [platform1_rect,platform2_rect]


landed = 0


while True:

    screen.fill((0,0,0))
    screen.blit(sky_surf, (bg_scroll % SCREEN_WIDTH - SCREEN_WIDTH, 0))
    screen.blit(sky_surf, (bg_scroll % SCREEN_WIDTH, 0))

    screen.blit(ground_surf, (bg_scroll % SCREEN_WIDTH - SCREEN_WIDTH, 700))
    screen.blit(ground_surf, (bg_scroll % SCREEN_WIDTH, 700))

    for platform in platforms_draw:
        pygame.draw.rect(screen,(255,255,255),platform)

    pygame.draw.rect(screen,(0,255,0),player_rect)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

    keys = pygame.key.get_pressed()
    if keys[pygame.K_a]:
        bg_scroll += scroll_speed
        # Adjust each platform to scroll with the background
        for platform in platforms:
            platform.x += scroll_speed
    if keys[pygame.K_d]:
        bg_scroll -= scroll_speed
        for platform in platforms:
            platform.x -= scroll_speed

    if keys[pygame.K_SPACE] and landed == 1:
        player_vel -= 20

    # Save previous values before moving
    prev_bottom = player_rect.bottom
    prev_top = player_rect.top

    # Move player with current velocity
    player_rect.y += player_vel

    is_on_platform = False

    # Check for collisions after movement
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

    # Apply gravity if not on a platform
    if is_on_platform:
        landed = 1
    else:
        player_vel += 0.75
        landed = 0



    pygame.display.update()
    clock.tick(60)
    


