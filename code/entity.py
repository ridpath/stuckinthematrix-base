import pygame
from math import sin
from support import get_path

# Base class for all simulated entities inside the Matrix
class Entity(pygame.sprite.Sprite):
    def __init__(self, groups, pos, obstacle_sprites=None):
        super().__init__(groups)
        self.frame_index = 0
        self.animation_speed = 4
        self.direction = pygame.math.Vector2()
        self.pos = pygame.math.Vector2(pos)

        # Will be initialized later by subclass after setting self.image and self.rect
        self.hitbox = None
        self.rect = None

        # Assign obstacle sprites if provided
        self.obstacle_sprites = obstacle_sprites or pygame.sprite.Group()

    # Movement update per frame
    def move(self, speed, pos, dt):
        self.pos = pos

        if self.direction.magnitude() != 0:
            self.direction = self.direction.normalize()

        # horizontal vector
        self.pos.x += self.direction.x * speed * dt
        self.hitbox.centerx = round(self.pos.x)
        self.rect.centerx = self.hitbox.centerx
        self.collision('horizontal')

        # vertical vector
        self.pos.y += self.direction.y * speed * dt
        self.hitbox.centery = round(self.pos.y)
        self.rect.centery = self.hitbox.centery
        self.collision('vertical')

    # Collision with environment layers
    def collision(self, direction):
        for sprite in self.obstacle_sprites.sprites():
            if hasattr(sprite, 'hitbox') and sprite.hitbox.colliderect(self.hitbox):
                if direction == 'horizontal':
                    if self.direction.x > 0:  # right
                        self.hitbox.right = sprite.hitbox.left
                    elif self.direction.x < 0:  # left
                        self.hitbox.left = sprite.hitbox.right
                    self.rect.centerx = self.hitbox.centerx
                    self.pos.x = self.hitbox.centerx

                elif direction == 'vertical':
                    if self.direction.y < 0:  # up
                        self.hitbox.top = sprite.hitbox.bottom
                    elif self.direction.y > 0:  # down
                        self.hitbox.bottom = sprite.hitbox.top
                    self.rect.centery = self.hitbox.centery
                    self.pos.y = self.hitbox.centery

    # Used for flicker effects when vulnerable (simulation glitch flicker)
    def wave_value(self):
        value = sin(pygame.time.get_ticks())
        return 255 if value >= 0 else 0
