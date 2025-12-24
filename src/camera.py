"""
Frozen Signal - Camera System
Handles viewport, screen shake, and smooth following
"""

import pygame
import math
import random
from .constants import RENDER_WIDTH, RENDER_HEIGHT, TILE_SIZE


class Camera:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.x = 0
        self.y = 0
        self.target_x = 0
        self.target_y = 0

        # Smooth following
        self.lerp_speed = 0.1

        # Screen shake
        self.shake_intensity = 0
        self.shake_duration = 0
        self.shake_offset_x = 0
        self.shake_offset_y = 0

        # Bounds
        self.bounds = None

    def set_bounds(self, min_x, min_y, max_x, max_y):
        """Set camera movement boundaries"""
        self.bounds = (min_x, min_y, max_x, max_y)

    def follow(self, target, instant=False):
        """Follow a target entity"""
        # Center camera on target
        self.target_x = target.x - self.width // 2
        self.target_y = target.y - self.height // 2

        if instant:
            self.x = self.target_x
            self.y = self.target_y

    def update(self, dt):
        """Update camera position with smooth following"""
        # Smooth interpolation
        self.x += (self.target_x - self.x) * self.lerp_speed
        self.y += (self.target_y - self.y) * self.lerp_speed

        # Apply bounds
        if self.bounds:
            min_x, min_y, max_x, max_y = self.bounds
            self.x = max(min_x, min(self.x, max_x - self.width))
            self.y = max(min_y, min(self.y, max_y - self.height))

        # Update screen shake
        if self.shake_duration > 0:
            self.shake_duration -= dt
            self.shake_offset_x = random.uniform(-self.shake_intensity, self.shake_intensity)
            self.shake_offset_y = random.uniform(-self.shake_intensity, self.shake_intensity)
        else:
            self.shake_offset_x = 0
            self.shake_offset_y = 0
            self.shake_intensity = 0

    def shake(self, intensity, duration):
        """Trigger screen shake effect"""
        self.shake_intensity = intensity
        self.shake_duration = duration

    def apply(self, pos):
        """Convert world position to screen position"""
        x = pos[0] - int(self.x) + int(self.shake_offset_x)
        y = pos[1] - int(self.y) + int(self.shake_offset_y)
        return (x, y)

    def apply_rect(self, rect):
        """Convert world rect to screen rect"""
        return pygame.Rect(
            rect.x - int(self.x) + int(self.shake_offset_x),
            rect.y - int(self.y) + int(self.shake_offset_y),
            rect.width,
            rect.height
        )

    def reverse(self, pos):
        """Convert screen position to world position"""
        return (pos[0] + int(self.x), pos[1] + int(self.y))

    def get_visible_rect(self):
        """Get the visible world area"""
        return pygame.Rect(
            int(self.x) - TILE_SIZE,
            int(self.y) - TILE_SIZE,
            self.width + TILE_SIZE * 2,
            self.height + TILE_SIZE * 2
        )
