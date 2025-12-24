"""
Frozen Signal - Tilemap and Level System
Room-based level design with transitions
"""

import pygame
import json
import random
from .constants import Colors, TILE_SIZE, RENDER_WIDTH, RENDER_HEIGHT, RoomType


class Tile:
    """Individual tile data"""

    # Tile type constants
    FLOOR = 0
    WALL = 1
    DOOR = 2
    PIT = 3
    WATER = 4
    ICE = 5
    GRATE = 6

    def __init__(self, tile_type, variant=0):
        self.tile_type = tile_type
        self.variant = variant
        self.solid = tile_type == self.WALL
        self.blocks_sight = tile_type == self.WALL

    @property
    def walkable(self):
        return self.tile_type not in [self.WALL, self.PIT, self.WATER]


class TileRenderer:
    """Renders tiles with the cold aesthetic"""

    def __init__(self):
        self.tile_cache = {}
        self._generate_tiles()

    def _generate_tiles(self):
        """Generate all tile sprites"""
        # Floor tiles
        for variant in range(4):
            self._create_floor_tile(variant)

        # Wall tiles
        for variant in range(16):  # 16 autotile variants
            self._create_wall_tile(variant)

        # Special tiles
        self._create_door_tile()
        self._create_ice_tile()
        self._create_grate_tile()

    def _create_floor_tile(self, variant):
        """Create floor tile variants"""
        surface = pygame.Surface((TILE_SIZE, TILE_SIZE))
        surface.fill(Colors.DARK_BLUE)

        # Add subtle variation
        if variant == 0:
            # Clean floor
            pass
        elif variant == 1:
            # Cracked
            pygame.draw.line(surface, Colors.DEEP_BLUE, (3, 3), (12, 10), 1)
        elif variant == 2:
            # Stained
            pygame.draw.circle(surface, Colors.DEEP_BLUE, (8, 8), 4)
        elif variant == 3:
            # Frost
            for _ in range(5):
                x = random.randint(2, 14)
                y = random.randint(2, 14)
                pygame.draw.circle(surface, Colors.ICE_BLUE, (x, y), 1)

        # Grid lines
        pygame.draw.line(surface, Colors.DEEP_BLUE, (0, 0), (TILE_SIZE, 0), 1)
        pygame.draw.line(surface, Colors.DEEP_BLUE, (0, 0), (0, TILE_SIZE), 1)

        self.tile_cache[('floor', variant)] = surface

    def _create_wall_tile(self, variant):
        """Create wall tile with autotiling support"""
        surface = pygame.Surface((TILE_SIZE, TILE_SIZE))
        surface.fill(Colors.DEEP_BLUE)

        # Main wall color
        pygame.draw.rect(surface, Colors.ICE_BLUE, (1, 1, TILE_SIZE - 2, TILE_SIZE - 2))

        # Add depth/shadow
        pygame.draw.line(surface, Colors.FROST, (1, 1), (TILE_SIZE - 2, 1), 1)
        pygame.draw.line(surface, Colors.FROST, (1, 1), (1, TILE_SIZE - 2), 1)
        pygame.draw.line(surface, Colors.DARK_BLUE, (TILE_SIZE - 2, 2), (TILE_SIZE - 2, TILE_SIZE - 2), 1)
        pygame.draw.line(surface, Colors.DARK_BLUE, (2, TILE_SIZE - 2), (TILE_SIZE - 2, TILE_SIZE - 2), 1)

        # Frost detail
        if variant % 4 == 0:
            for _ in range(3):
                x = random.randint(3, 12)
                y = random.randint(3, 12)
                pygame.draw.circle(surface, Colors.FROST, (x, y), 1)

        self.tile_cache[('wall', variant)] = surface

    def _create_door_tile(self):
        """Create door tile"""
        # Closed door
        surface = pygame.Surface((TILE_SIZE, TILE_SIZE))
        surface.fill(Colors.DARK_BLUE)
        pygame.draw.rect(surface, Colors.RUST, (2, 0, 12, TILE_SIZE))
        pygame.draw.rect(surface, Colors.AMBER_DARK, (3, 1, 10, TILE_SIZE - 2))
        pygame.draw.circle(surface, Colors.AMBER, (11, 8), 2)
        self.tile_cache[('door', 0)] = surface

        # Open door
        surface = pygame.Surface((TILE_SIZE, TILE_SIZE))
        surface.fill(Colors.DARK_BLUE)
        pygame.draw.rect(surface, Colors.RUST, (0, 1, 4, TILE_SIZE - 2))
        self.tile_cache[('door', 1)] = surface

    def _create_ice_tile(self):
        """Create slippery ice tile"""
        surface = pygame.Surface((TILE_SIZE, TILE_SIZE))
        surface.fill(Colors.ICE_BLUE)

        # Ice cracks
        pygame.draw.line(surface, Colors.FROST, (2, 4), (14, 12), 1)
        pygame.draw.line(surface, Colors.FROST, (8, 2), (6, 14), 1)

        # Reflection
        pygame.draw.rect(surface, Colors.PURE_WHITE, (4, 3, 3, 2))

        self.tile_cache[('ice', 0)] = surface

    def _create_grate_tile(self):
        """Create metal grate tile"""
        surface = pygame.Surface((TILE_SIZE, TILE_SIZE))
        surface.fill(Colors.BLACK)

        # Grate pattern
        for i in range(0, TILE_SIZE, 4):
            pygame.draw.line(surface, Colors.DEEP_BLUE, (i, 0), (i, TILE_SIZE), 1)
            pygame.draw.line(surface, Colors.DEEP_BLUE, (0, i), (TILE_SIZE, i), 1)

        self.tile_cache[('grate', 0)] = surface

    def get_tile(self, tile_type, variant=0):
        """Get tile surface from cache"""
        if tile_type == Tile.FLOOR:
            key = ('floor', variant % 4)
        elif tile_type == Tile.WALL:
            key = ('wall', variant % 16)
        elif tile_type == Tile.DOOR:
            key = ('door', variant)
        elif tile_type == Tile.ICE:
            key = ('ice', 0)
        elif tile_type == Tile.GRATE:
            key = ('grate', 0)
        else:
            key = ('floor', 0)

        return self.tile_cache.get(key, self.tile_cache[('floor', 0)])


