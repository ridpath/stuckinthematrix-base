import pygame
import os
from settings import *
from support import get_path

class UI:
    def __init__(self):
        self.display_surface = pygame.display.get_surface()
        try:
            self.font = pygame.font.Font(get_path(UI_FONT), UI_FONT_SIZE)
        except FileNotFoundError:
            self.font = pygame.font.SysFont('consolas', UI_FONT_SIZE)
            print("Warning: UI font not found, using fallback system font.")

        # Bar areas
        self.health_bar_rect = pygame.Rect(10, 10, HEALTH_BAR_WIDTH, BAR_HEIGHT)
        self.energy_bar_rect = pygame.Rect(10, 34, ENERGY_BAR_WIDTH, BAR_HEIGHT)

        # Weapon icons
        self.weapon_graphics = []
        for weapon in weapon_data.values():
            try:
                weapon_img = pygame.image.load(get_path(weapon['graphic'])).convert_alpha()
            except FileNotFoundError:
                weapon_img = pygame.Surface((ITEM_BOX_SIZE - 4, ITEM_BOX_SIZE - 4), pygame.SRCALPHA)
                weapon_img.fill((255, 0, 0))
                print(f"Warning: Missing weapon graphic: {weapon['graphic']}")
            self.weapon_graphics.append(weapon_img)

        # Magic icons
        self.magic_graphics = []
        for magic in magic_data.values():
            try:
                magic_img = pygame.image.load(get_path(magic['graphic'])).convert_alpha()
            except FileNotFoundError:
                magic_img = pygame.Surface((ITEM_BOX_SIZE - 4, ITEM_BOX_SIZE - 4), pygame.SRCALPHA)
                magic_img.fill((0, 0, 255))
                print(f"Warning: Missing magic graphic: {magic['graphic']}")
            self.magic_graphics.append(magic_img)

    def show_bar(self, current, max_amount, bg_rect, color, label):
        pygame.draw.rect(self.display_surface, UI_BG_COLOR, bg_rect)

        ratio = current / max_amount
        current_width = bg_rect.width * ratio
        current_rect = bg_rect.copy()
        current_rect.width = current_width
        pygame.draw.rect(self.display_surface, color, current_rect)
        pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, bg_rect, 3)

        label_surf = self.font.render(label, False, TEXT_COLOR)
        self.display_surface.blit(label_surf, (bg_rect.left + 5, bg_rect.top - 2))

    def show_exp(self, exp):
        text_surf = self.font.render(f"{int(exp)} EXP", False, TEXT_COLOR)
        x = self.display_surface.get_size()[0] - 20
        y = self.display_surface.get_size()[1] - 20
        text_rect = text_surf.get_rect(bottomright=(x, y))

        pygame.draw.rect(self.display_surface, UI_BG_COLOR, text_rect.inflate(20, 20))
        self.display_surface.blit(text_surf, text_rect)
        pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, text_rect.inflate(20, 20), 3)

    def selection_box(self, left, top, has_switched):
        bg_rect = pygame.Rect(left, top, ITEM_BOX_SIZE, ITEM_BOX_SIZE)
        pygame.draw.rect(self.display_surface, UI_BG_COLOR, bg_rect)

        border_color = UI_BORDER_COLOR_ACTIVE if has_switched else UI_BORDER_COLOR
        pygame.draw.rect(self.display_surface, border_color, bg_rect, 3)
        return bg_rect

    def weapon_overlay(self, weapon_index, has_switched):
        bg_rect = self.selection_box(10, 630, has_switched)
        if weapon_index < len(self.weapon_graphics):
            weapon_surf = self.weapon_graphics[weapon_index]
            weapon_rect = weapon_surf.get_rect(center=bg_rect.center)
            self.display_surface.blit(weapon_surf, weapon_rect)

    def magic_overlay(self, magic_index, has_switched):
        bg_rect = self.selection_box(80, 635, has_switched)
        if magic_index < len(self.magic_graphics):
            magic_surf = self.magic_graphics[magic_index]
            magic_rect = magic_surf.get_rect(center=bg_rect.center)
            self.display_surface.blit(magic_surf, magic_rect)

    def display(self, player):
        self.show_bar(player.health, player.stats['health'], self.health_bar_rect, HEALTH_COLOR, "STABILITY")
        self.show_bar(player.energy, player.stats['energy'], self.energy_bar_rect, ENERGY_COLOR, "BUFFER")
        self.show_exp(player.exp)
        self.weapon_overlay(player.weapon_index, not player.can_switch_weapon)
        self.magic_overlay(player.magic_index, not player.can_switch_magic)
