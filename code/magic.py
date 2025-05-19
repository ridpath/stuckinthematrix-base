import pygame
from settings import *
from random import randint
from support import get_path

class MagicPlayer:
    def __init__(self, animation_player):
        self.animation_player = animation_player

        def safe_load_sound(path, default_volume=0.4):
            try:
                sound = pygame.mixer.Sound(get_path(path))
                sound.set_volume(default_volume)
                return sound
            except FileNotFoundError:
                print(f"Warning: Missing sound file: {path}")
                return None

        self.sounds = {
            'heal': safe_load_sound(magic_data['heal']['spell_sound'], 0.5),
            'flame': safe_load_sound(magic_data['flame']['spell_sound'], 0.4)
        }

        # Hackable Features
        self.mana_cost_reduction = 1.0      # 1: Default mana cost (1.0 = full cost)
        self.spell_power_boost = 1.0        # 2: Default spell strength
        self.cooldown_reduction = 1.0       # 3: Default cooldown (1.0 = normal)
        self.area_of_effect = 1.0           # 4: Default AoE multiplier
        self.duration_extension = 1.0       # 5: Default effect duration
        self.multi_target = False           # 6: Single target by default
        self.spell_chaining = False         # 7: No chaining by default
        self.mana_regen_boost = 1.0         # 8: Default mana regeneration
        self.spell_penetration = False      # 9: No resistance bypass by default
        self.instant_cast = False           # 10: Normal casting time

    def heal(self, player, strength, cost, groups):
        reduced_cost = cost * self.mana_cost_reduction
        if player.energy >= reduced_cost or self.instant_cast:
            if self.sounds['heal']:
                self.sounds['heal'].play()
            player.health += strength * self.spell_power_boost
            player.energy -= reduced_cost
            if player.health > player.stats['health']:
                player.health = player.stats['health']
            self.animation_player.create_particles('aura', player.rect.center, groups)
            self.animation_player.create_particles('heal', player.rect.center + pygame.math.Vector2(0, -20), groups)

    def flame(self, player, cost, groups):
        reduced_cost = cost * self.mana_cost_reduction
        if player.energy >= reduced_cost or self.instant_cast:
            player.energy -= reduced_cost
            if self.sounds['flame']:
                self.sounds['flame'].play()

            status = player.status.split('_')[0]
            direction = {
                'up': pygame.math.Vector2(0, -1),
                'down': pygame.math.Vector2(0, 1),
                'right': pygame.math.Vector2(1, 0),
                'left': pygame.math.Vector2(-1, 0)
            }.get(status, pygame.math.Vector2(-1, 0))

            # Apply area of effect and chaining
            range_multiplier = 6 * self.area_of_effect
            for i in range(1, int(range_multiplier)):
                if direction.x:
                    offset_x = (direction.x * i) * TILESIZE
                    x = player.rect.centerx + offset_x + randint(-TILESIZE // 3, TILESIZE // 3)
                    y = player.rect.centery + randint(-TILESIZE // 3, TILESIZE // 3)
                    self.animation_player.create_particles('flame', (x, y), groups)
                else:
                    offset_y = (direction.y * i) * TILESIZE
                    x = player.rect.centerx + randint(-TILESIZE // 3, TILESIZE // 3)
                    y = player.rect.centery + offset_y + randint(-TILESIZE // 3, TILESIZE // 3)
                    self.animation_player.create_particles('flame', (x, y), groups)
