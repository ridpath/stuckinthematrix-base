# -*- coding: utf-8 -*-
import pygame
import sys
import time
import os
import pygame.mixer
from settings import *
from level import Level
from support import get_path
from save_manager import load_game, save_game
from random import randint, choice

class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        pygame.display.set_caption('Stuck in the Matrix')
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()

        self.current_map_id = 'default'
        self.player = None
        self.show_save_dialog = os.path.exists('savegame.json')
        self.save_dialog_result = None
        self.save_message_time = None

        # Hackable Features (142 features for students to discover and manipulate)
        # Player Stats and Abilities
        self.infinite_health = False            # Never lose health
        self.infinite_mana = False              # Unlimited mana for spells
        self.one_hit_ko = False                 # Instant enemy kills
        self.fast_attack = False                # Faster attack speed
        self.super_speed = False                # Increased movement speed
        self.high_jump = False                  # Increased jump height
        self.invisibility = False               # Invisible to enemies
        self.god_mode = False                   # Invulnerability + one-hit kills
        self.unlimited_ammo = False             # Infinite ammo for ranged attacks
        self.instant_cast = False               # No casting time for spells
        self.max_stats = False                  # Maximize all player stats
        self.regeneration = False               # Passive health regeneration
        self.shield = False                     # Temporary shield
        self.double_jump = False                # Allow double jumping
        self.dash_ability = False               # Enable dash ability
        self.wall_climb = False                 # Allow climbing walls
        self.flight = False                     # Enable flying
        self.water_breathing = False            # Breathe underwater
        self.fire_resistance = False            # Resistance to fire damage
        self.poison_immunity = False            # Immunity to poison
        self.heal_on_hit = False                # Restore health when damaging enemies
        self.mana_on_hit = False                # Restore mana when damaging enemies
        self.life_steal = False                 # Restore health on kill
        self.critical_hit_chance = 0.0          # Chance for critical hits (0.0 to 1.0)
        self.dodge_ability = False              # Temporary invincibility and speed boost
        self.parry_ability = False              # Reflect enemy attacks
        self.berserk_mode = False               # Double speed and damage temporarily
        self.stun_attack = False                # Attacks stun enemies
        self.speed_burst = False                # Temporary movement speed increase
        self.shield_reflect = False             # Reflect projectiles with shield
        self.random_teleport = False            # Teleport to random map location
        self.double_damage = False              # Double all damage output
        self.invincibility_toggle = False       # Toggle invincibility on/off

        # Game Mechanics
        self.game_speed = 1.0                   # Game speed multiplier
        self.xp_multiplier = 1.0                # Multiplies XP gained
        self.no_cooldown = False                # No spell/weapon cooldowns
        self.free_upgrades = False              # Upgrades cost no XP
        self.time_freeze = False                # Pause enemy updates
        self.instant_transition = False         # Skip fade animations
        self.unlimited_saves = False            # Save without restrictions
        self.no_clip = False                    # Walk through obstacles
        self.teleport_enabled = False           # Teleport to coordinates
        self.teleport_target = (100, 100)       # Target coordinates for teleport
        self.perma_death = False                # Enable permanent death
        self.hardcore_mode = False              # Increased difficulty
        self.peaceful_mode = False              # No enemies spawn
        self.infinite_resources = False         # Unlimited crafting resources
        self.fast_travel = False                # Enable fast travel
        self.auto_save = False                  # Automatic saving
        self.manual_save_only = False           # Only manual saves allowed
        self.time_limit = False                 # Add a time limit
        self.score_multiplier = 1.0             # Multiplies score gained
        self.extra_lives = 0                    # Additional lives

        # Enemy Behaviors
        self.enemy_spawn_rate = 1.0             # Enemy spawn rate multiplier
        self.enemy_health_reduction = 1.0       # Enemy health multiplier
        self.enemy_damage_reduction = 1.0       # Enemy damage multiplier
        self.enemy_speed_reduction = 1.0        # Enemy speed multiplier
        self.enemy_aggro_range_reduction = 1.0  # Enemy notice radius multiplier
        self.pacifist_enemies = False           # Enemies don’t attack
        self.fear_enemies = False               # Enemies flee from player
        self.increased_loot = False             # Higher loot drop rates
        self.xp_boost = 1.0                     # Multiplies XP from enemies
        self.stun_enemies = False               # Enemies are stunned
        self.health_reduction = 1.0             # Enemy health multiplier (alternative)
        self.damage_reduction = 1.0             # Enemy damage multiplier (alternative)
        self.speed_reduction = 1.0              # Enemy speed multiplier (alternative)
        self.aggro_range_reduction = 1.0        # Enemy notice radius multiplier (alternative)
        self.loot_drop_increase = 1.0           # Loot drop rate multiplier
        self.stun_duration_increase = 1.0       # Stun duration multiplier
        self.knockback_effect = False           # Enable knockback on hit
        self.fear_effect = False                # Enemies fear player
        self.flees_from_player = False          # Enemies flee from player
        self.explode_on_death = False           # Enemies explode on death
        self.regenerate = False                 # Enemies regenerate health
        self.regen_rate = 0.1                   # Health regeneration rate per second
        self.swarm = False                      # Enemies swarm together

        # UI and Visuals
        self.debug_mode = False                 # Show debug info
        self.show_hitboxes = False              # Display hitboxes
        self.fullbright = False                 # Disable lighting effects
        self.custom_fov = 1.0                   # Field of view multiplier
        self.hud_visible = True                 # Show HUD elements
        self.minimap_enabled = False            # Display minimap
        self.custom_cursor = False              # Use a custom cursor
        self.screen_shake = True                # Enable screen shake effects
        self.particle_effects = True            # Enable particle effects
        self.fog_of_war = False                 # Enable fog of war

        # Audio
        self.mute_music = False                 # Mute background music
        self.mute_sounds = False                # Mute sound effects
        self.custom_volume = 1.0                # Custom volume level
        self.ambient_sounds = True              # Enable ambient sounds
        self.footstep_sounds = True             # Enable footstep sounds
        self.combat_music = False               # Play special combat music
        self.sound_spatialization = False       # Enable 3D sound effects
        self.echo_effects = False               # Add echo to sounds
        self.pitch_shift = 1.0                  # Alter sound pitch
        self.reverb = False                     # Add reverb to sounds

        # Visual Effects
        self.bloom = False                      # Enable bloom effect
        self.motion_blur = False                # Enable motion blur
        self.color_grading = False              # Apply color grading
        self.vignette = False                   # Add vignette effect
        self.chromatic_aberration = False       # Enable chromatic aberration
        self.depth_of_field = False             # Enable depth of field
        self.anti_aliasing = True               # Enable anti-aliasing
        self.shadows = True                     # Enable dynamic shadows
        self.reflections = False                # Enable reflections
        self.ambient_occlusion = False          # Enable ambient occlusion

        # Economy and Trading
        self.infinite_money = False             # Unlimited currency
        self.discounts = False                  # Reduced prices in shops
        self.free_items = False                 # Items are free
        self.rare_item_drop = False             # Increased rare item drops
        self.crafting_boost = False             # Faster crafting times
        self.smelting_boost = False             # Faster smelting times
        self.farming_boost = False              # Faster crop growth
        self.mining_boost = False               # Faster mining
        self.fishing_boost = False              # Faster fishing
        self.trading_boost = False              # Better trade deals

        # Miscellaneous
        self.custom_gravity = 1.0               # Alter gravity strength
        self.weather_control = False            # Control weather effects
        self.time_of_day_control = False        # Control time of day
        self.npc_interaction_boost = False      # NPCs are more friendly
        self.pet_companion = False              # Spawn a pet companion
        self.mount_available = False            # Enable mounts
        self.vehicle_available = False          # Enable vehicles
        self.build_mode = False                 # Enable building mode
        self.survival_mode = False              # Enable survival mechanics
        self.creative_mode = False              # Enable creative mode

        # Weapon Features
        self.damage_multiplier = 1.0            # Weapon damage multiplier
        self.attack_speed_boost = 1.0           # Weapon attack speed multiplier
        self.elemental_damage = 0               # Additional elemental damage
        self.range_extension = 1.0              # Attack range multiplier
        self.projectile_speed = 5               # Speed of projectiles
        self.homing_projectiles = False         # Projectiles track enemies
        self.area_of_effect_weapon = 1.0        # Area of effect radius for weapons
        self.invincibility_during_attack = False# Invincibility during attacks
        self.ammo = -1                          # Ammo count (-1 = unlimited)

        # Magic Features
        self.mana_cost_reduction = 1.0          # Mana cost multiplier
        self.spell_power_boost = 1.0            # Spell strength multiplier
        self.cooldown_reduction = 1.0           # Spell cooldown multiplier
        self.area_of_effect_magic = 1.0         # Area of effect multiplier for spells
        self.duration_extension = 1.0           # Spell effect duration multiplier
        self.multi_target = False               # Spells hit multiple targets
        self.spell_chaining = False             # Spells chain to nearby targets
        self.mana_regen_boost = 1.0             # Mana regeneration multiplier
        self.spell_penetration = False          # Spells bypass resistances

        self.play_background_music()

        loaded_data = None
        if loaded_data and 'player' in loaded_data:
            self.level = Level(self.current_map_id, player=None, loaded_data=loaded_data, on_transition=self.handle_transition)
        else:
            self.level = Level(self.current_map_id, player=self.player, loaded_data=None, on_transition=self.handle_transition)
        self.player = self.level.player

    def play_background_music(self):
        theme_path = get_path('audio/matrix_theme.wav')
        if os.path.exists(theme_path) and not self.mute_music:
            pygame.mixer.music.load(theme_path)
            pygame.mixer.music.set_volume(0.0 * self.custom_volume)
            pygame.mixer.music.play(-1)
            self.fade_music_in()

    def fade_music_in(self):
        for i in range(0, 11):
            pygame.mixer.music.set_volume(i / 10.0 * self.custom_volume)
            pygame.time.delay(100)

    def fade_music_out(self):
        for i in range(10, -1, -1):
            pygame.mixer.music.set_volume(i / 10.0 * self.custom_volume)
            pygame.time.delay(100)
        pygame.mixer.music.stop()

    def fade(self, fade_in=False, speed=15):
        if self.instant_transition:
            return
        fade_surface = pygame.Surface((WIDTH, HEIGHT))
        fade_surface.fill((0, 0, 0))
        clock = pygame.time.Clock()
        sequence = range(0, 256, speed) if not fade_in else range(255, -1, -speed)
        for alpha in sequence:
            fade_surface.set_alpha(alpha)
            self.screen.fill((0, 0, 0))
            self.level.run(0)
            self.screen.blit(fade_surface, (0, 0))
            pygame.display.update()
            clock.tick(FPS // 2)

    def handle_transition(self, target_map_id, target_spawn):
        self.fade(fade_in=False)
        self.current_map_id = target_map_id
        self.level = Level(
            self.current_map_id,
            player=self.player,
            loaded_data=None,
            player_spawn_pos=target_spawn,
            on_transition=self.handle_transition
        )
        self.fade(fade_in=True)

    def render_save_dialog(self):
        self.screen.fill((10, 20, 10))
        dialog_width, dialog_height = 600, 220
        dialog_x = (WIDTH - dialog_width) // 2
        dialog_y = (HEIGHT - dialog_height) // 2
        dialog_rect = pygame.Rect(dialog_x, dialog_y, dialog_width, dialog_height)
        shadow_rect = dialog_rect.move(6, 6)
        pygame.draw.rect(self.screen, (0, 0, 0, 100), shadow_rect, border_radius=24)
        pygame.draw.rect(self.screen, (15, 40, 20), dialog_rect, border_radius=24)
        pygame.draw.rect(self.screen, (0, 255, 0), dialog_rect, 3, border_radius=24)
        font_title = pygame.font.Font(None, 54)
        text1 = font_title.render("Detected Save File", True, (0, 255, 0))
        self.screen.blit(text1, (dialog_x + (dialog_width - text1.get_width()) // 2, dialog_y + 30))
        font_body = pygame.font.Font(None, 36)
        text2 = font_body.render("Press C to Continue or N to Reset Simulation", True, (0, 220, 0))
        self.screen.blit(text2, (dialog_x + (dialog_width - text2.get_width()) // 2, dialog_y + 100))
        font_hint = pygame.font.Font(None, 28)
        c_hint = font_hint.render("[C] Continue", True, (0, 255, 0))
        n_hint = font_hint.render("[N] New Game", True, (255, 100, 100))
        self.screen.blit(c_hint, (dialog_x + 80, dialog_y + 160))
        self.screen.blit(n_hint, (dialog_x + dialog_width - n_hint.get_width() - 80, dialog_y + 160))
        pygame.display.update()

    def run(self):
        last_time = time.time()
        while True:
            dt = time.time() - last_time
            last_time = time.time()
            adjusted_dt = dt * self.game_speed

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.fade_music_out()
                    pygame.quit()
                    sys.exit()
                if self.show_save_dialog:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_c:
                            self.save_dialog_result = 'c'
                        elif event.key == pygame.K_n:
                            self.save_dialog_result = 'n'
                else:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_m:
                            self.level.toggle_menu()
                        if event.key == pygame.K_p and getattr(self.level, 'game_paused', False):
                            if self.unlimited_saves or time.time() - (self.save_message_time or 0) > 1:
                                save_game(self.level.get_savable_state())
                                self.save_message_time = time.time()
                                print("Game saved!")
                        if self.level.game_over and event.key == pygame.K_r:
                            self.level.restart_game()

            if self.show_save_dialog:
                self.render_save_dialog()
                if self.save_dialog_result:
                    if self.save_dialog_result == 'c':
                        loaded_data = load_game('savegame.json')
                        self.level = Level(self.current_map_id, player=None, loaded_data=loaded_data, on_transition=self.handle_transition)
                    elif self.save_dialog_result == 'n':
                        self.level = Level(self.current_map_id, player=None, loaded_data=None, on_transition=self.handle_transition)
                    self.player = self.level.player
                    self.show_save_dialog = False
                self.clock.tick(FPS)
                continue

            # Apply hackable features
            if self.infinite_health or self.god_mode:
                self.player.health = self.player.stats['health']
            if self.infinite_mana or self.god_mode:
                self.player.energy = self.player.stats['energy']
            if self.one_hit_ko or self.god_mode:
                self.level.one_hit_ko = True
            if self.fast_attack:
                self.player.attack_cooldown = 100
            if self.super_speed:
                self.player.stats['speed'] = 600
            if self.regeneration:
                self.player.health = min(self.player.health + 0.5 * adjusted_dt, self.player.stats['health'])
            if self.no_cooldown:
                self.player.attack_cooldown = 0
            if self.time_freeze:
                self.level.time_stopped = True
            if self.no_clip:
                self.player.obstacle_sprites = pygame.sprite.Group()
            if self.teleport_enabled:
                self.player.pos = pygame.math.Vector2(self.teleport_target)
                self.player.rect.center = self.player.pos
                self.player.hitbox.center = self.player.pos
                self.teleport_enabled = False
            if self.free_upgrades:
                for stat in self.player.upgrade_cost:
                    self.player.upgrade_cost[stat] = 0
            if self.max_stats:
                for stat in self.player.stats:
                    self.player.stats[stat] = self.player.max_stats[stat]
            if self.mute_sounds:
                for sound in [self.level.red_pill_sound, self.level.endscene_sound, self.level.death_sound]:
                    sound.set_volume(0)
            if not self.hud_visible:
                self.level.ui.display = lambda _: None
            if self.instant_cast:
                self.level.magic_player.mana_cost_reduction = 0.0
            if self.pacifist_enemies:
                for sprite in self.level.attackable_sprites:
                    if sprite.sprite_type == 'enemy':
                        sprite.can_attack = False
            if self.fear_enemies:
                for sprite in self.level.attackable_sprites:
                    if sprite.sprite_type == 'enemy':
                        sprite.flees_from_player = True
            if self.increased_loot:
                self.level.increased_loot = True
            self.level.xp_multiplier = self.xp_multiplier
            self.level.enemy_spawn_rate = self.enemy_spawn_rate
            if self.invisibility:
                self.player.is_stealthy = True
            if self.dash_ability:
                self.player.can_wall_dash = True
            self.player.heal_on_hit = self.heal_on_hit
            self.player.mana_on_hit = self.mana_on_hit
            self.player.life_steal = self.life_steal
            self.player.critical_hit_chance = self.critical_hit_chance
            self.player.dodge_ability = self.dodge_ability
            self.player.parry_ability = self.parry_ability
            self.player.berserk_mode = self.berserk_mode
            self.player.stun_attack = self.stun_attack
            self.player.speed_burst = self.speed_burst
            self.player.shield_reflect = self.shield_reflect
            self.player.unlimited_ammo = self.unlimited_ammo
            self.player.random_teleport = self.random_teleport
            self.player.double_damage = self.double_damage
            self.player.invincibility_toggle = self.invincibility_toggle
            for sprite in self.level.attackable_sprites:
                if sprite.sprite_type == 'enemy':
                    sprite.explode_on_death = self.explode_on_death
                    sprite.regenerate = self.regenerate
                    sprite.regen_rate = self.regen_rate
                    sprite.swarm = self.swarm
                    sprite.health_reduction = self.health_reduction
                    sprite.damage_reduction = self.damage_reduction
                    sprite.speed_reduction = self.speed_reduction
                    sprite.aggro_range_reduction = self.aggro_range_reduction
                    sprite.loot_drop_increase = self.loot_drop_increase
                    sprite.xp_boost = self.xp_boost
                    sprite.stun_duration_increase = self.stun_duration_increase
                    sprite.knockback_effect = self.knockback_effect
                    sprite.fear_effect = self.fear_effect
                    sprite.flees_from_player = self.flees_from_player
                    if self.stun_enemies:
                        sprite.stunned = True
                        sprite.stun_time = pygame.time.get_ticks()
                        sprite.stun_duration = 1000
            for sprite in self.level.attack_sprites:
                if sprite.sprite_type == 'weapon':
                    sprite.damage_multiplier = self.damage_multiplier
                    sprite.attack_speed_boost = self.attack_speed_boost
                    sprite.elemental_damage = self.elemental_damage
                    sprite.range_extension = self.range_extension
                    sprite.projectile_speed = self.projectile_speed
                    sprite.homing_projectiles = self.homing_projectiles
                    sprite.area_of_effect = self.area_of_effect_weapon
                    sprite.invincibility_during_attack = self.invincibility_during_attack
                    sprite.ammo = self.ammo
            self.level.magic_player.mana_cost_reduction = self.mana_cost_reduction
            self.level.magic_player.spell_power_boost = self.spell_power_boost
            self.level.magic_player.cooldown_reduction = self.cooldown_reduction
            self.level.magic_player.area_of_effect = self.area_of_effect_magic
            self.level.magic_player.duration_extension = self.duration_extension
            self.level.magic_player.multi_target = self.multi_target
            self.level.magic_player.spell_chaining = self.spell_chaining
            self.level.magic_player.mana_regen_boost = self.mana_regen_boost
            self.level.magic_player.spell_penetration = self.spell_penetration

            self.screen.fill(WATER_COLOR)
            self.level.run(adjusted_dt)

            if self.debug_mode:
                font = pygame.font.SysFont('consolas', 20)
                debug_info = [
                    f"FPS: {int(self.clock.get_fps())}",
                    f"Pos: ({int(self.player.pos.x)}, {int(self.player.pos.y)})",
                    f"Health: {self.player.health}/{self.player.stats['health']}",
                    f"Energy: {self.player.energy}/{self.player.stats['energy']}",
                    f"XP: {self.player.exp}",
                    f"Map: {self.current_map_id}"
                ]
                for i, text in enumerate(debug_info):
                    debug_surf = font.render(text, True, (255, 255, 255))
                    self.screen.blit(debug_surf, (10, 10 + i * 20))

            # Anti-hacking checks
            if self.infinite_health and not self.god_mode:
                print("Cheat detected: Infinite health without God Mode!")
                self.player.health -= 10
            if self.xp_multiplier > 10.0:
                print("Cheat detected: Excessive XP multiplier!")
                self.player.exp = max(0, self.player.exp - 100)

            pygame.display.update()
            self.clock.tick(FPS)

def show_title_screen(screen):
    pygame.font.init()
    font_title = pygame.font.Font(None, 72)
    font_sub = pygame.font.Font(None, 36)
    title_text = font_title.render("Stuck in the Matrix", True, (0, 255, 0))
    sub_text = font_sub.render("Press ENTER to Escape", True, (0, 200, 0))
    while True:
        screen.fill((5, 20, 5))
        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 2 - 100))
        screen.blit(sub_text, (WIDTH // 2 - sub_text.get_width() // 2, HEIGHT // 2))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                return
        pygame.display.update()

def show_intro(screen):
    pygame.font.init()
    pygame.mixer.init()
    font = pygame.font.SysFont('consolas', 18, bold=True)
    cols = WIDTH // 16
    drops = [randint(0, HEIGHT // 16) for _ in range(cols)]
    chars = [chr(i) for i in range(33, 127)]
    clock = pygame.time.Clock()
    sound_path = get_path('audio/endscene.wav')
    if os.path.exists(sound_path):
        endscene_sound = pygame.mixer.Sound(sound_path)
        endscene_sound.set_volume(0.8)
        endscene_sound.play()
    trail_surface = pygame.Surface((WIDTH, HEIGHT))
    trail_surface.set_alpha(40)
    trail_surface.fill((0, 0, 0))
    running = True
    while running:
        screen.blit(trail_surface, (0, 0))
        for i in range(cols):
            char = choice(chars)
            text = font.render(char, True, (0, 255, 0))
            x = i * 16
            y = drops[i] * 16
            screen.blit(text, (x, y))
            if y > HEIGHT and randint(0, 50) > 48:
                drops[i] = 0
            else:
                drops[i] += 1
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                running = False
        pygame.display.update()
        clock.tick(30)
    if 'endscene_sound' in locals():
        endscene_sound.fadeout(1000)

if __name__ == '__main__':
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    show_title_screen(screen)
    show_intro(screen)
    game = Game()
    game.run()
