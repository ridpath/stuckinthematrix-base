import pygame
from settings import *
from support import get_path

# Matrix-style attribute renames
STAT_ALIASES = {
    'health': 'Stability Buffer',
    'energy': 'Memory Pool',
    'attack': 'Payload Vector',
    'magic': 'Injection Module',
    'speed': 'Thread Speed'
}

class Upgrade:
    def __init__(self, player):
        self.display_surface = pygame.display.get_surface()
        self.player = player
        self.attributes_len = len(player.stats)
        self.attributes_names = list(player.stats.keys())
        self.max_values = list(player.max_stats.values())

        try:
            self.font = pygame.font.Font(get_path(UI_FONT), UI_FONT_SIZE)
        except FileNotFoundError:
            self.font = pygame.font.SysFont('consolas', UI_FONT_SIZE)
            print("Warning: joystix.ttf not found. Using fallback system font.")

        self.width = self.display_surface.get_width() // (self.attributes_len + 1)
        self.height = self.display_surface.get_height() * 0.8
        self.create_items()

        self.selection_index = 0
        self.selection_time = None
        self.can_move = True

    def input(self):
        keys = pygame.key.get_pressed()
        if self.can_move:
            if keys[pygame.K_RIGHT] and self.selection_index < self.attributes_len - 1:
                self.selection_index += 1
                self.can_move = False
                self.selection_time = pygame.time.get_ticks()
            elif keys[pygame.K_LEFT] and self.selection_index > 0:
                self.selection_index -= 1
                self.can_move = False
                self.selection_time = pygame.time.get_ticks()

            if keys[pygame.K_SPACE]:
                self.can_move = False
                self.selection_time = pygame.time.get_ticks()
                self.items[self.selection_index].trigger(self.player)

    def selection_cooldown(self):
        if not self.can_move:
            if pygame.time.get_ticks() - self.selection_time >= 300:
                self.can_move = True

    def create_items(self):
        self.items = []
        for index in range(self.attributes_len):
            full_width = self.display_surface.get_width()
            increment = full_width // self.attributes_len
            left = (index * increment) + (increment - self.width) // 2
            top = self.display_surface.get_height() * 0.1
            item = Item(left, top, self.width, self.height, index, self.font)
            self.items.append(item)

    def display(self):
        self.input()
        self.selection_cooldown()

        for index, item in enumerate(self.items):
            key = self.attributes_names[index]
            display_name = STAT_ALIASES.get(key, key)
            value = self.player.get_value_by_index(index)
            max_value = self.max_values[index]
            cost = self.player.get_cost_by_index(index)

            item.display(self.display_surface, self.selection_index, display_name, value, max_value, cost)


class Item:
    def __init__(self, l, t, w, h, index, font):
        self.rect = pygame.Rect(l, t, w, h)
        self.index = index
        self.font = font

    def display_names(self, surface, name, cost, selected):
        color = TEXT_COLOR_SELECTED if selected else TEXT_COLOR
        title_surf = self.font.render(name, False, color)
        title_rect = title_surf.get_rect(midtop=self.rect.midtop + pygame.math.Vector2(0, 20))

        cost_surf = self.font.render(f'{int(cost)} EXP', False, color)
        cost_rect = cost_surf.get_rect(midbottom=self.rect.midbottom - pygame.math.Vector2(0, 20))

        surface.blit(title_surf, title_rect)
        surface.blit(cost_surf, cost_rect)

    def display_bar(self, surface, value, max_value, selected):
        top = self.rect.midtop + pygame.math.Vector2(0, 60)
        bottom = self.rect.midbottom - pygame.math.Vector2(0, 60)
        color = BAR_COLOR_SELECTED if selected else BAR_COLOR

        full_height = bottom[1] - top[1]
        relative_num = (value / max_value) * full_height
        value_rect = pygame.Rect(top[0] - 15, bottom[1] - relative_num, 30, 10)

        pygame.draw.line(surface, color, top, bottom, 5)
        pygame.draw.rect(surface, color, value_rect)

    def trigger(self, player):
        key = list(player.stats.keys())[self.index]
        if player.exp >= player.upgrade_cost[key] and player.stats[key] < player.max_stats[key]:
            player.exp -= player.upgrade_cost[key]
            player.stats[key] *= 1.2
            player.upgrade_cost[key] *= 1.4

            # Clamp to max
            if player.stats[key] > player.max_stats[key]:
                player.stats[key] = player.max_stats[key]

    def display(self, surface, selection_num, name, value, max_value, cost):
        pygame.draw.rect(surface,
                         UPGRADE_BG_COLOR_SELECTED if self.index == selection_num else UI_BG_COLOR,
                         self.rect)
        pygame.draw.rect(surface, UI_BORDER_COLOR, self.rect, 4)

        self.display_names(surface, name, cost, self.index == selection_num)
        self.display_bar(surface, value, max_value, self.index == selection_num)
