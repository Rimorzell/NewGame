"""
Frozen Signal - Player System
Player entity with movement, stats, and survival mechanics
"""

import pygame
import math
from .constants import (
    Colors, TILE_SIZE, Direction, Layer,
    PLAYER_SPEED, PLAYER_RUN_SPEED,
    PLAYER_MAX_HEALTH, PLAYER_MAX_SANITY, PLAYER_MAX_WARMTH,
    SANITY_DRAIN_RATE, COLD_DRAIN_RATE,
    COLD_DAMAGE_THRESHOLD, COLD_DAMAGE_RATE,
    MELEE_DAMAGE, MELEE_RANGE, PISTOL_DAMAGE, PISTOL_RANGE
)
from .inventory import Inventory


class Player:
    """Player character with survival mechanics"""

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 14
        self.height = 14
        self.layer = Layer.PLAYER

        # Movement
        self.velocity_x = 0
        self.velocity_y = 0
        self.speed = PLAYER_SPEED
        self.facing = Direction.DOWN
        self.moving = False
        self.running = False

        # Stats
        self.health = PLAYER_MAX_HEALTH
        self.max_health = PLAYER_MAX_HEALTH
        self.sanity = PLAYER_MAX_SANITY
        self.max_sanity = PLAYER_MAX_SANITY
        self.warmth = PLAYER_MAX_WARMTH
        self.max_warmth = PLAYER_MAX_WARMTH

        # Status effects
        self.is_in_cold_zone = False
        self.is_in_dark = False
        self.is_near_enemy = False
        self.damage_immunity_timer = 0

        # Combat
        self.attacking = False
        self.attack_timer = 0
        self.attack_cooldown = 0
        self.equipped_weapon = None

        # Animation
        self.animation_frame = 0
        self.animation_timer = 0
        self.animation_speed = 0.15

        # Inventory
        self.inventory = Inventory()

        # Flags for narrative/endings
        self.discovered_flags = set()
        self.notes_read = []
        self.audio_logs_heard = []

        # Create sprites
        self._create_sprites()

    def _create_sprites(self):
        """Create player sprite sheets"""
        self.sprites = {}

        # Create simple directional sprites
        for direction in ['up', 'down', 'left', 'right']:
            frames = []
            for frame in range(4):
                sprite = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

                # Body
                pygame.draw.ellipse(sprite, Colors.DEEP_BLUE,
                                  (1, 4, 12, 10))  # Parka body

                # Head
                pygame.draw.ellipse(sprite, Colors.FROST,
                                  (3, 0, 8, 8))  # Face

                # Hood
                pygame.draw.arc(sprite, Colors.ICE_BLUE,
                              (2, -1, 10, 10), 0, math.pi, 2)

                # Walking animation - leg movement
                if frame % 2 == 0:
                    pygame.draw.line(sprite, Colors.DARK_BLUE,
                                   (4, 12), (3, 14), 2)
                    pygame.draw.line(sprite, Colors.DARK_BLUE,
                                   (10, 12), (11, 14), 2)
                else:
                    pygame.draw.line(sprite, Colors.DARK_BLUE,
                                   (4, 12), (5, 14), 2)
                    pygame.draw.line(sprite, Colors.DARK_BLUE,
                                   (10, 12), (9, 14), 2)

                # Direction indicator (eyes or back of head)
                if direction == 'down':
                    pygame.draw.circle(sprite, Colors.DARK_BLUE, (5, 4), 1)
                    pygame.draw.circle(sprite, Colors.DARK_BLUE, (9, 4), 1)
                elif direction == 'up':
                    pygame.draw.arc(sprite, Colors.ICE_BLUE,
                                  (4, 1, 6, 6), 0, math.pi, 1)
                elif direction == 'left':
                    pygame.draw.circle(sprite, Colors.DARK_BLUE, (4, 4), 1)
                elif direction == 'right':
                    pygame.draw.circle(sprite, Colors.DARK_BLUE, (9, 4), 1)

                frames.append(sprite)
            self.sprites[direction] = frames

        # Idle sprite (same as down, frame 0)
        self.sprites['idle'] = [self.sprites['down'][0]]

    @property
    def rect(self):
        return pygame.Rect(self.x - self.width // 2, self.y - self.height // 2,
                          self.width, self.height)

    @property
    def center(self):
        return (self.x, self.y)

    def handle_input(self, keys, dt):
        """Process movement input"""
        self.velocity_x = 0
        self.velocity_y = 0
        self.moving = False

        # Running
        self.running = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
        current_speed = PLAYER_RUN_SPEED if self.running else self.speed

        # Movement
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.velocity_y = -current_speed
            self.facing = Direction.UP
            self.moving = True
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.velocity_y = current_speed
            self.facing = Direction.DOWN
            self.moving = True
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.velocity_x = -current_speed
            self.facing = Direction.LEFT
            self.moving = True
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.velocity_x = current_speed
            self.facing = Direction.RIGHT
            self.moving = True

        # Normalize diagonal movement
        if self.velocity_x != 0 and self.velocity_y != 0:
            self.velocity_x *= 0.707
            self.velocity_y *= 0.707

    def update(self, dt, game):
        """Update player state"""
        # Update damage immunity
        if self.damage_immunity_timer > 0:
            self.damage_immunity_timer -= dt

        # Update attack
        if self.attacking:
            self.attack_timer -= dt
            if self.attack_timer <= 0:
                self.attacking = False

        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt

        # Apply movement with collision
        new_x = self.x + self.velocity_x
        new_y = self.y + self.velocity_y

        # Check collision for X movement
        test_rect = pygame.Rect(new_x - self.width // 2, self.y - self.height // 2,
                               self.width, self.height)
        if not game.level.check_collision(test_rect):
            self.x = new_x

        # Check collision for Y movement
        test_rect = pygame.Rect(self.x - self.width // 2, new_y - self.height // 2,
                               self.width, self.height)
        if not game.level.check_collision(test_rect):
            self.y = new_y

        # Update animation
        if self.moving:
            self.animation_timer += dt
            if self.animation_timer >= self.animation_speed:
                self.animation_timer = 0
                self.animation_frame = (self.animation_frame + 1) % 4
        else:
            self.animation_frame = 0

        # Update survival mechanics
        self._update_survival(dt, game)

    def _update_survival(self, dt, game):
        """Update sanity, warmth, and related effects"""
        # Cold drain
        if self.is_in_cold_zone:
            self.warmth -= COLD_DRAIN_RATE * dt * 60

        # Sanity drain from darkness and enemies
        sanity_drain = 0
        if self.is_in_dark:
            sanity_drain += SANITY_DRAIN_RATE
        if self.is_near_enemy:
            sanity_drain += SANITY_DRAIN_RATE * 2

        self.sanity -= sanity_drain * dt * 60

        # Cold damage
        if self.warmth < COLD_DAMAGE_THRESHOLD:
            cold_factor = 1 - (self.warmth / COLD_DAMAGE_THRESHOLD)
            self.health -= COLD_DAMAGE_RATE * cold_factor * dt * 60

        # Clamp values
        self.health = max(0, min(self.health, self.max_health))
        self.sanity = max(0, min(self.sanity, self.max_sanity))
        self.warmth = max(0, min(self.warmth, self.max_warmth))

        # Check death
        if self.health <= 0:
            game.trigger_game_over("You succumbed to the cold and darkness.")

    def attack(self, game):
        """Perform melee or weapon attack"""
        if self.attack_cooldown > 0:
            return

        self.attacking = True
        self.attack_timer = 0.3
        self.attack_cooldown = 0.5

        # Calculate attack direction
        dx, dy = self.facing
        attack_x = self.x + dx * MELEE_RANGE
        attack_y = self.y + dy * MELEE_RANGE

        # Check for enemies in range
        damage = MELEE_DAMAGE
        attack_range = MELEE_RANGE

        if self.equipped_weapon:
            weapon_type = self.equipped_weapon.get('weapon_type', 'melee')
            if weapon_type == 'pistol':
                # Check ammo
                ammo = self.inventory.get_ammo_count('pistol')
                if ammo > 0:
                    self.inventory.use_ammo('pistol', 1)
                    damage = PISTOL_DAMAGE
                    attack_range = PISTOL_RANGE
                else:
                    # Click - no ammo
                    return

        # Hit detection
        for enemy in game.entities:
            if hasattr(enemy, 'take_damage'):
                dist = math.sqrt((enemy.x - attack_x) ** 2 + (enemy.y - attack_y) ** 2)
                if dist < attack_range:
                    enemy.take_damage(damage)
                    game.effects.trigger_damage_flash()
                    game.particles.emit(enemy.x, enemy.y, "blood", 5)
                    break

    def take_damage(self, amount, source=None):
        """Take damage from enemies or environment"""
        if self.damage_immunity_timer > 0:
            return

        self.health -= amount
        self.damage_immunity_timer = 0.5

        # Sanity hit from taking damage
        self.sanity -= amount * 0.2

        if self.health <= 0:
            self.health = 0
            # Death handled in update

    def heal(self, amount):
        """Restore health"""
        self.health = min(self.max_health, self.health + amount)

    def restore_sanity(self, amount):
        """Restore sanity"""
        self.sanity = min(self.max_sanity, self.sanity + amount)

    def warm_up(self, amount):
        """Restore warmth"""
        self.warmth = min(self.max_warmth, self.warmth + amount)

    def add_discovery(self, flag):
        """Add a narrative discovery flag"""
        self.discovered_flags.add(flag)

    def has_discovery(self, flag):
        """Check if player has made a discovery"""
        return flag in self.discovered_flags

    def get_direction_name(self):
        """Get current facing direction as string"""
        if self.facing == Direction.UP:
            return 'up'
        elif self.facing == Direction.DOWN:
            return 'down'
        elif self.facing == Direction.LEFT:
            return 'left'
        elif self.facing == Direction.RIGHT:
            return 'right'
        return 'down'

    def render(self, surface, camera):
        """Render player sprite"""
        direction = self.get_direction_name()
        sprites = self.sprites.get(direction, self.sprites['idle'])
        frame = self.animation_frame % len(sprites)
        sprite = sprites[frame]

        pos = camera.apply((self.x - self.width // 2, self.y - self.height // 2))

        # Damage flash
        if self.damage_immunity_timer > 0 and int(self.damage_immunity_timer * 10) % 2:
            tinted = sprite.copy()
            tinted.fill((255, 100, 100), special_flags=pygame.BLEND_MULT)
            surface.blit(tinted, pos)
        else:
            surface.blit(sprite, pos)

        # Attack visualization
        if self.attacking:
            dx, dy = self.facing
            attack_x = self.x + dx * 10
            attack_y = self.y + dy * 10
            attack_pos = camera.apply((attack_x, attack_y))

            # Simple attack arc
            pygame.draw.circle(surface, Colors.STERILE_WHITE, attack_pos, 4, 1)
