import pygame
from settings import *

class Tile(pygame.sprite.Sprite):
    def __init__(self, pos, groups, sprite_type, surface=None):
        """
        Creates a tile at a given position.

        Args:
            pos (tuple): (x, y) pixel position.
            groups (list): Sprite groups to add this tile to.
            sprite_type (str): 'object', 'grass', 'invisible', etc.
            surface (pygame.Surface): Optional image surface for the tile.
        """
        super().__init__(groups)
        self.sprite_type = sprite_type

        # Default to an empty tile if no surface provided
        self.image = surface if surface else pygame.Surface((TILESIZE, TILESIZE))

        # Positioning and hitbox
        if sprite_type == 'object':
            self.rect = self.image.get_rect(topleft=(pos[0], pos[1] - TILESIZE))
        else:
            self.rect = self.image.get_rect(topleft=pos)

        y_offset = HITBOX_OFFSET.get(sprite_type, 0)
        self.hitbox = self.rect.inflate(-10, y_offset)
