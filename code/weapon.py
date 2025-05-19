import pygame
import os
from support import get_path

class Weapon(pygame.sprite.Sprite):
    def __init__(self, player, groups):
        super().__init__(groups)
        self.sprite_type = 'weapon'

        direction = player.status.split('_')[0]
        weapon_name = player.weapon
        weapon_path = f'graphics/weapons/{weapon_name}/{direction}.png'

        try:
            self.image = pygame.image.load(get_path(weapon_path)).convert_alpha()
        except FileNotFoundError:
            print(f"[Warning] Missing weapon sprite: {weapon_path}")
            self.image = pygame.Surface((32, 32), pygame.SRCALPHA)
            self.image.fill((255, 0, 255))  # Magenta placeholder

        if direction == 'right':
            self.rect = self.image.get_rect(midleft=player.rect.midright + pygame.math.Vector2(0, 16))
        elif direction == 'left':
            self.rect = self.image.get_rect(midright=player.rect.midleft + pygame.math.Vector2(0, 16))
        elif direction == 'down':
            self.rect = self.image.get_rect(midtop=player.rect.midbottom + pygame.math.Vector2(-10, 0))
        else:  # up
            self.rect = self.image.get_rect(midbottom=player.rect.midtop + pygame.math.Vector2(-10, 0))

        # Hackable Features (assumed weapon behavior)
        self.damage_multiplier = 1.0          # 1: Default damage multiplier
        self.attack_speed_boost = 1.0         # 2: Default attack speed (1.0 = normal)
        self.critical_hit_chance = 0.1        # 3: 10% chance for critical hits
        self.elemental_damage = 0             # 4: No elemental damage by default
        self.range_extension = 1.0            # 5: Default attack range
        self.projectile_speed = 5             # 6: Default speed for projectiles
        self.homing_projectiles = False       # 7: Projectiles don’t track enemies by default
        self.area_of_effect = 1.0             # 8: Default AoE radius
        self.invincibility_during_attack = False  # 9: No invincibility by default
        self.ammo = -1                        # 10: Infinite ammo (-1 = unlimited)
