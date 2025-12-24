"""
Frozen Signal - Visual Effects System
CRT effects, scanlines, color grading, and atmospheric effects
"""

import pygame
import math
import random
from .constants import Colors, RENDER_WIDTH, RENDER_HEIGHT


class VisualEffects:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        # CRT effect settings
        self.scanline_opacity = 40
        self.vignette_strength = 0.4
        self.chromatic_aberration = 1
        self.noise_intensity = 0.02
        self.flicker_intensity = 0.02

        # Pre-render scanlines overlay
        self.scanlines = self._create_scanlines()
        self.vignette = self._create_vignette()

        # Noise frame
        self.noise_timer = 0
        self.noise_surface = None
        self._update_noise()

        # Flicker
        self.flicker_value = 1.0
        self.flicker_timer = 0

        # Screen distortion for sanity effects
        self.distortion_amount = 0
        self.distortion_timer = 0

        # Cold overlay
        self.cold_overlay = self._create_cold_overlay()
        self.cold_intensity = 0

        # Blood vignette for damage
        self.damage_flash = 0

    def _create_scanlines(self):
        """Create scanline overlay"""
        surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        for y in range(0, self.height, 2):
            pygame.draw.line(surface, (0, 0, 0, self.scanline_opacity),
                           (0, y), (self.width, y))
        return surface

    def _create_vignette(self):
        """Create vignette overlay"""
        surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        center_x = self.width // 2
        center_y = self.height // 2
        max_dist = math.sqrt(center_x ** 2 + center_y ** 2)

        for y in range(self.height):
            for x in range(self.width):
                dist = math.sqrt((x - center_x) ** 2 + (y - center_y) ** 2)
                intensity = (dist / max_dist) ** 2 * self.vignette_strength
                alpha = int(min(255, intensity * 255))
                surface.set_at((x, y), (0, 0, 0, alpha))
        return surface

    def _create_cold_overlay(self):
        """Create frost overlay for cold effect"""
        surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        # Create frosted edges
        for y in range(self.height):
            for x in range(self.width):
                edge_dist = min(x, y, self.width - x, self.height - y)
                if edge_dist < 40:
                    intensity = (40 - edge_dist) / 40
                    noise = random.random() * 0.3
                    alpha = int((intensity + noise) * 180)
                    color = (180, 200, 220, min(255, alpha))
                    surface.set_at((x, y), color)
        return surface

    def _update_noise(self):
        """Generate noise texture"""
        self.noise_surface = pygame.Surface((self.width // 4, self.height // 4), pygame.SRCALPHA)
        for y in range(self.height // 4):
            for x in range(self.width // 4):
                if random.random() < self.noise_intensity:
                    gray = random.randint(0, 50)
                    self.noise_surface.set_at((x, y), (gray, gray, gray, 30))

    def update(self, dt, sanity=100, warmth=100):
        """Update effect parameters"""
        # Update noise periodically
        self.noise_timer += dt
        if self.noise_timer > 0.1:
            self.noise_timer = 0
            self._update_noise()

        # Flicker effect
        self.flicker_timer += dt
        if self.flicker_timer > 0.05:
            self.flicker_timer = 0
            self.flicker_value = 1.0 - random.random() * self.flicker_intensity

        # Sanity-based distortion
        if sanity < 50:
            self.distortion_amount = (50 - sanity) / 50 * 0.3
            self.distortion_timer += dt
        else:
            self.distortion_amount = 0

        # Cold intensity
        if warmth < 50:
            self.cold_intensity = (50 - warmth) / 50
        else:
            self.cold_intensity = 0

        # Fade damage flash
        if self.damage_flash > 0:
            self.damage_flash = max(0, self.damage_flash - dt * 2)

    def apply_chromatic_aberration(self, surface):
        """Apply RGB channel separation"""
        if self.chromatic_aberration <= 0:
            return surface

        result = pygame.Surface((self.width, self.height))

        # Separate channels with slight offset
        r_surface = surface.copy()
        g_surface = surface.copy()
        b_surface = surface.copy()

        # Apply color filters
        r_surface.fill((255, 0, 0), special_flags=pygame.BLEND_MULT)
        g_surface.fill((0, 255, 0), special_flags=pygame.BLEND_MULT)
        b_surface.fill((0, 0, 255), special_flags=pygame.BLEND_MULT)

        # Offset red and blue channels
        offset = self.chromatic_aberration
        result.blit(r_surface, (-offset, 0), special_flags=pygame.BLEND_ADD)
        result.blit(g_surface, (0, 0), special_flags=pygame.BLEND_ADD)
        result.blit(b_surface, (offset, 0), special_flags=pygame.BLEND_ADD)

        return result

    def apply_distortion(self, surface):
        """Apply sanity distortion effect"""
        if self.distortion_amount <= 0:
            return surface

        result = surface.copy()
        wave = math.sin(self.distortion_timer * 10) * self.distortion_amount * 5

        # Simple wave distortion
        for y in range(0, self.height, 4):
            offset = int(math.sin(y * 0.1 + self.distortion_timer * 5) * wave)
            strip = surface.subsurface((0, y, self.width, min(4, self.height - y)))
            result.blit(strip, (offset, y))

        return result

    def apply(self, surface):
        """Apply all post-processing effects"""
        result = surface.copy()

        # Apply chromatic aberration
        if self.chromatic_aberration > 0:
            result = self.apply_chromatic_aberration(result)

        # Apply sanity distortion
        if self.distortion_amount > 0:
            result = self.apply_distortion(result)

        # Apply flicker
        if self.flicker_value < 1.0:
            dark = pygame.Surface((self.width, self.height))
            dark.fill((0, 0, 0))
            dark.set_alpha(int((1 - self.flicker_value) * 50))
            result.blit(dark, (0, 0))

        # Apply noise
        if self.noise_surface:
            scaled_noise = pygame.transform.scale(self.noise_surface, (self.width, self.height))
            result.blit(scaled_noise, (0, 0), special_flags=pygame.BLEND_ADD)

        # Apply cold overlay
        if self.cold_intensity > 0:
            cold = self.cold_overlay.copy()
            cold.set_alpha(int(self.cold_intensity * 200))
            result.blit(cold, (0, 0))

        # Apply damage flash
        if self.damage_flash > 0:
            flash = pygame.Surface((self.width, self.height))
            flash.fill(Colors.BLOOD_RED)
            flash.set_alpha(int(self.damage_flash * 100))
            result.blit(flash, (0, 0))

        # Apply scanlines
        result.blit(self.scanlines, (0, 0))

        # Apply vignette
        result.blit(self.vignette, (0, 0))

        return result

    def trigger_damage_flash(self):
        """Trigger red damage flash"""
        self.damage_flash = 1.0


class LightingSystem:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.ambient_light = 0.3
        self.lights = []

        # Create darkness overlay
        self.darkness = pygame.Surface((width, height), pygame.SRCALPHA)

    def add_light(self, x, y, radius, color=(255, 200, 150), intensity=1.0, flicker=False):
        """Add a light source"""
        self.lights.append({
            'x': x,
            'y': y,
            'radius': radius,
            'color': color,
            'intensity': intensity,
            'flicker': flicker,
            'flicker_offset': random.random() * math.pi * 2
        })

    def clear_lights(self):
        """Clear all dynamic lights"""
        self.lights = []

    def update(self, dt, time):
        """Update flickering lights"""
        for light in self.lights:
            if light['flicker']:
                light['current_intensity'] = light['intensity'] * (
                    0.8 + 0.2 * math.sin(time * 10 + light['flicker_offset']) +
                    random.random() * 0.1
                )
            else:
                light['current_intensity'] = light['intensity']

    def render(self, surface, camera):
        """Render lighting overlay"""
        # Fill with darkness
        darkness_level = int((1 - self.ambient_light) * 255)
        self.darkness.fill((0, 0, 0, darkness_level))

        # Cut out light areas
        for light in self.lights:
            screen_pos = camera.apply((light['x'], light['y']))
            intensity = light.get('current_intensity', light['intensity'])
            radius = int(light['radius'] * intensity)

            if radius <= 0:
                continue

            # Create radial gradient for light
            for r in range(radius, 0, -2):
                alpha = int((1 - r / radius) * 255 * intensity)
                color = (*light['color'][:3], alpha)
                pygame.draw.circle(self.darkness, (0, 0, 0, 255 - alpha),
                                 screen_pos, r)

        # Apply darkness overlay
        surface.blit(self.darkness, (0, 0))


class ParticleSystem:
    def __init__(self):
        self.particles = []

    def emit(self, x, y, particle_type="dust", count=1):
        """Emit particles at position"""
        for _ in range(count):
            if particle_type == "dust":
                self.particles.append({
                    'x': x + random.uniform(-5, 5),
                    'y': y + random.uniform(-5, 5),
                    'vx': random.uniform(-0.2, 0.2),
                    'vy': random.uniform(-0.5, -0.1),
                    'life': random.uniform(1, 3),
                    'max_life': random.uniform(1, 3),
                    'size': random.randint(1, 2),
                    'color': Colors.FROST
                })
            elif particle_type == "blood":
                self.particles.append({
                    'x': x,
                    'y': y,
                    'vx': random.uniform(-2, 2),
                    'vy': random.uniform(-2, 1),
                    'life': random.uniform(0.5, 1),
                    'max_life': random.uniform(0.5, 1),
                    'size': random.randint(1, 3),
                    'color': Colors.BLOOD_RED
                })
            elif particle_type == "spark":
                self.particles.append({
                    'x': x,
                    'y': y,
                    'vx': random.uniform(-3, 3),
                    'vy': random.uniform(-3, 3),
                    'life': random.uniform(0.1, 0.3),
                    'max_life': random.uniform(0.1, 0.3),
                    'size': 1,
                    'color': Colors.AMBER_LIGHT
                })
            elif particle_type == "frost":
                self.particles.append({
                    'x': x + random.uniform(-10, 10),
                    'y': y,
                    'vx': random.uniform(-0.1, 0.1),
                    'vy': random.uniform(0.2, 0.5),
                    'life': random.uniform(2, 4),
                    'max_life': random.uniform(2, 4),
                    'size': random.randint(1, 2),
                    'color': Colors.PURE_WHITE
                })

    def update(self, dt):
        """Update all particles"""
        for particle in self.particles[:]:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['life'] -= dt

            if particle['life'] <= 0:
                self.particles.remove(particle)

    def render(self, surface, camera):
        """Render all particles"""
        for particle in self.particles:
            alpha = int((particle['life'] / particle['max_life']) * 255)
            pos = camera.apply((int(particle['x']), int(particle['y'])))
            color = (*particle['color'][:3], alpha) if len(particle['color']) == 3 else particle['color']

            if particle['size'] == 1:
                if 0 <= pos[0] < surface.get_width() and 0 <= pos[1] < surface.get_height():
                    surface.set_at(pos, particle['color'])
            else:
                s = pygame.Surface((particle['size'] * 2, particle['size'] * 2), pygame.SRCALPHA)
                pygame.draw.circle(s, color, (particle['size'], particle['size']), particle['size'])
                surface.blit(s, (pos[0] - particle['size'], pos[1] - particle['size']))
