# -*- coding: utf-8 -*-
import pygame
import os
from settings import *
from tile import Tile
from player import Player
from support import get_path, import_csv_layout, import_folder
from random import choice, randint
from weapon import Weapon
from ui import UI
from enemy import Enemy
from particles import AnimationPlayer
from magic import MagicPlayer
from upgrade import Upgrade
import pygame.mixer

class Level:
    def get_savable_state(self):
        defeated_enemies = []
        destroyed_grass = []
        for sprite in self.attackable_sprites:
            if hasattr(sprite, 'sprite_type'):
                if sprite.sprite_type == 'enemy' and not sprite.alive():
                    defeated_enemies.append({'x': sprite.rect.x, 'y': sprite.rect.y})
                if sprite.sprite_type == 'grass' and not sprite.alive():
                    destroyed_grass.append({'x': sprite.rect.x, 'y': sprite.rect.y})
        return {
            'player': self.player.to_dict(),
            'defeated_enemies': defeated_enemies,
            'destroyed_grass': destroyed_grass
        }

    def __init__(self, map_id, player=None, loaded_data=None, player_spawn_pos=None, on_transition=None):
        self.display_surface = pygame.display.get_surface()
        self.game_paused = False
        self.game_over = False

        self.visible_sprites = YSortCameraGroup()
        self.obstacle_sprites = pygame.sprite.Group()
        self.current_attack = None
        self.attack_sprites = pygame.sprite.Group()
        self.attackable_sprites = pygame.sprite.Group()

        self.player = player
        self._player_spawn_pos = player_spawn_pos
        self.on_transition = on_transition

        self.transition_points = {}
        self._last_transition_tile = None

        original_image = pygame.image.load(get_path('graphics/objects/red_pill_tile.png')).convert_alpha()
        self.red_pill_surf = pygame.transform.scale(original_image, (TILESIZE, TILESIZE))

        self.red_pill_sound = pygame.mixer.Sound(get_path('audio/red_pill.wav'))
        self.red_pill_sound.set_volume(0.7)

        self.endscene_sound = pygame.mixer.Sound(get_path('audio/endscene.wav'))
        self.endscene_sound.set_volume(0.7)

        self.death_sound = pygame.mixer.Sound(get_path('audio/death.wav'))
        self.death_sound.set_volume(0.6)

        self.create_map(map_id, loaded_data)

        self.ui = UI()
        self.upgrade = Upgrade(self.player)
        self.animation_player = AnimationPlayer()
        self.magic_player = MagicPlayer(self.animation_player)

        # Hackable Features
        self.invulnerable = False
        self.infinite_mana = False
        self.super_speed = False
        self.one_hit_ko = False
        self.xp_multiplier = 1.0
        self.god_mode = False
        self.teleport = False
        self.teleport_target = (100, 100)
        self.fast_attack = False
        self.energy_regen_boost = False
        self.max_stats = False
        self.time_stopped = False

        try:
            self.font = pygame.font.Font(get_path('font/joystix.ttf'), 36)
        except FileNotFoundError:
            self.font = pygame.font.SysFont('consolas', 36)

    def create_map(self, map_id, loaded_data=None):
        TRANSITION_CODE_MAP = {
            '9000': {'target_map_id': 'test', 'target_spawn': (4*TILESIZE, 4*TILESIZE)},
            '9001': {'target_map_id': 'default', 'target_spawn': (27*TILESIZE, 6*TILESIZE)},
            '9002': {'target_map_id': 'island', 'target_spawn': (4*TILESIZE, 4*TILESIZE)},
            '9003': {'target_map_id': 'test', 'target_spawn': (8*TILESIZE, 5*TILESIZE)},
            '9004': {'target_map_id': 'island2', 'target_spawn': (4*TILESIZE, 4*TILESIZE)}
        }

        def map_file(layer):
            if map_id == 'default':
                return f"data/map/map_{layer}.csv"
            return f"data/map/map_{map_id}_{layer}.csv"

        layouts = {
            'boundary': import_csv_layout(map_file('FloorBlocks')),
            'grass': import_csv_layout(map_file('Grass')),
            'object': import_csv_layout(map_file('Objects')),
            'entities': import_csv_layout(map_file('Entities')),
        }

        graphics = {
            'grass': import_folder('graphics/grass'),
            'objects': import_folder('graphics/objects'),
        }

        from pathfinding_utils import build_grid
        self.pathfinding_grid = None

        for style, layout in layouts.items():
            for row_idx, row in enumerate(layout):
                for col_idx, col in enumerate(row):
                    if col != '-1':
                        x = col_idx * TILESIZE
                        y = row_idx * TILESIZE

                        if style == 'boundary':
                            Tile((x, y), [self.obstacle_sprites], 'invisible')

                        if style == 'grass':
                            destroyed = False
                            if loaded_data and 'destroyed_grass' in loaded_data:
                                destroyed = any(g['x'] == x and g['y'] == y for g in loaded_data['destroyed_grass'])
                            if not destroyed:
                                random_grass_image = choice(graphics['grass'])
                                Tile((x, y), [self.visible_sprites, self.obstacle_sprites, self.attackable_sprites], 'grass', random_grass_image)

                        if style == 'object':
                            surf = graphics['objects'][int(col)]
                            Tile((x, y), [self.visible_sprites, self.obstacle_sprites], 'object', surf)

        self.pathfinding_grid = build_grid(WIDTH, HEIGHT, TILESIZE, self.obstacle_sprites)

        entities_layout = layouts['entities']
        for row_idx, row in enumerate(entities_layout):
            for col_idx, col in enumerate(row):
                if col != '-1':
                    x = col_idx * TILESIZE
                    y = row_idx * TILESIZE
                    if col in TRANSITION_CODE_MAP:
                        self.transition_points[(x, y)] = TRANSITION_CODE_MAP[col]
                        Tile((x, y), [self.visible_sprites], 'object', self.red_pill_surf)
                        continue
                    if col == '394':
                        if self.player is None:
                            spawn_pos = (x, y) if self._player_spawn_pos is None else self._player_spawn_pos
                            self.player = Player(spawn_pos, [self.visible_sprites], self.obstacle_sprites, self.create_attack, self.destroy_attack, self.create_magic)
                            if loaded_data and 'player' in loaded_data:
                                self.player.from_dict(loaded_data['player'])
                        else:
                            if self._player_spawn_pos is not None:
                                self.player.pos.x, self.player.pos.y = self._player_spawn_pos
                                self.player.rect.center = self._player_spawn_pos
                                self.player.hitbox.center = self._player_spawn_pos
                            self.player.obstacle_sprites = self.obstacle_sprites
                            self.player.create_attack = self.create_attack
                            self.player.destroy_attack = self.destroy_attack
                            self.player.create_magic = self.create_magic
                            self.visible_sprites.add(self.player)
                        self.initial_spawn_pos = (self.player.pos.x, self.player.pos.y)
                    else:
                        defeated = False
                        if loaded_data and 'defeated_enemies' in loaded_data:
                            defeated = any(e['x'] == x and e['y'] == y for e in loaded_data['defeated_enemies'])
                        if not defeated:
                            monster_name = {
                                '390': 'bamboo',
                                '391': 'spirit',
                                '392': 'raccoon'
                            }.get(col, 'squid')
                            Enemy(monster_name, (x, y), [self.visible_sprites, self.attackable_sprites],
                                  self.obstacle_sprites, self.damage_player, self.trigger_death_particles,
                                  self.add_exp, lambda ep, pp, ea=0: self.trigger_exp_particles(ep, pp, ea),
                                  pathfinding_grid=self.pathfinding_grid, tile_size=TILESIZE, level=self)

    def trigger_exp_particles(self, enemy_pos, player_pos, exp_amount=0):
        animation_type = 'exp_orb' if 'exp_orb' in self.animation_player.frames else 'sparkle'
        self.animation_player.create_exp_particles(enemy_pos, player_pos, self.visible_sprites, amount=5, exp_amount=exp_amount)

    def check_transition(self):
        px = int(self.player.rect.centerx // TILESIZE) * TILESIZE
        py = int(self.player.rect.centery // TILESIZE) * TILESIZE
        for (tx, ty), data in self.transition_points.items():
            if abs(px - tx) < TILESIZE // 2 and abs(py - ty) < TILESIZE // 2:
                if self._last_transition_tile != (tx, ty):
                    self._last_transition_tile = (tx, ty)
                    if hasattr(self, 'red_pill_sound'):
                        self.red_pill_sound.play()
                    if hasattr(self, 'endscene_sound'):
                        pygame.time.set_timer(pygame.USEREVENT + 1, 1200)
                    if self.on_transition:
                        self.on_transition(data['target_map_id'], data['target_spawn'])
                    return True
                else:
                    return False
        self._last_transition_tile = None
        return False

    def create_attack(self):
        self.current_attack = Weapon(self.player, [self.visible_sprites, self.attack_sprites])

    def create_magic(self, style, strength, cost):
        if self.infinite_mana or self.god_mode:
            cost = 0
        if style == 'heal':
            self.magic_player.heal(self.player, strength, cost, [self.visible_sprites])
        elif style == 'flame':
            self.magic_player.flame(self.player, cost, [self.visible_sprites, self.attack_sprites])

    def destroy_attack(self):
        if self.current_attack:
            self.current_attack.kill()
        self.current_attack = None

    def create_explosion(self, pos, radius, damage):
        """Handles explosion effect when an enemy with explode_on_death dies."""
        for sprite in self.attackable_sprites:
            if sprite.sprite_type == 'enemy':
                distance = (pygame.math.Vector2(sprite.rect.center) - pygame.math.Vector2(pos)).magnitude()
                if distance <= radius:
                    sprite.health -= damage
                    if sprite.health <= 0:
                        sprite.check_death()

    def player_attack_logic(self):
        for attack_sprite in self.attack_sprites:
            collisions = pygame.sprite.spritecollide(attack_sprite, self.attackable_sprites, False)
            for target in collisions:
                if target.sprite_type == 'grass':
                    pos = target.rect.center
                    offset = pygame.math.Vector2(0, 75)
                    for _ in range(randint(3, 6)):
                        self.animation_player.create_grass_particles(pos - offset, [self.visible_sprites])
                    target.kill()
                else:
                    if self.one_hit_ko or self.god_mode:
                        target.health = 0
                    else:
                        target.get_damage(self.player, attack_sprite.sprite_type)
                    if target.health <= 0:
                        if getattr(self.player, 'life_steal', False):
                            self.player.health = min(self.player.health + 10, self.player.stats['health'])
                        target.check_death()

    def damage_player(self, amount, attack_type):
        if self.player.vulnerable and not (self.invulnerable or self.god_mode):
            print(f"Player took {amount} damage from {attack_type}")
            self.player.health -= amount
            self.player.vulnerable = False
            self.player.hurt_time = pygame.time.get_ticks()
            self.animation_player.create_particles(attack_type, self.player.rect.center, [self.visible_sprites])
            if self.player.health <= 0:
                self.death_sound.play()
                self.game_over = True
                print("Player died!")

    def draw_game_over(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.display_surface.blit(overlay, (0, 0))
        text = self.font.render("Game Over - Press R to Restart", True, (255, 0, 0))
        text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        self.display_surface.blit(text, text_rect)

    def restart_game(self):
        self.game_over = False
        self.player.health = self.player.stats['health']
        if hasattr(self, 'initial_spawn_pos'):
            self.player.pos.x, self.player.pos.y = self.initial_spawn_pos
        else:
            self.player.pos.x, self.player.pos.y = self._player_spawn_pos or (WIDTH // 2, HEIGHT // 2)
        self.player.rect.center = self.player.pos
        self.player.hitbox.center = self.player.pos
        self.player.vulnerable = True
        print("Game restarted!")

    def trigger_death_particles(self, pos, particle_type):
        self.animation_player.create_particles(particle_type, pos, self.visible_sprites)

    def add_exp(self, amount):
        self.player.exp += amount * self.xp_multiplier

    def toggle_menu(self):
        self.game_paused = not self.game_paused
        if self.game_paused:
            from save_manager import save_game
            if pygame.key.get_pressed()[pygame.K_p]:
                save_game(self.get_savable_state())
                print("Game saved!")

    def run(self, dt):
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if self.game_over and event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                self.restart_game()

        if self.game_over:
            self.visible_sprites.custom_draw(self.player)
            self.ui.display(self.player)
            self.draw_game_over()
        else:
            if self.super_speed:
                self.player.speed = 600
            if self.teleport:
                self.player.pos = pygame.math.Vector2(self.teleport_target)
                self.player.rect.center = self.player.pos
                self.player.hitbox.center = self.player.pos
                self.teleport = False
            if self.energy_regen_boost:
                self.player.energy += 1
            if self.max_stats:
                for stat in self.player.stats:
                    self.player.stats[stat] = self.player.max_stats[stat]
            if self.fast_attack:
                self.player.attack_cooldown = 100

            self.visible_sprites.custom_draw(self.player)
            self.ui.display(self.player)

            if self.game_paused:
                self.upgrade.display()
            else:
                if self.time_stopped:
                    self.player.update(dt)
                else:
                    self.visible_sprites.update(dt)
                    self.visible_sprites.enemy_update(self.player)
                self.player_attack_logic()
                self.check_transition()

        if self.invulnerable and not self.god_mode:
            print("Cheat detected: Invulnerability without God Mode!")
            self.player.health -= 10

class YSortCameraGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.half_width = self.display_surface.get_width() // 2
        self.half_height = self.display_surface.get_height() // 2
        self.offset = pygame.math.Vector2()

        floor_path = get_path('graphics/tilemap/ground.png')
        self.floor_surf = pygame.image.load(floor_path).convert()
        self.floor_rect = self.floor_surf.get_rect(topleft=(0, 0))

    def custom_draw(self, player):
        self.offset.x = player.rect.centerx - self.half_width
        self.offset.y = player.rect.centery - self.half_height
        self.display_surface.blit(self.floor_surf, self.floor_rect.topleft - self.offset)

        for sprite in sorted(self.sprites(), key=lambda s: s.rect.centery):
            offset_rect = sprite.rect.topleft - self.offset
            self.display_surface.blit(sprite.image, offset_rect)

    def enemy_update(self, player):
        for sprite in self.sprites():
            if getattr(sprite, 'sprite_type', None) == 'enemy':
                sprite.enemy_update(player)
