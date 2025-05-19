import pygame
from support import get_path, import_folder
from random import choice


class AnimationPlayer:
    def __init__(self):
        self.frames = {
            'flame': self.safe_import('graphics/particles/flame/frames'),
            'aura': self.safe_import('graphics/particles/aura'),
            'heal': self.safe_import('graphics/particles/heal/frames'),
            'claw': self.safe_import('graphics/particles/claw'),
            'slash': self.safe_import('graphics/particles/slash'),
            'sparkle': self.safe_import('graphics/particles/sparkle'),
            'leaf_attack': self.safe_import('graphics/particles/leaf_attack'),
            'thunder': self.safe_import('graphics/particles/thunder'),
            'squid': self.safe_import('graphics/particles/smoke_orange'),
            'raccoon': self.safe_import('graphics/particles/raccoon'),
            'spirit': self.safe_import('graphics/particles/nova'),
            'bamboo': self.safe_import('graphics/particles/bamboo'),
            'leaf': (
                self.safe_import('graphics/particles/leaf1'),
                self.safe_import('graphics/particles/leaf2'),
                self.safe_import('graphics/particles/leaf3'),
                self.safe_import('graphics/particles/leaf4'),
                self.safe_import('graphics/particles/leaf5'),
                self.safe_import('graphics/particles/leaf6'),
                self.reflect_images(self.safe_import('graphics/particles/leaf1')),
                self.reflect_images(self.safe_import('graphics/particles/leaf2')),
                self.reflect_images(self.safe_import('graphics/particles/leaf3')),
                self.reflect_images(self.safe_import('graphics/particles/leaf4')),
                self.reflect_images(self.safe_import('graphics/particles/leaf5')),
                self.reflect_images(self.safe_import('graphics/particles/leaf6')),
            ),
            'exp_orb': self.safe_import('graphics/particles/exp_orb')
        }

    def safe_import(self, folder_path):
        try:
            return import_folder(folder_path)
        except Exception as e:
            print(f"Warning: Failed to load particle frames from {folder_path} -> {e}")
            return [pygame.Surface((1, 1), pygame.SRCALPHA)]

    def reflect_images(self, frames):
        return [pygame.transform.flip(frame, True, False) for frame in frames]

    def create_grass_particles(self, pos, groups):
        grass_animation_frames = choice(self.frames['leaf'])
        ParticleEffect(pos, grass_animation_frames, groups)

    def create_particles(self, animation_type, pos, groups):
        animation_frames = self.frames.get(animation_type, [])
        if animation_frames:
            ParticleEffect(pos, animation_frames, groups)

    def create_exp_particles(self, pos, target_pos, groups, amount=5, speed=250, exp_amount=None):
        from random import uniform
        orb_frames = self.frames.get('exp_orb', []) or self.frames.get('sparkle', [])
        if not orb_frames:
            return

        for _ in range(amount):
            offset = pygame.math.Vector2(uniform(-10, 10), uniform(-10, 10))
            spawn_pos = (pos[0] + offset.x, pos[1] + offset.y)
            MovingParticleEffect(spawn_pos, orb_frames, groups, target_pos, speed, sprite_type='exp_orb')

        if exp_amount is not None:
            self.create_floating_text(f"+{exp_amount} XP", pos, groups)

    def create_floating_text(self, text, pos, groups, color=(255, 255, 0), font_size=18, duration=1.2, rise_distance=30):
        FloatingText(text, pos, groups, color, font_size, duration, rise_distance)


class FloatingText(pygame.sprite.Sprite):
    def __init__(self, text, pos, groups, color=(255, 255, 0), font_size=18, duration=1.2, rise_distance=30):
        super().__init__(groups)
        try:
            self.font = pygame.font.Font(get_path('font/joystix.ttf'), font_size)
        except FileNotFoundError:
            print("Warning: joystix.ttf not found. Using system fallback font.")
            self.font = pygame.font.SysFont("consolas", font_size)

        self.image = self.font.render(text, True, color)
        self.rect = self.image.get_rect(center=pos)
        self.start_pos = pygame.math.Vector2(pos)
        self.duration = duration
        self.elapsed = 0
        self.rise_distance = rise_distance
        self.alpha = 255

    def update(self, dt):
        self.elapsed += dt
        progress = min(self.elapsed / self.duration, 1.0)
        offset_y = -self.rise_distance * progress
        self.rect.center = (self.start_pos.x, self.start_pos.y + offset_y)
        self.alpha = int(255 * (1 - progress))
        self.image.set_alpha(self.alpha)
        if self.elapsed >= self.duration:
            self.kill()


class ParticleEffect(pygame.sprite.Sprite):
    def __init__(self, pos, animation_frames, groups, sprite_type='magic'):
        super().__init__(groups)
        self.sprite_type = sprite_type
        self.frame_index = 0
        self.animation_speed = 15
        self.frames = animation_frames
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect(center=pos)

    def animate(self, dt):
        self.frame_index += self.animation_speed * dt
        if self.frame_index >= len(self.frames):
            self.kill()
        else:
            self.image = self.frames[int(self.frame_index)]

    def update(self, dt):
        self.animate(dt)


class MovingParticleEffect(ParticleEffect):
    def __init__(self, pos, animation_frames, groups, target_pos, speed=250, sprite_type='exp_orb', max_lifetime=1.5):
        super().__init__(pos, animation_frames, groups, sprite_type)
        self.target_pos = pygame.math.Vector2(target_pos)
        self.pos = pygame.math.Vector2(pos)
        self.speed = speed
        self.max_lifetime = max_lifetime
        self.lifetime = 0

    def update(self, dt):
        direction = self.target_pos - self.pos
        distance = direction.length()
        if distance > 0:
            direction = direction.normalize()
            move_dist = min(self.speed * dt, distance)
            self.pos += direction * move_dist
            self.rect.center = (round(self.pos.x), round(self.pos.y))

        self.animate(dt)
        self.lifetime += dt
        if distance < 16 or self.lifetime > self.max_lifetime:
            self.kill()
