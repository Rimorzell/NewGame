"""
Frozen Signal - Entity System
Base entity class and game objects
"""

import pygame
import math
import random
from .constants import (
    Colors, TILE_SIZE, Direction, Layer,
    ENEMY_DETECTION_RANGE, ENEMY_ATTACK_RANGE,
    ENEMY_PATROL_SPEED, ENEMY_CHASE_SPEED
)


class Entity:
    """Base class for all game entities"""

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = TILE_SIZE
        self.height = TILE_SIZE
        self.velocity_x = 0
        self.velocity_y = 0
        self.layer = Layer.ENTITIES
        self.active = True
        self.solid = True
        self.sprite = None
        self.animation_frame = 0
        self.animation_timer = 0
        self.facing = Direction.DOWN

    @property
    def rect(self):
        return pygame.Rect(self.x - self.width // 2, self.y - self.height // 2,
                          self.width, self.height)

    @property
    def center(self):
        return (self.x, self.y)

    def update(self, dt, game):
        """Update entity state"""
        self.animation_timer += dt
        if self.animation_timer > 0.1:
            self.animation_timer = 0
            self.animation_frame = (self.animation_frame + 1) % 4

    def render(self, surface, camera):
        """Render entity"""
        if self.sprite:
            pos = camera.apply((self.x - self.width // 2, self.y - self.height // 2))
            surface.blit(self.sprite, pos)
        else:
            # Debug rectangle
            rect = camera.apply_rect(self.rect)
            pygame.draw.rect(surface, Colors.WARNING_RED, rect)

    def distance_to(self, other):
        """Calculate distance to another entity or point"""
        if hasattr(other, 'x') and hasattr(other, 'y'):
            return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)
        else:
            return math.sqrt((self.x - other[0]) ** 2 + (self.y - other[1]) ** 2)

    def angle_to(self, other):
        """Calculate angle to another entity or point"""
        if hasattr(other, 'x') and hasattr(other, 'y'):
            return math.atan2(other.y - self.y, other.x - self.x)
        else:
            return math.atan2(other[1] - self.y, other[0] - self.x)


class Enemy(Entity):
    """Twisted researcher enemy - moves in uncanny, glitchy patterns"""

    def __init__(self, x, y, enemy_type="researcher"):
        super().__init__(x, y)
        self.enemy_type = enemy_type
        self.health = 100
        self.max_health = 100
        self.damage = 15
        self.layer = Layer.ENTITIES

        # AI state
        self.state = "idle"  # idle, patrol, alert, chase, attack, stunned
        self.state_timer = 0
        self.target = None
        self.last_known_pos = None

        # Patrol
        self.patrol_points = []
        self.current_patrol_index = 0
        self.patrol_wait_timer = 0

        # Glitch effect
        self.glitch_timer = 0
        self.glitch_offset_x = 0
        self.glitch_offset_y = 0
        self.glitch_intensity = 0.3

        # Attack cooldown
        self.attack_cooldown = 0

        # Detection
        self.detection_range = ENEMY_DETECTION_RANGE
        self.attack_range = ENEMY_ATTACK_RANGE
        self.fov_angle = math.pi * 0.6  # ~108 degrees

        # Movement
        self.speed = ENEMY_PATROL_SPEED
        self.chase_speed = ENEMY_CHASE_SPEED

        # Create sprite placeholder
        self._create_sprite()

    def _create_sprite(self):
        """Create enemy sprite"""
        self.sprite = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        if self.enemy_type == "researcher":
            # Twisted humanoid shape
            pygame.draw.ellipse(self.sprite, Colors.FROZEN_FLESH,
                              (2, 0, 12, 8))  # Head
            pygame.draw.rect(self.sprite, Colors.DEEP_BLUE,
                           (3, 7, 10, 9))  # Body (lab coat)
            # Glowing eyes
            pygame.draw.circle(self.sprite, Colors.WARNING_RED, (5, 3), 1)
            pygame.draw.circle(self.sprite, Colors.WARNING_RED, (10, 3), 1)
        else:
            # Generic creature
            pygame.draw.ellipse(self.sprite, Colors.ORGANIC_DARK,
                              (0, 0, self.width, self.height))
            pygame.draw.circle(self.sprite, Colors.ALARM_RED,
                             (self.width // 2, self.height // 3), 2)

    def set_patrol_points(self, points):
        """Set patrol route"""
        self.patrol_points = points
        if points:
            self.state = "patrol"

    def update(self, dt, game):
        """Update enemy with glitchy AI"""
        super().update(dt, game)

        # Update glitch effect
        self.glitch_timer += dt
        if random.random() < 0.05:  # Random glitch chance
            self.glitch_offset_x = random.uniform(-3, 3) * self.glitch_intensity
            self.glitch_offset_y = random.uniform(-2, 2) * self.glitch_intensity
        elif self.glitch_timer > 0.1:
            self.glitch_timer = 0
            self.glitch_offset_x *= 0.5
            self.glitch_offset_y *= 0.5

        # Update attack cooldown
        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt

        # State machine
        if self.state == "stunned":
            self.state_timer -= dt
            if self.state_timer <= 0:
                self.state = "alert"
                self.state_timer = 2
        elif self.state == "idle":
            self._update_idle(dt, game)
        elif self.state == "patrol":
            self._update_patrol(dt, game)
        elif self.state == "alert":
            self._update_alert(dt, game)
        elif self.state == "chase":
            self._update_chase(dt, game)
        elif self.state == "attack":
            self._update_attack(dt, game)

        # Check for player detection
        self._check_detection(game)

    def _check_detection(self, game):
        """Check if player is detected"""
        if not game.player or self.state == "stunned":
            return

        distance = self.distance_to(game.player)
        angle_to_player = self.angle_to(game.player)

        # Get facing angle
        facing_angle = math.atan2(self.facing[1], self.facing[0])
        angle_diff = abs(angle_to_player - facing_angle)
        if angle_diff > math.pi:
            angle_diff = 2 * math.pi - angle_diff

        # Detection check
        if distance < self.detection_range:
            if angle_diff < self.fov_angle / 2 or distance < self.attack_range:
                # TODO: Add line of sight check with walls
                if self.state not in ["chase", "attack"]:
                    self.state = "alert"
                    self.state_timer = 1
                self.last_known_pos = (game.player.x, game.player.y)
                self.target = game.player

    def _update_idle(self, dt, game):
        """Idle behavior - occasional twitching"""
        self.state_timer += dt
        if random.random() < 0.01:
            # Random twitch
            self.glitch_offset_x = random.uniform(-5, 5)
            self.glitch_offset_y = random.uniform(-5, 5)

        if self.patrol_points and self.state_timer > 3:
            self.state = "patrol"
            self.state_timer = 0

    def _update_patrol(self, dt, game):
        """Patrol between points with glitchy movement"""
        if not self.patrol_points:
            self.state = "idle"
            return

        target = self.patrol_points[self.current_patrol_index]
        distance = math.sqrt((target[0] - self.x) ** 2 + (target[1] - self.y) ** 2)

        if distance < 5:
            # Reached patrol point
            self.patrol_wait_timer += dt
            if self.patrol_wait_timer > random.uniform(1, 3):
                self.patrol_wait_timer = 0
                self.current_patrol_index = (self.current_patrol_index + 1) % len(self.patrol_points)
        else:
            # Move toward patrol point (with glitchy stuttering)
            if random.random() > 0.1:  # 10% chance to stutter
                angle = math.atan2(target[1] - self.y, target[0] - self.x)
                self.x += math.cos(angle) * self.speed
                self.y += math.sin(angle) * self.speed
                self.facing = (math.cos(angle), math.sin(angle))

    def _update_alert(self, dt, game):
        """Alert state - spotted something"""
        self.state_timer -= dt

        # Turn toward last known position
        if self.last_known_pos:
            angle = self.angle_to(self.last_known_pos)
            self.facing = (math.cos(angle), math.sin(angle))

        if self.state_timer <= 0:
            if self.target and self.distance_to(self.target) < self.detection_range:
                self.state = "chase"
            else:
                self.state = "patrol" if self.patrol_points else "idle"

    def _update_chase(self, dt, game):
        """Chase the player with glitchy movement"""
        if not self.target:
            self.state = "patrol" if self.patrol_points else "idle"
            return

        distance = self.distance_to(self.target)

        if distance < self.attack_range:
            self.state = "attack"
            return

        if distance > self.detection_range * 1.5:
            # Lost target
            self.state = "alert"
            self.state_timer = 2
            return

        # Glitchy chase movement
        angle = self.angle_to(self.target)

        # Add glitch jitter
        if random.random() < 0.15:
            angle += random.uniform(-0.5, 0.5)

        # Teleport glitch (rare)
        if random.random() < 0.02:
            teleport_dist = random.uniform(5, 15)
            self.x += math.cos(angle) * teleport_dist
            self.y += math.sin(angle) * teleport_dist
        else:
            speed = self.chase_speed
            if random.random() < 0.1:
                speed *= random.uniform(0.5, 2)  # Speed glitch

            self.x += math.cos(angle) * speed
            self.y += math.sin(angle) * speed

        self.facing = (math.cos(angle), math.sin(angle))
        self.last_known_pos = (self.target.x, self.target.y)

    def _update_attack(self, dt, game):
        """Attack the player"""
        if not self.target:
            self.state = "idle"
            return

        distance = self.distance_to(self.target)

        if distance > self.attack_range * 1.5:
            self.state = "chase"
            return

        if self.attack_cooldown <= 0:
            # Perform attack
            if hasattr(self.target, 'take_damage'):
                self.target.take_damage(self.damage)
            self.attack_cooldown = 1.0

            # Attack glitch effect
            self.glitch_offset_x = random.uniform(-8, 8)
            self.glitch_offset_y = random.uniform(-8, 8)

    def take_damage(self, amount):
        """Take damage"""
        self.health -= amount
        self.state = "stunned"
        self.state_timer = 0.5

        # Damage glitch
        self.glitch_offset_x = random.uniform(-10, 10)
        self.glitch_offset_y = random.uniform(-10, 10)

        if self.health <= 0:
            self.die()

    def die(self):
        """Enemy death"""
        self.active = False

    def render(self, surface, camera):
        """Render with glitch effect"""
        if not self.active:
            return

        # Apply glitch offset
        render_x = self.x + self.glitch_offset_x
        render_y = self.y + self.glitch_offset_y

        pos = camera.apply((render_x - self.width // 2, render_y - self.height // 2))

        if self.sprite:
            # Occasional sprite corruption effect
            if random.random() < 0.05:
                corrupted = self.sprite.copy()
                # Shift color channels
                pixels = pygame.PixelArray(corrupted)
                pixels[:] = pixels[:] ^ random.randint(0, 0xFF)
                del pixels
                surface.blit(corrupted, pos)
            else:
                surface.blit(self.sprite, pos)

        # Draw detection cone in debug mode (commented out)
        # self._draw_debug(surface, camera)


class InteractableObject(Entity):
    """Object that can be interacted with"""

    def __init__(self, x, y, obj_type, data=None):
        super().__init__(x, y)
        self.obj_type = obj_type
        self.data = data or {}
        self.solid = False
        self.interacted = False
        self.layer = Layer.OBJECTS

        # Interaction settings
        self.interaction_range = 20
        self.requires_item = None
        self.gives_item = None

        self._create_sprite()

    def _create_sprite(self):
        """Create object sprite based on type"""
        self.sprite = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        if self.obj_type == "terminal":
            # CRT terminal
            pygame.draw.rect(self.sprite, Colors.DARK_BLUE, (1, 2, 14, 12))
            pygame.draw.rect(self.sprite, Colors.ICE_BLUE, (2, 3, 12, 8))
            pygame.draw.rect(self.sprite, Colors.DEEP_BLUE, (3, 12, 10, 3))
            # Screen glow
            pygame.draw.rect(self.sprite, Colors.AMBER, (3, 4, 10, 6))

        elif self.obj_type == "door":
            pygame.draw.rect(self.sprite, Colors.RUST, (2, 0, 12, 16))
            pygame.draw.rect(self.sprite, Colors.DARK_BLUE, (3, 1, 10, 14))
            # Handle
            pygame.draw.circle(self.sprite, Colors.AMBER_DARK, (11, 8), 2)
            self.solid = not self.data.get('open', False)

        elif self.obj_type == "locker":
            pygame.draw.rect(self.sprite, Colors.DEEP_BLUE, (2, 0, 12, 16))
            pygame.draw.rect(self.sprite, Colors.ICE_BLUE, (3, 1, 10, 14))
            pygame.draw.rect(self.sprite, Colors.DARK_BLUE, (6, 6, 4, 4))

        elif self.obj_type == "corpse":
            pygame.draw.ellipse(self.sprite, Colors.FROZEN_FLESH, (0, 4, 16, 10))
            pygame.draw.ellipse(self.sprite, Colors.DEEP_BLUE, (2, 0, 8, 8))
            self.solid = False

        elif self.obj_type == "note":
            pygame.draw.rect(self.sprite, Colors.STERILE_WHITE, (4, 4, 8, 10))
            # Text lines
            for i in range(3):
                pygame.draw.line(self.sprite, Colors.DARK_BLUE,
                               (5, 6 + i * 3), (11, 6 + i * 3))
            self.solid = False

        elif self.obj_type == "save_point":
            # Tape recorder
            pygame.draw.rect(self.sprite, Colors.DARK_BLUE, (1, 4, 14, 10))
            pygame.draw.circle(self.sprite, Colors.RUST, (5, 9), 3)
            pygame.draw.circle(self.sprite, Colors.RUST, (11, 9), 3)
            pygame.draw.rect(self.sprite, Colors.AMBER, (6, 5, 4, 2))
            self.solid = False

        elif self.obj_type == "item_pickup":
            pygame.draw.rect(self.sprite, Colors.AMBER_LIGHT, (4, 4, 8, 8))
            self.solid = False

        elif self.obj_type == "heater":
            pygame.draw.rect(self.sprite, Colors.RUST, (2, 2, 12, 12))
            # Heat glow
            if self.data.get('active', True):
                pygame.draw.rect(self.sprite, Colors.AMBER, (4, 4, 8, 8))
            self.solid = True

        else:
            pygame.draw.rect(self.sprite, Colors.UI_BORDER, (0, 0, 16, 16))

    def can_interact(self, player):
        """Check if player can interact"""
        if self.interacted and not self.data.get('reusable', False):
            return False

        distance = self.distance_to(player)
        if distance > self.interaction_range:
            return False

        if self.requires_item:
            if not player.inventory.has_item(self.requires_item):
                return False

        return True

    def interact(self, player, game):
        """Handle interaction"""
        if not self.can_interact(player):
            return None

        result = {'type': self.obj_type, 'data': self.data}

        if self.obj_type == "door":
            if self.requires_item:
                if player.inventory.has_item(self.requires_item):
                    self.data['open'] = True
                    self.solid = False
                    self._create_sprite()
                    result['message'] = "Door unlocked."
                else:
                    result['message'] = f"Requires {self.requires_item}."
                    result['blocked'] = True
            else:
                self.data['open'] = not self.data.get('open', False)
                self.solid = not self.data['open']
                self._create_sprite()

        elif self.obj_type == "terminal":
            result['show_terminal'] = True
            result['terminal_data'] = self.data

        elif self.obj_type == "note":
            result['show_document'] = True
            result['document'] = self.data.get('content', "The text is illegible.")
            self.interacted = True

        elif self.obj_type == "item_pickup":
            if player.inventory.add_item(self.data.get('item')):
                self.active = False
                result['message'] = f"Picked up {self.data.get('item', {}).get('name', 'item')}."
            else:
                result['message'] = "Inventory full."
                result['blocked'] = True

        elif self.obj_type == "save_point":
            result['save_game'] = True
            result['message'] = "Progress saved."

        elif self.obj_type == "locker":
            if not self.interacted:
                if self.gives_item:
                    if player.inventory.add_item(self.gives_item):
                        result['message'] = f"Found {self.gives_item.get('name', 'item')}."
                        self.interacted = True
                    else:
                        result['message'] = "Inventory full."
                        result['blocked'] = True
                else:
                    result['message'] = "Empty."
                    self.interacted = True

        elif self.obj_type == "heater":
            if self.data.get('active', True):
                player.warmth = min(player.max_warmth, player.warmth + 30)
                result['message'] = "The warmth is comforting."

        elif self.obj_type == "corpse":
            if not self.interacted:
                if self.gives_item:
                    if player.inventory.add_item(self.gives_item):
                        result['message'] = f"Found {self.gives_item.get('name', 'item')} on the body."
                        self.interacted = True
                    else:
                        result['message'] = "Inventory full."
                        result['blocked'] = True
                else:
                    result['message'] = self.data.get('examine_text',
                        "A frozen corpse. They died in terror.")
                    self.interacted = True

        return result

    def render(self, surface, camera):
        """Render object with interaction hint"""
        super().render(surface, camera)

        # Draw interaction indicator if nearby player
        # (handled by UI system)
