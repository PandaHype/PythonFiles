import json

# Use your game's Block class or whatever represents a level object.
def load_level_from_json(filename, block_class, block_group, block_width, block_height, block_types):
    """
    Load a level from a JSON file and populate a sprite group.

    :param filename: Path to the JSON level file.
    :param block_class: Class used to instantiate blocks.
    :param block_group: A pygame.sprite.Group() to add blocks to.
    :param block_width: Width of each block.
    :param block_height: Height of each block.
    :param block_types: Dictionary of block_id to color mapping.
    """
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
        for item in data:
            block_id = item['block_id']
            x = item['x']
            y = item['y']
            color = block_types.get(block_id, (100, 100, 100))
            block = block_class(x, y, block_width, block_height, block_id, color)
            block_group.add(block)
        print(f"Level loaded from {filename}")
    except Exception as e:
        print(f"Failed to load level: {e}")
