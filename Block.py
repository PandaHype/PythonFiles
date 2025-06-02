import pygame

class Block(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h, block_id=0, color=(0, 255, 0)):
        super().__init__()
        self.block_id = block_id
        self.image = pygame.Surface((w, h))
        self.image.fill(color)
        self.rect = self.image.get_rect(topleft=(x, y))