class Room:
    """A single room in the level"""

    def __init__(self, room_id, x, y, width, height, room_type=RoomType.CORRIDOR):
        self.room_id = room_id
        self.x = x  # Grid position
        self.y = y
        self.width = width
        self.height = height
        self.room_type = room_type

        # Tiles (2D array)
        self.tiles = [[Tile(Tile.FLOOR) for _ in range(width)] for _ in range(height)]

        # Room properties
        self.is_heated = True
        self.is_dark = False
        self.ambient_light = 0.4

        # Connected rooms
        self.exits = {}  # direction -> (room_id, spawn_point)

        # Objects and enemies in this room
        self.objects = []
        self.enemies = []
        self.spawn_point = (width // 2 * TILE_SIZE, height // 2 * TILE_SIZE)

    def set_tile(self, x, y, tile_type, variant=0):
        """Set a tile in the room"""
        if 0 <= x < self.width and 0 <= y < self.height:
            self.tiles[y][x] = Tile(tile_type, variant)

    def get_tile(self, x, y):
        """Get tile at position"""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.tiles[y][x]
        return Tile(Tile.WALL)  # Out of bounds = wall

    def add_walls(self):
        """Add walls around room perimeter"""
        for x in range(self.width):
            self.tiles[0][x] = Tile(Tile.WALL, random.randint(0, 15))
            self.tiles[self.height - 1][x] = Tile(Tile.WALL, random.randint(0, 15))
        for y in range(self.height):
            self.tiles[y][0] = Tile(Tile.WALL, random.randint(0, 15))
            self.tiles[y][self.width - 1] = Tile(Tile.WALL, random.randint(0, 15))

    def add_exit(self, direction, target_room_id, spawn_x, spawn_y):
        """Add exit to another room"""
        self.exits[direction] = (target_room_id, (spawn_x, spawn_y))

    def get_world_pos(self, local_x, local_y):
        """Convert room-local position to world position"""
        return (
            self.x * TILE_SIZE + local_x,
            self.y * TILE_SIZE + local_y
        )

    def check_collision(self, rect):
        """Check collision with solid tiles"""
        # Convert rect to tile coordinates
        left = max(0, int(rect.left // TILE_SIZE))
        right = min(self.width - 1, int(rect.right // TILE_SIZE))
        top = max(0, int(rect.top // TILE_SIZE))
        bottom = min(self.height - 1, int(rect.bottom // TILE_SIZE))

        for y in range(top, bottom + 1):
            for x in range(left, right + 1):
                tile = self.get_tile(x, y)
                if tile.solid:
                    tile_rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE,
                                           TILE_SIZE, TILE_SIZE)
                    if rect.colliderect(tile_rect):
                        return True
        return False


class Level:
    """Complete level with multiple rooms"""

    def __init__(self):
        self.rooms = {}
        self.current_room = None
        self.current_room_id = None
        self.tile_renderer = TileRenderer()

        # Level-wide properties
        self.name = "Unknown"
        self.ambient_cold = False

        # Rendered surface cache
        self.rendered_room = None
        self.needs_redraw = True

    def add_room(self, room):
        """Add a room to the level"""
        self.rooms[room.room_id] = room

    def set_current_room(self, room_id):
        """Change to a different room"""
        if room_id in self.rooms:
            self.current_room_id = room_id
            self.current_room = self.rooms[room_id]
            self.needs_redraw = True
            return True
        return False

    def check_collision(self, rect):
        """Check collision in current room"""
        if not self.current_room:
            return False

        # Check tile collision
        if self.current_room.check_collision(rect):
            return True

        # Check object collision
        for obj in self.current_room.objects:
            if obj.solid and obj.active:
                if rect.colliderect(obj.rect):
                    return True

        return False

    def get_tile_at(self, x, y):
        """Get tile at world position"""
        if not self.current_room:
            return Tile(Tile.WALL)

        tile_x = int(x // TILE_SIZE)
        tile_y = int(y // TILE_SIZE)
        return self.current_room.get_tile(tile_x, tile_y)

    def check_room_transition(self, player):
        """Check if player should transition to another room"""
        if not self.current_room:
            return None

        room = self.current_room
        px, py = player.x, player.y

        # Check exits
        for direction, (target_room, spawn) in room.exits.items():
            if direction == 'north' and py < TILE_SIZE:
                return (target_room, spawn)
            elif direction == 'south' and py > (room.height - 1) * TILE_SIZE:
                return (target_room, spawn)
            elif direction == 'west' and px < TILE_SIZE:
                return (target_room, spawn)
            elif direction == 'east' and px > (room.width - 1) * TILE_SIZE:
                return (target_room, spawn)

        return None

    def render(self, surface, camera):
        """Render current room"""
        if not self.current_room:
            return

        room = self.current_room
        visible = camera.get_visible_rect()

        # Calculate visible tile range
        start_x = max(0, int(visible.left // TILE_SIZE))
        end_x = min(room.width, int(visible.right // TILE_SIZE) + 1)
        start_y = max(0, int(visible.top // TILE_SIZE))
        end_y = min(room.height, int(visible.bottom // TILE_SIZE) + 1)

        # Render visible tiles
        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                tile = room.tiles[y][x]
                tile_surface = self.tile_renderer.get_tile(tile.tile_type, tile.variant)

                world_x = x * TILE_SIZE
                world_y = y * TILE_SIZE
                screen_pos = camera.apply((world_x, world_y))

                surface.blit(tile_surface, screen_pos)

    def get_spawn_point(self):
        """Get spawn point for current room"""
        if self.current_room:
            return self.current_room.spawn_point
        return (TILE_SIZE * 5, TILE_SIZE * 5)


def create_outpost_erebus():
    """Create the main game level - Outpost Erebus"""
    level = Level()
    level.name = "Outpost Erebus"
    level.ambient_cold = True

    # Create rooms

    # Room 1: Starting Area - Crew Quarters
    quarters = Room("quarters", 0, 0, 20, 15, RoomType.QUARTERS)
    quarters.add_walls()
    quarters.spawn_point = (TILE_SIZE * 10, TILE_SIZE * 8)
    quarters.is_heated = True

    # Add interior walls and furniture representations
    for x in range(5, 8):
        quarters.set_tile(x, 5, Tile.WALL)
    for x in range(12, 15):
        quarters.set_tile(x, 5, Tile.WALL)

    # Add some floor variation
    for _ in range(15):
        x = random.randint(2, 17)
        y = random.randint(2, 12)
        quarters.set_tile(x, y, Tile.FLOOR, random.randint(1, 3))

    quarters.add_exit('east', 'corridor_1', TILE_SIZE * 2, TILE_SIZE * 7)
    level.add_room(quarters)

    # Room 2: Main Corridor
    corridor1 = Room("corridor_1", 20, 0, 8, 20, RoomType.CORRIDOR)
    corridor1.add_walls()
    corridor1.spawn_point = (TILE_SIZE * 4, TILE_SIZE * 10)
    corridor1.is_heated = False

    # Ice patches in corridor
    for _ in range(5):
        x = random.randint(2, 5)
        y = random.randint(3, 16)
        corridor1.set_tile(x, y, Tile.ICE)

    corridor1.add_exit('west', 'quarters', TILE_SIZE * 17, TILE_SIZE * 8)
    corridor1.add_exit('east', 'lab_1', TILE_SIZE * 2, TILE_SIZE * 7)
    corridor1.add_exit('south', 'storage', TILE_SIZE * 4, TILE_SIZE * 2)
    level.add_room(corridor1)

    # Room 3: Laboratory
    lab1 = Room("lab_1", 28, 0, 18, 14, RoomType.LAB)
    lab1.add_walls()
    lab1.spawn_point = (TILE_SIZE * 9, TILE_SIZE * 7)
    lab1.is_heated = True

    # Lab benches (walls)
    for x in range(4, 8):
        lab1.set_tile(x, 4, Tile.WALL)
        lab1.set_tile(x, 9, Tile.WALL)
    for x in range(10, 14):
        lab1.set_tile(x, 4, Tile.WALL)
        lab1.set_tile(x, 9, Tile.WALL)

    # Grate floor section
    for x in range(7, 11):
        for y in range(6, 8):
            lab1.set_tile(x, y, Tile.GRATE)

    lab1.add_exit('west', 'corridor_1', TILE_SIZE * 5, TILE_SIZE * 10)
    lab1.add_exit('south', 'reactor', TILE_SIZE * 9, TILE_SIZE * 2)
    level.add_room(lab1)

    # Room 4: Storage
    storage = Room("storage", 20, 20, 12, 10, RoomType.STORAGE)
    storage.add_walls()
    storage.spawn_point = (TILE_SIZE * 6, TILE_SIZE * 5)
    storage.is_heated = False

    # Shelf walls
    for y in range(3, 7):
        storage.set_tile(3, y, Tile.WALL)
        storage.set_tile(8, y, Tile.WALL)

    storage.add_exit('north', 'corridor_1', TILE_SIZE * 4, TILE_SIZE * 17)
    level.add_room(storage)

    # Room 5: Reactor Room
    reactor = Room("reactor", 28, 14, 16, 12, RoomType.REACTOR)
    reactor.add_walls()
    reactor.spawn_point = (TILE_SIZE * 8, TILE_SIZE * 6)
    reactor.is_heated = True
    reactor.is_dark = True
    reactor.ambient_light = 0.2

    # Reactor core (impassable center)
    for x in range(6, 10):
        for y in range(4, 8):
            reactor.set_tile(x, y, Tile.WALL)

    # Grate around reactor
    for x in range(5, 11):
        reactor.set_tile(x, 3, Tile.GRATE)
        reactor.set_tile(x, 8, Tile.GRATE)
    for y in range(4, 8):
        reactor.set_tile(5, y, Tile.GRATE)
        reactor.set_tile(10, y, Tile.GRATE)

    reactor.add_exit('north', 'lab_1', TILE_SIZE * 9, TILE_SIZE * 11)
    reactor.add_exit('south', 'deep_excavation', TILE_SIZE * 8, TILE_SIZE * 2)
    level.add_room(reactor)

    # Room 6: Communications
    comms = Room("communications", 0, 15, 15, 12, RoomType.COMMUNICATIONS)
    comms.add_walls()
    comms.spawn_point = (TILE_SIZE * 7, TILE_SIZE * 6)
    comms.is_heated = False

    # Equipment banks
    for x in range(3, 6):
        comms.set_tile(x, 3, Tile.WALL)
    for x in range(9, 12):
        comms.set_tile(x, 3, Tile.WALL)

    comms.add_exit('east', 'storage', TILE_SIZE * 2, TILE_SIZE * 5)
    level.add_room(comms)

    # Room 7: Deep Excavation - Final Area
    deep = Room("deep_excavation", 28, 26, 20, 16, RoomType.DEEP_EXCAVATION)
    deep.add_walls()
    deep.spawn_point = (TILE_SIZE * 10, TILE_SIZE * 4)
    deep.is_heated = False
    deep.is_dark = True
    deep.ambient_light = 0.1

    # Ice everywhere
    for y in range(2, 14):
        for x in range(2, 18):
            if random.random() < 0.4:
                deep.set_tile(x, y, Tile.ICE)
            else:
                deep.set_tile(x, y, Tile.FLOOR, 3)  # Frost variant

    # Central excavation pit
    for x in range(8, 12):
        for y in range(8, 12):
            deep.set_tile(x, y, Tile.PIT)

    # The Signal - represented as a special tile
    deep.set_tile(10, 10, Tile.GRATE)  # Placeholder for the signal source

    deep.add_exit('north', 'reactor', TILE_SIZE * 8, TILE_SIZE * 9)
    level.add_room(deep)

    # Set starting room
    level.set_current_room("quarters")

    return level
