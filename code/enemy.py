import pygame
import os
from settings import *
from support import import_folder, get_path
from entity import Entity
from pathfinding_utils import astar, pos_to_grid, grid_to_pos

class Enemy(Entity):
    def __init__(self, monster_name, pos, groups, obstacle_sprites, damage_player,
                 trigger_death_particles, add_exp, trigger_exp_particles=None,
                 pathfinding_grid=None, tile_size=None, level=None):
        super().__init__(groups, pos, obstacle_sprites)

        self.sprite_type = 'enemy'
        self.monster_name = monster_name
        self.import_graphics(monster_name)
        self.status = 'idle'

        default_surface = pygame.Surface((32, 32), pygame.SRCALPHA)
        default_surface.fill((255, 0, 0))  # Red error square

        idle_frames = self.animations.get(self.status, [])
        self.image = idle_frames[0] if idle_frames else default_surface
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.inflate(0, -10)
        self.pos = pygame.math.Vector2(self.rect.center)

        monster_info = monster_data.get(self.monster_name, {})
        self.health = monster_info.get('health', 100)
        self.exp = monster_info.get('exp', 50)
        self.speed = monster_info.get('speed', 100)
        self.attack_damage = monster_info.get('damage', 10)
        self.resistance = monster_info.get('resistance', 1)
        self.attack_radius = monster_info.get('attack_radius', 50)
        self.notice_radius = monster_info.get('notice_radius', 200)
        self.attack_type = monster_info.get('attack_type', 'slash')

        self.can_attack = True
        self.attack_time = None
        self.attack_cooldown = 400
        self.damage_player = damage_player
        self.trigger_death_particles = trigger_death_particles
        self.add_exp = add_exp
        self.trigger_exp_particles = trigger_exp_particles
        self.last_player_pos = None

        self.vulnerable = True
        self.hit_time = None
        self.invisibility_duration = 300

        try:
            attack_sfx = monster_info.get('attack_sound', get_path('audio/sword.wav'))
            self.attack_sound = pygame.mixer.Sound(attack_sfx)
        except:
            self.attack_sound = pygame.mixer.Sound(get_path('audio/sword.wav'))

        self.hit_sound = pygame.mixer.Sound(get_path('audio/hit.wav'))
        self.death_sound = pygame.mixer.Sound(get_path('audio/death.wav'))

        self.hit_sound.set_volume(0.6)
        self.death_sound.set_volume(0.6)
        self.attack_sound.set_volume(0.3)

        self.pathfinding_grid = pathfinding_grid
        self.tile_size = tile_size
        self.path = []
        self.last_path_time = 0
        self.path_recalc_interval = 500
        self._last_player_grid = None
        self.level = level  # Reference to the level for explosion effects

        # Hackable Features (Existing)
        self.health_reduction = 1.0
        self.damage_reduction = 1.0
        self.speed_reduction = 1.0
        self.aggro_range_reduction = 1.0
        self.loot_drop_increase = 1.0
        self.xp_boost = 1.0
        self.stun_duration_increase = 1.0
        self.knockback_effect = False
        self.fear_effect = False
        self.pacifist_mode = False
        self.flees_from_player = False

        # New Hackable Features
        self.explode_on_death = False  # Triggers explosion on death
        self.regenerate = False        # Enables health regeneration
        self.regen_rate = 0.1          # Health regained per second
        self.swarm = False             # Enables swarm behavior
        self.stunned = False           # Indicates if enemy is stunned
        self.stun_duration = 0         # Duration of stun in milliseconds
        self.stun_time = None          # Time when stun was applied

    def import_graphics(self, name):
        self.animations = {'idle': [], 'move': [], 'attack': []}
        base_path = get_path(f'graphics/monsters/{name}')
        for anim in self.animations.keys():
            full_path = os.path.join(base_path, anim)
            if os.path.exists(full_path):
                self.animations[anim] = import_folder(full_path)

    def get_player_distance_direction(self, player):
        enemy_vec = pygame.math.Vector2(self.rect.center)
        player_vec = pygame.math.Vector2(player.rect.center)
        distance = (player_vec - enemy_vec).magnitude()
        direction = (player_vec - enemy_vec).normalize() if distance > 0 else pygame.math.Vector2()
        if getattr(player, 'is_stealthy', False) and distance > self.attack_radius:
            return float('inf'), pygame.math.Vector2()
        return distance, direction

    def get_status(self, player):
        if self.stunned:
            self.status = 'idle'  # Use 'idle' or add a 'stunned' animation if available
            return
        distance, _ = self.get_player_distance_direction(player)
        reduced_notice_radius = self.notice_radius * self.aggro_range_reduction
        if distance <= self.attack_radius and self.can_attack and not self.pacifist_mode:
            if self.status != 'attack':
                self.frame_index = 0
            self.status = 'attack'
        elif distance <= reduced_notice_radius:
            self.status = 'move'
        else:
            self.status = 'idle'
        if self.status != 'move' or self.fear_effect:
            self.path = []

    def actions(self, player):
        if self.stunned:
            self.direction = pygame.math.Vector2()
            return
        now = pygame.time.get_ticks()
        if self.status == 'attack' and not self.pacifist_mode:
            self.attack_time = now
            self.damage_player(self.attack_damage * self.damage_reduction, self.attack_type)
            self.attack_sound.play()
        elif self.status == 'move':
            if self.flees_from_player or self.fear_effect:
                self.direction = -self.get_player_distance_direction(player)[1]
            elif self.swarm:
                # Swarm behavior: Move toward average position of nearby enemies
                nearby_enemies = [
                    e for e in self.level.attackable_sprites
                    if e.sprite_type == 'enemy' and e != self and
                    (pygame.math.Vector2(e.rect.center) - pygame.math.Vector2(self.rect.center)).magnitude() < 200
                ]
                if nearby_enemies:
                    avg_pos = sum((pygame.math.Vector2(e.rect.center) for e in nearby_enemies), pygame.math.Vector2()) / len(nearby_enemies)
                    self.direction = (avg_pos - pygame.math.Vector2(self.rect.center)).normalize() if (avg_pos - pygame.math.Vector2(self.rect.center)).magnitude() > 0 else pygame.math.Vector2()
                else:
                    self.direction = self.get_player_distance_direction(player)[1]
            else:
                recalc = (
                    not self.path or
                    now - self.last_path_time > self.path_recalc_interval or
                    self._last_player_grid != pos_to_grid(player.rect.center, self.tile_size)
                )
                if recalc and self.pathfinding_grid is not None:
                    start = pos_to_grid(self.rect.center, self.tile_size)
                    goal = pos_to_grid(player.rect.center, self.tile_size)
                    self._last_player_grid = goal
                    path = astar(self.pathfinding_grid, start, goal)
                    self.path = path[1:] if path and len(path) > 1 else []
                    self.last_path_time = now
                if self.path:
                    next_node = self.path[0]
                    next_pos = grid_to_pos(next_node, self.tile_size)
                    vec_to_next = pygame.math.Vector2(next_pos) - pygame.math.Vector2(self.rect.center)
                    if vec_to_next.length() < 4:
                        self.path.pop(0)
                    self.direction = vec_to_next.normalize() if vec_to_next.length() > 0 else pygame.math.Vector2()
                else:
                    self.direction = self.get_player_distance_direction(player)[1]
        else:
            self.direction = pygame.math.Vector2()

    def animate(self, dt):
        animation = self.animations.get(self.status, [])
        if not animation:
            return
        self.frame_index += self.animation_speed * dt
        if self.frame_index >= len(animation):
            if self.status == 'attack':
                self.can_attack = False
            self.frame_index = 0
        self.image = animation[int(self.frame_index)]
        if not self.vulnerable:
            self.image.set_alpha(self.wave_value())
        else:
            self.image.set_alpha(255)

    def cooldown(self):
        current_time = pygame.time.get_ticks()
        if not self.can_attack and current_time - self.attack_time >= self.attack_cooldown:
            self.can_attack = True
        if not self.vulnerable and current_time - self.hit_time >= (self.invisibility_duration * self.stun_duration_increase):
            self.vulnerable = True
        if self.stunned and current_time - self.stun_time >= self.stun_duration:
            self.stunned = False

    def get_damage(self, player, attack_type):
        if self.vulnerable:
            self.hit_sound.play()
            self.direction = self.get_player_distance_direction(player)[1]
            dmg = player.get_full_weapon_damage() if attack_type == 'weapon' else player.get_full_magic_damage()
            self.health -= dmg * self.health_reduction
            self.hit_time = pygame.time.get_ticks()
            self.vulnerable = False
            if self.knockback_effect:
                self.direction *= 2
            if getattr(player, 'stun_attack', False):
                self.stunned = True
                self.stun_time = pygame.time.get_ticks()
                self.stun_duration = 1000  # 1 second stun

    def check_death(self):
        if self.health <= 0:
            self.kill()
            self.trigger_death_particles(self.rect.center, self.monster_name)
            self.add_exp(self.exp * self.xp_boost)
            if self.trigger_exp_particles and self.last_player_pos:
                self.trigger_exp_particles(self.rect.center, self.last_player_pos, self.exp)
            self.death_sound.play()
            if self.explode_on_death and self.level:
                self.level.create_explosion(self.rect.center, 100, 20)  # Explosion with radius 100, damage 20

    def hit_reaction(self):
        if not self.vulnerable:
            self.direction *= -self.resistance

    def update(self, dt):
        if self.regenerate:
            self.health = min(self.health + self.regen_rate * dt, monster_data[self.monster_name].get('health', 100))
        self.hit_reaction()
        self.move(self.speed * self.speed_reduction, self.pos, dt)
        self.animate(dt)
        self.cooldown()
        self.check_death()

    def enemy_update(self, player):
        self.get_status(player)
        self.actions(player)
        self.last_player_pos = player.rect.center
