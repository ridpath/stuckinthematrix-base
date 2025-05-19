# -*- coding: utf-8 -*-
import pygame
import os
from settings import *
from support import get_path, import_folder
from entity import Entity
from random import random, randint

class Player(Entity):
    def to_dict(self):
        """Serialize player state for saving."""
        return {
            'pos': {'x': self.pos.x, 'y': self.pos.y},
            'health': self.health,
            'energy': self.energy,
            'exp': self.exp,
            'stats': dict(self.stats),
            'max_stats': dict(self.max_stats),
            'upgrade_cost': dict(self.upgrade_cost),
            'weapon_index': self.weapon_index,
            'magic_index': self.magic_index
        }

    def from_dict(self, data):
        """Load player state from saved data."""
        self.pos.x = data['pos']['x']
        self.pos.y = data['pos']['y']
        self.rect.center = (self.pos.x, self.pos.y)
        self.health = data['health']
        self.energy = data['energy']
        self.exp = data['exp']
        self.stats = dict(data['stats'])
        self.max_stats = dict(data['max_stats'])
        self.upgrade_cost = dict(data['upgrade_cost'])
        self.weapon_index = data['weapon_index']
        self.weapon = list(weapon_data.keys())[self.weapon_index]
        self.magic_index = data['magic_index']
        self.magic = list(magic_data.keys())[self.magic_index]

    def __init__(self, pos, groups, obstacle_sprites, create_attack, destroy_attack, create_magic):
        super().__init__(groups, pos, obstacle_sprites)
        player_path = get_path('graphics/test/player.png')
        self.image = pygame.image.load(player_path).convert_alpha()
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.inflate(-6, HITBOX_OFFSET['player'])
        self.import_player_assets()
        self.status = 'down'
        self.attacking = False
        self.attack_cooldown = 400
        self.attack_time = None
        self.pos = pygame.math.Vector2(self.rect.center)
        self.create_attack = create_attack
        self.destroy_attack = destroy_attack
        self.weapon_index = 0
        self.weapon = list(weapon_data.keys())[self.weapon_index]
        self.can_switch_weapon = True
        self.weapon_switch_time = None
        self.switch_duration_cooldown = 200
        self.create_magic = create_magic
        self.magic_index = 0
        self.magic = list(magic_data.keys())[self.magic_index]
        self.can_switch_magic = True
        self.magic_switch_time = None

        # Player stats
        self.stats = {
            'health': 100,
            'energy': 60,
            'attack': 10,
            'magic': 3,
            'speed': 300
        }
        self.max_stats = {
            'health': 300,
            'energy': 140,
            'attack': 20,
            'magic': 10,
            'speed': 720
        }
        self.upgrade_cost = {stat: 100 for stat in self.stats}
        self.health = self.stats['health']
        self.energy = self.stats['energy']
        self.speed = self.stats['speed']
        self.exp = 0
        self.vulnerable = True
        self.hurt_time = None
        self.invulnerability_duration = 500
        self.weapon_attack_sound = pygame.mixer.Sound(get_path('audio/sword.wav'))
        self.weapon_attack_sound.set_volume(0.2)

        # Hackable Features for Students
        self.infinite_health = False      # Never lose health
        self.one_hit_kill = False         # Kill enemies in one hit
        self.unlimited_energy = False     # Infinite magic energy
        self.speed_boost = False          # Double movement speed
        self.exp_multiplier = 1.0         # Faster XP gain
        self.god_mode = False             # Invincibility + one-hit kills
        self.teleport_enabled = False     # Teleport to target
        self.teleport_target = (100, 100) # Teleport coordinates (x, y)
        self.fast_attack = False          # Faster attack cooldown
        self.energy_regen_boost = False   # Faster energy regeneration
        self.max_stats_boost = False      # Maximize all stats
        self.can_wall_dash = False        # Dash through walls
        self.is_stealthy = False          # Invisible to enemies
        self.rage_mode = False            # Double damage output
        self.heal_on_hit = False          # Restore health when damaging enemies
        self.mana_on_hit = False          # Restore mana when damaging enemies
        self.life_steal = False           # Restore health on kill (requires enemy logic)
        self.critical_hit_chance = 0.0    # Chance for critical hits (0.0 to 1.0)
        self.dodge_ability = False        # Temporary invincibility and speed boost
        self.parry_ability = False        # Reflect enemy attacks (needs enemy logic)
        self.berserk_mode = False         # Double speed and damage temporarily
        self.stun_attack = False          # Attacks stun enemies (needs enemy logic)
        self.speed_burst = False          # Temporary movement speed increase
        self.shield_reflect = False       # Reflect projectiles (needs projectile logic)
        self.infinite_ammo = False        # No ammo limits for ranged attacks
        self.random_teleport = False      # Teleport to random map location
        self.double_damage = False        # Double all damage output
        self.invincibility_toggle = False # Toggle invincibility on/off

        # Timers for temporary effects
        self.berserk_time = 0
        self.berserk_duration = 5000  # 5 seconds
        self.speed_burst_time = 0
        self.speed_burst_duration = 2000  # 2 seconds
        self.dodge_time = 0
        self.dodge_duration = 1000  # 1 second

    def import_player_assets(self):
        """Load player animation sprites."""
        character_path = get_path('graphics/player')
        self.animations = {
            'up': [], 'down': [], 'left': [], 'right': [],
            'right_idle': [], 'left_idle': [], 'up_idle': [], 'down_idle': [],
            'right_attack': [], 'left_attack': [], 'up_attack': [], 'down_attack': []
        }
        for animation in self.animations.keys():
            full_path = os.path.join(character_path, animation)
            self.animations[animation] = import_folder(full_path)

    def input(self):
        """Handle player input for movement and actions."""
        if not self.attacking:
            keys = pygame.key.get_pressed()
            self.direction.y = keys[pygame.K_DOWN] - keys[pygame.K_UP]
            self.direction.x = keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]
            if self.direction.y < 0: self.status = 'up'
            elif self.direction.y > 0: self.status = 'down'
            elif self.direction.x > 0: self.status = 'right'
            elif self.direction.x < 0: self.status = 'left'
            if keys[pygame.K_SPACE]:
                self.attacking = True
                self.attack_time = pygame.time.get_ticks()
                self.create_attack()
                self.weapon_attack_sound.play()
                self.direction.x = self.direction.y = 0
            if keys[pygame.K_LCTRL]:
                self.attacking = True
                self.attack_time = pygame.time.get_ticks()
                style = list(magic_data.keys())[self.magic_index]
                strength = magic_data[style]['strength'] + self.stats['magic']
                cost = magic_data[style]['cost']
                self.create_magic(style, strength, cost)
                self.direction.x = self.direction.y = 0
            if keys[pygame.K_q] and self.can_switch_weapon:
                self.can_switch_weapon = False
                self.weapon_switch_time = pygame.time.get_ticks()
                self.weapon_index = (self.weapon_index + 1) % len(weapon_data)
                self.weapon = list(weapon_data.keys())[self.weapon_index]
            if keys[pygame.K_e] and self.can_switch_magic:
                self.can_switch_magic = False
                self.magic_switch_time = pygame.time.get_ticks()
                self.magic_index = (self.magic_index + 1) % len(magic_data)
                self.magic = list(magic_data.keys())[self.magic_index]
            # New feature inputs
            if keys[pygame.K_d] and self.dodge_ability:
                self.dodge_time = pygame.time.get_ticks()
            if keys[pygame.K_b] and self.berserk_mode:
                self.berserk_time = pygame.time.get_ticks()
            if keys[pygame.K_s] and self.speed_burst:
                self.speed_burst_time = pygame.time.get_ticks()
            if keys[pygame.K_t] and self.random_teleport:
                self.pos.x = randint(0, WIDTH)
                self.pos.y = randint(0, HEIGHT)
                self.rect.center = self.pos
                self.hitbox.center = self.pos
                self.random_teleport = False  # One-time use until reset

    def get_status(self):
        """Update player animation status based on movement and actions."""
        if self.direction.x == 0 and self.direction.y == 0:
            if 'idle' not in self.status and 'attack' not in self.status:
                self.status += '_idle'
        if self.attacking:
            if 'attack' not in self.status:
                self.status = self.status.replace('_idle', '') + '_attack'
        elif 'attack' in self.status:
            self.status = self.status.replace('_attack', '')

    def cooldowns(self):
        """Manage cooldowns for attacks and switches."""
        current_time = pygame.time.get_ticks()
        attack_cooldown = self.attack_cooldown // 2 if self.fast_attack else self.attack_cooldown
        if self.attacking and current_time - self.attack_time >= attack_cooldown + weapon_data[self.weapon]['cooldown']:
            self.attacking = False
            self.destroy_attack()
        if not self.can_switch_weapon and current_time - self.weapon_switch_time >= self.switch_duration_cooldown:
            self.can_switch_weapon = True
        if not self.can_switch_magic and current_time - self.magic_switch_time >= self.switch_duration_cooldown:
            self.can_switch_magic = True
        if not self.vulnerable and current_time - self.hurt_time >= self.invulnerability_duration:
            self.vulnerable = True

    def animate(self, dt):
        """Animate the player based on current status."""
        animation = self.animations[self.status]
        self.frame_index += self.animation_speed * dt
        if self.frame_index >= len(animation):
            self.frame_index = 0
        self.image = animation[int(self.frame_index)]
        self.rect = self.image.get_rect(center=self.hitbox.center)
        if not self.vulnerable:
            self.image.set_alpha(self.wave_value())
        else:
            self.image.set_alpha(255)

    def get_full_weapon_damage(self):
        """Calculate total weapon damage with new features."""
        base_damage = self.stats['attack'] + weapon_data[self.weapon]['damage']
        if self.rage_mode or (self.berserk_mode and pygame.time.get_ticks() - self.berserk_time < self.berserk_duration):
            base_damage *= 2
        if self.double_damage:
            base_damage *= 2
        if random() < self.critical_hit_chance:
            base_damage *= 2  # Critical hit doubles damage
        return base_damage

    def get_full_magic_damage(self):
        """Calculate total magic damage with new features."""
        base_damage = self.stats['magic'] + magic_data[self.magic]['strength']
        if self.rage_mode or (self.berserk_mode and pygame.time.get_ticks() - self.berserk_time < self.berserk_duration):
            base_damage *= 2
        if self.double_damage:
            base_damage *= 2
        if random() < self.critical_hit_chance:
            base_damage *= 2  # Critical hit doubles damage
        return base_damage

    def energy_cost(self, cost):
        """Handle energy cost for magic with infinite ammo support."""
        if self.infinite_ammo or self.unlimited_energy:
            return True
        if self.energy >= cost:
            self.energy -= cost
            return True
        return False

    def energy_recovery(self, dt):
        """Regenerate energy over time."""
        regen_rate = self.stats['magic'] * (2 if self.energy_regen_boost else 1)
        if self.energy < self.stats['energy']:
            self.energy += regen_rate * dt
        if self.energy > self.stats['energy']:
            self.energy = self.stats['energy']

    def collision(self, direction):
        if not self.can_wall_dash:  # Ignore collisions if wall_dash is active
            super().collision(direction)

    def update(self, dt):
        """Update player state each frame with new features."""
        if self.max_stats_boost:
            self.stats = dict(self.max_stats)
            self.health = self.stats['health']
            self.energy = self.stats['energy']
            self.speed = self.stats['speed']

        # Apply invincibility and infinite health
        if self.infinite_health or self.invincibility_toggle:
            self.health = self.stats['health']
            self.vulnerable = False

        # Heal on hit and mana on hit when attacking
        if self.attacking:
            if self.heal_on_hit:
                self.health = min(self.health + 5, self.stats['health'])
            if self.mana_on_hit:
                self.energy = min(self.energy + 5, self.stats['energy'])

        # Calculate speed with boosts
        speed = self.stats['speed']
        if self.speed_boost:
            speed *= 2
        if self.speed_burst and pygame.time.get_ticks() - self.speed_burst_time < self.speed_burst_duration:
            speed *= 1.5
        if self.dodge_ability and pygame.time.get_ticks() - self.dodge_time < self.dodge_duration:
            self.vulnerable = False
            speed *= 1.5
        if self.berserk_mode and pygame.time.get_ticks() - self.berserk_time < self.berserk_duration:
            speed *= 2

        self.input()
        self.cooldowns()
        self.get_status()
        self.animate(dt)
        self.move(speed, self.pos, dt)
        self.energy_recovery(dt)

        if self.god_mode:
            self.infinite_health = True
            self.one_hit_kill = True

        if self.teleport_enabled:
            self.pos = pygame.math.Vector2(self.teleport_target)
            self.rect.center = self.pos
            self.hitbox.center = self.pos
            self.teleport_enabled = False  # Reset after teleporting
