import pygame
import json

# SETTINGS #
GRID_SIZE = 20
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800

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

pygame.init()

BLOCK_SLOT_START_X = 300
BLOCK_SLOTS = [
    pygame.Rect(BLOCK_SLOT_START_X + i * 60, SCREEN_HEIGHT - 80, 50, 50)
    for i in range(4)
]

LEFT_ARROW = pygame.Rect(BLOCK_SLOT_START_X - 40, SCREEN_HEIGHT - 75, 30, 30)
RIGHT_ARROW = pygame.Rect(BLOCK_SLOT_START_X + 4 * 60, SCREEN_HEIGHT - 75, 30, 30)

class Block(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h, block_id=0, color=(0, 255 ,0)):
        super().__init__()
        self.block_id = block_id  # store block type id
        self.image = pygame.Surface((w, h))
        self.image.fill(color)
        self.rect = self.image.get_rect(topleft=(x, y))

class LevelEditor:
    def __init__(self, block_width=20, block_height=20):
        self.blocks = pygame.sprite.Group()
        self.block_width = block_width
        self.block_height = block_height

        self.block_type_page = 0
        self.selected_index = 0

        self.mouse_down = False
        self.delete_mode = False

        self.scroll_x = 0  # Horizontal scroll in pixels


    def place_block(self, pos):
        x = ((pos[0] + self.scroll_x) // self.block_width) * self.block_width
        y = (pos[1] // self.block_height) * self.block_height

        if y + self.block_height > SCREEN_HEIGHT - 100:
            return

        for existing_block in self.blocks:
            if existing_block.rect.topleft == (x ,y):
                return

        block_id = self.block_type_page * 4 + self.selected_index
        color = BLOCK_TYPES.get(block_id, (100, 100, 100))
        block = Block(x, y, self.block_width, self.block_height, block_id, color)
        self.blocks.add(block)

    
    def remove_block(self, pos):
        for block in list(self.blocks):  # Convert to list to safely remove
            adj_pos = (pos[0] + self.scroll_x, pos[1])
            if block.rect.collidepoint(adj_pos):
                self.blocks.remove(block)

    def get_selected_block_color(self):
        block_id = self.block_type_page * 4 + self.selected_index
        return BLOCK_TYPES.get(block_id, (100, 100, 100))
                
    def draw(self, surface):
        for block in self.blocks:
            rect = block.rect.copy()
            rect.x -= self.scroll_x
            surface.blit(block.image, rect)


    def handle_event(self, event):
        pos = pygame.mouse.get_pos()

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 or event.button == 3:
                self.mouse_down = True
                self.delete_mode = (event.button == 3)

                if LEFT_ARROW.collidepoint(pos):
                    if self.block_type_page > 0:
                        self.block_type_page -= 1
                        self.selected_index = 0
                    return
                elif RIGHT_ARROW.collidepoint(pos):
                    max_page = (len(BLOCK_TYPES) - 1) // 4
                    if self.block_type_page < max_page:
                        self.block_type_page += 1
                        self.selected_index = 0
                    return
                for i, rect in enumerate(BLOCK_SLOTS):
                    if rect.collidepoint(pos):
                        self.selected_index = i
                        return

                if self.delete_mode:
                    self.remove_block(pos)
                else:
                    self.place_block(pos)

        elif event.type == pygame.MOUSEBUTTONUP:
            self.mouse_down = False

        elif event.type == pygame.MOUSEMOTION and self.mouse_down:
            if self.delete_mode:
                self.remove_block(pos)
            else:
                self.place_block(pos)

    def save_map(self, filename):
        data = []
        for block in self.blocks:
            # Save block_id and position
            data.append({
                'block_id': block.block_id,
                'x': block.rect.x,
                'y': block.rect.y
            })
        with open(filename, 'w') as f:
            json.dump(data, f)
        print(f"Map saved to {filename}")

    def load_map(self, filename):
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            self.blocks.empty()  # Clear existing blocks
            for item in data:
                block_id = item['block_id']
                x = item['x']
                y = item['y']
                color = BLOCK_TYPES.get(block_id, (100, 100, 100))
                block = Block(x, y, self.block_width, self.block_height, block_id, color)
                self.blocks.add(block)
            print(f"Map loaded from {filename}")
        except Exception as e:
            print(f"Failed to load map: {e}")

def drawGrid():
    for x in range(-editor.scroll_x % GRID_SIZE, SCREEN_WIDTH, GRID_SIZE):
        for y in range(0, SCREEN_HEIGHT - 100, GRID_SIZE):
            true_x = x + (editor.scroll_x // GRID_SIZE) * GRID_SIZE
            rect = pygame.Rect(true_x - editor.scroll_x, y, GRID_SIZE, GRID_SIZE)
            pygame.draw.rect(screen, (255, 255, 255), rect, 1)


def drawUI(editor):
    pygame.draw.rect(screen, (50, 50, 50), (0, SCREEN_HEIGHT - 100, SCREEN_WIDTH, 100))

    # Left arrow
    pygame.draw.polygon(screen, (200, 200, 200), [
        (LEFT_ARROW.centerx + 8, LEFT_ARROW.top),
        (LEFT_ARROW.centerx + 8, LEFT_ARROW.bottom),
        (LEFT_ARROW.centerx - 5, LEFT_ARROW.centery)
    ])
    pygame.draw.rect(screen, (200, 200, 200), LEFT_ARROW, 2)

    # Right arrow
    pygame.draw.polygon(screen, (200, 200, 200), [
        (RIGHT_ARROW.centerx - 8, RIGHT_ARROW.top),
        (RIGHT_ARROW.centerx - 8, RIGHT_ARROW.bottom),
        (RIGHT_ARROW.centerx + 5, RIGHT_ARROW.centery)
    ])
    pygame.draw.rect(screen, (200, 200, 200), RIGHT_ARROW, 2)

    # Block type slots
    for i, rect in enumerate(BLOCK_SLOTS):
        block_id = editor.block_type_page * 4 + i
        color = BLOCK_TYPES.get(block_id, (80, 80, 80))
        pygame.draw.rect(screen, color, rect)
        border_color = (255, 255, 255) if i == editor.selected_index else (180, 180, 180)
        pygame.draw.rect(screen, border_color, rect, 3)

# Init
clock = pygame.time.Clock()
screen = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
editor = LevelEditor()
mouse_pos = pygame.mouse.get_pos()

sky_surf = pygame.image.load('Sprites/sky.png')
sky_surf = pygame.transform.scale(sky_surf, (SCREEN_WIDTH, 600))
sky_width = sky_surf.get_width()

# Main loop
running = True
while running:
    for event in pygame.event.get():   
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_o:
                editor.save_map("my_level.json")
            elif event.key == pygame.K_l:
                editor.load_map("my_level.json")
            elif event.key == pygame.K_a:
                editor.scroll_x = max(0, editor.scroll_x - GRID_SIZE * 2)  # scroll left
            elif event.key == pygame.K_d:
                editor.scroll_x += GRID_SIZE * 2  # scroll right
        else:
            editor.handle_event(event)


    screen.fill((0, 0, 0))  
    bg_offset = editor.scroll_x % sky_width
    for i in range(-1, SCREEN_WIDTH // sky_width + 2):  # +2 ensures full coverage
        screen.blit(sky_surf, (i * sky_width - bg_offset, 0))

    drawGrid()
    editor.draw(screen)
    drawUI(editor)

    # Draw preview rect near cursor
    mouse_x, mouse_y = pygame.mouse.get_pos()
    preview_color = editor.get_selected_block_color()
    preview_rect = pygame.Rect(mouse_x + 10, mouse_y + 10, 10, 10)
    pygame.draw.rect(screen, preview_color, preview_rect)
    pygame.draw.rect(screen, (255, 255, 255), preview_rect, 1)  # white border

    pygame.display.flip()
    clock.tick(60)

