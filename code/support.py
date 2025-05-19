import os
import pygame
import sys
from csv import reader

# Caches root path after first detection
_PROJECT_ROOT = None

def get_path(relative_path: str) -> str:
    """
    Resolves a file path relative to the `pyzelda-rpg` project root.
    It searches upwards from the current file until it finds the expected folders.
    """
    global _PROJECT_ROOT
    if _PROJECT_ROOT is None:
        current = os.path.abspath(__file__)
        while True:
            current = os.path.dirname(current)
            if os.path.isdir(os.path.join(current, "graphics")) and os.path.isdir(os.path.join(current, "audio")):
                _PROJECT_ROOT = current
                break
            if current == os.path.dirname(current):
                raise FileNotFoundError("Project root with 'graphics/' and 'audio/' not found.")

    final_path = os.path.join(_PROJECT_ROOT, relative_path)
    if not os.path.exists(final_path):
        print(f"Warning: File not found at path: {final_path}")
    return final_path

def import_csv_layout(path: str) -> list[list[str]]:
    """
    Parses a CSV file into a 2D list of strings.

    Args:
        path (str): Relative path to the CSV file.

    Returns:
        list[list[str]]: 2D map layout.
    """
    layout = []
    full_path = get_path(path)
    with open(full_path, newline='') as file:
        csv_reader = reader(file, delimiter=',')
        layout = [list(row) for row in csv_reader]
    return layout

def import_folder(path: str) -> list[pygame.Surface]:
    """
    Loads all images from a folder into a list.

    Args:
        path (str): Relative folder path.

    Returns:
        list[pygame.Surface]: List of loaded images with alpha transparency.
    """
    full_path = get_path(path)
    images = []

    if not os.path.isdir(full_path):
        print(f"Warning: Directory not found: {full_path}")
        return images

    for _, _, files in os.walk(full_path):
        for file in sorted(files):
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                image_path = os.path.join(full_path, file)
                try:
                    surface = pygame.image.load(image_path).convert_alpha()
                    images.append(surface)
                except Exception as e:
                    print(f"Warning: Failed to load image {image_path}: {e}")

    return images
